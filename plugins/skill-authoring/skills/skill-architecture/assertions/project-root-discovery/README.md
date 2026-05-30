# Project-root discovery — method landscape

**The problem.** A skill or script frequently needs the project root — to resolve
config, find sibling files, locate state. There is no single reliable lever:
Claude Code does **not** put `CLAUDE_PROJECT_DIR` in the environment of Bash-tool
subprocesses (it's hook-only), so every method is a tradeoff between requirements,
failure modes, and what it forces downstream users to install or tolerate.

This file is the standalone "project-root discovery" rung of the ladder
([`../README.md`](../README.md)). Rows marked *reasoned* are git/platform knowledge
not yet re-probed with `runner.py`; rows marked *confirmed* have a probe.

## Levers

| Method | Requirements | Limitations / failure mode | Downstream imposition | Status |
|---|---|---|---|---|
| **`git rev-parse --show-toplevel`** | git repo; cwd inside worktree | Errors if no `.git` up-tree. Inside a **submodule** returns the *submodule* root, not the superproject. Drifts with `cd`. | None — one command, no install | reasoned |
| **`git rev-parse --show-superproject-working-tree`** | git submodule | Climbs only **one** level; empty if not a submodule. Nested submodules need a loop. | None | reasoned |
| **Marker walk-up** (`.git`, `CLAUDE.md`, `.claude/`, `pyproject.toml`…) | a chosen marker at root | Ambiguous if marker repeats up-tree; must agree on the marker set; nested projects can mis-resolve | None — but every consumer reimplements it | reasoned |
| **Native `CLAUDE_PROJECT_DIR`** | hook execution context | **Absent in normal Bash-tool subprocesses** — only set inside hooks | None where present; unusable elsewhere | confirmed (hook-only) |
| **Session-hook-populated env var** — SessionStart hook writes root to a file / exports it, always-on | A `SessionStart` hook **and** companion script installed in the project | Every skill needing it must ship the hook+script; stale if root moves mid-session; per-project install | **High** — forces hook+script install on the consumer | reasoned (we shipped a variant; see quarantine) |
| **Entry-wrapper `export CLAUDE_PROJECT_DIR="$(pwd)"`** | all invocations routed through the wrapper | Trusts cwd at entry — wrong if launched from a plugin-cache checkout (landed in `~/.claude`); bypassed by any direct call | Medium — everything must go through the wrapper | reasoned (we shipped `run-plugin.sh`) |
| **MCP cwd-bootstrap** — server treats `Path.cwd()` as root at import | MCP server context (Claude Code contract: cwd = project root) | Valid **only** in MCP subprocesses; silent corruption elsewhere. We lost saved data to a `${CLAUDE_PROJECT_DIR}`-literal path once | Low (scoped to MCP) | reasoned (shipped, verified-in-context) |
| **Block `cd`** (deny `Bash(cd:*)`) so cwd is always root | A permission deny rule (settings/hook) | cwd stays root, but the agent **can't change directory at all** → every command needs explicit path refs; complicates approvals; breaks anything that must run *in* a directory | **High** — reshapes how all Bash commands are written | unverified (explored) |
| **`CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1`** | env var set for the session | Restores cwd to the launch dir *after* each Bash command (neutralizes `cd` carry-over between calls; a `cd` still works within one command). Main-session only — not subagents/background. Doesn't *resolve* root, *pins* cwd to it | None — documented knob | reasoned (community-documented) |
| **SessionStart hook → `$CLAUDE_ENV_FILE`** | a SessionStart hook installed per project | Hook computes the root once and appends `PROJECT_ROOT=…` to `$CLAUDE_ENV_FILE`; Claude Code sources it into every later **Bash-tool** command. NOT MCP/PowerShell/subagents. **Broken on resume** (#52774 — file written, not re-sourced). A plain `export` in the hook does NOT propagate — must write the file | **High** — per-project hook install | **VERIFIED working on fresh session, v2.1.150** (resume case untested) |
| **Transcript `cwd` tail-scan** | session JSONL readable | Returns the **drifted** cwd, not the root — buggy | Medium | quarantined (wrong) |

## The deeper issue: "project root" is ambiguous under submodules

If plugins become git submodules (see `plans/git-plugin-submodule-expansion.md`), a
skill running inside `plugins/<x>/` could legitimately want **either**:

- the **submodule's own root** — `--show-toplevel` gives this; or
- the **superproject / marketplace root** — climb via `--show-superproject-working-tree`.

No command is "the" answer until we decide *which root the caller needs*. That
decision is upstream of picking a method.

## All roots (multi-root projects) — conform, don't circumvent

A tool that must operate across a superproject **and its submodules** (the git skill
fanning out commit/push, the monaco ERP-migration project) needs *every* root. The
tempting move is a filesystem `.git` scan that finds them regardless of git's view —
but that **routes around git instead of conforming to it**. Decision: detect drift
from proper submodule structure and propose a repair, then operate via canonical git.

**Operational path (conforming repo):** canonical git *is* the "how to get" —
`git submodule status --recursive`, `git submodule foreach`,
`git rev-parse --show-superproject-working-tree`. No scanning.

**These commands key entirely off the gitlink** (mode `160000`) in the superproject
index. If the gitlink is absent, *all* of them go blind — even the superproject-climb
from inside a submodule. Verified against monaco and reproduced in a throwaway
(`$CLAUDE_JOB_DIR/repro_repair.sh`): submodules declared in `.gitmodules`, registered
in `.git/config`, gitdir absorbed, checked out on disk — yet `git submodule status
--recursive` returned **empty** and the submodule files were staged as **plain blobs**
in the superproject index.

**Drift check.** Per `gitsubmodules(7)`, a conformant submodule needs **both** a gitlink
(mode `160000`) **and** a `.gitmodules` declaration — either alone is drift. So classify
on three signals: gitlink (`l`), on-disk `.git` (`o`), declared (`d`):

| l | o | d | State | Action |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | conforming | operate via canonical git |
| ✅ | — | ❌ | **orphan-gitlink** (gitlink, no declaration — invisible to `git submodule`) | propose declare-or-remove |
| ✅ | ❌ | ✅ | not-checked-out | `git submodule update --init` |
| ❌ | ✅ | ✅ | **broken-link** (monaco — staged as blobs) | propose repair |
| ❌ | ✅ | ❌ | **undeclared** (on-disk repo, not declared, *not* parent-gitignored) | surface, ask intent |
| ❌ | ✅ | ❌ | **nested-independent** (same, but parent-**gitignored**) | benign — not drift |
| ❌ | ❌ | ✅ | declared-only | repair/init |

**The `agent-os` umbrella case.** When a parent git repo deliberately contains
independent project repos (shared config passed down, projects nested but not
submodules), `git check-ignore` is the disambiguator: a nested repo the parent
**gitignores** is intentionally independent (`nested-independent`, benign), whereas one
that is *not* ignored is a forgotten/broken submodule worth flagging (`undeclared`). From
*inside* a nested project the relationship-bounded climb already stops correctly (never
climbs into the umbrella); the gitignore check fixes the *from-the-umbrella-root* false
positive. Verified against a reproduced umbrella topology.

The filesystem `.git` scan is demoted to a **diagnostic** that feeds this check — never
the operational root list. The reliable detection primitive is git's own:
`git ls-files --stage | grep '^160000'` diffed against `.gitmodules` paths.

**Prior art (researched 2026-05) — are we reinventing?** No, for the parts that exist:
the *repair* (`git rm --cached` + re-add; `absorbgitdirs` for the unabsorbed-gitdir
variant) and the *detection primitive* (`ls-files 160000` vs `.gitmodules`) are standard.
But **no packaged tool does robust all-roots-with-conformance auditing** — every
off-the-shelf option (`forbid-new-submodules`, submodule_checker, `mr`/`gita`,
`submodule foreach`) keys off `.gitmodules` and is blind to orphan-gitlink / undeclared /
blob states, or is a SHA-freshness hook, or a multi-repo runner. The "enumerate every
git root, classify each against `.gitmodules` for conformance" capability is genuinely
unpackaged; the community substitute is a hand-rolled `find . -name .git` + `ls-files`
loop. `git-roots.sh` + `git-doctor` fill that gap.

**Discovery is asymmetric — a fundamental limit, not a bug.** Finding roots *downward*
from the superproject (filesystem scan) is complete: it finds every nested repo
regardless of any recorded relationship. Climbing *upward* from inside a child relies
on git's relationship markers — gitdir resolving under `parent/.git/modules/`, or
`parent/.gitmodules` declaring the path — and is only as reliable as those markers.

- monaco's breakage (missing gitlink) leaves **both** markers intact → upward climb works.
- The climb survives losing *either* marker (declared-but-gitdir-not-absorbed still climbs).
- It fails only when **all** markers are gone (undeclared *and* unabsorbed). That case is
  undiscoverable from below **by information theory**: a nested repo with no recorded
  relationship anywhere is, on disk, identical to an unrelated independent repo. There is
  no signal to invent the relationship from — and inventing one from mere nesting is the
  over-climb bug (climbing into `~/.claude`). Stopping is the only correct behavior.

The orphan in that last case *is* found by scanning **down** from the superproject (flagged
`undeclared`). So: for complete discovery, orient to the superproject and scan down; treat
the upward climb as best-effort, and never assume the topmost reached repo is the outermost.

**Validated repair** (broken-link case, gitdir already absorbed) — scoped to the one
broken path, never project-wide:

```
git rm -r --cached --quiet <path>   # drop blob entries INSIDE this border only (working tree untouched)
git add <path>                       # git stops at the nested .git → one 160000 gitlink
                                     # (emits a benign "adding embedded git repository" warning — not a failure)
git commit -m "repair: <path> as submodule gitlink"
```

After repair the throwaway confirmed `submodule status --recursive` lists it, the
gitlink records the submodule's current HEAD, `--show-superproject-working-tree` climbs
correctly from inside, and `submodule foreach` reaches it. Gotcha: submodule **name ≠
path** is legal (monaco: name `tools/quickbooks-online-mcp-server`, checkout path
`quickbooks-online-mcp-server`) — resolve checkouts by the `.path` field, not the name.

**What's automatic vs. manual.** `git add <path>` automatically refuses to recurse a
nested `.git` and records the gitlink — boundary *detection* is free. But git does
**not** clean up blobs already staged/committed inside the border; that reconciliation
is the explicit `git rm --cached`. So boundary detection is automatic, ownership
reconciliation is not.

**Risk tiers — the gate raises a classified report, it does not auto-refactor.** Check
history (`git ls-tree HEAD <path>`, `git log -- <path>`) because it sets the tier:

| Tier | State | Fix | Disposition |
|---|---|---|---|
| 0 | conforming | none | silent |
| 1 | broken link, **index-only** (monaco — 0 history commits, blobs only staged) | `rm --cached` + `add`, scoped to the path | reversible — propose with file count + exact commands, apply on approval |
| 2 | interior files **committed to history** | history rewrite (filter-repo) → SHA churn, force-push, broken clones | destructive — **never automatic**; surface with heavy warning as a separate, deliberate decision |

Never unstage project-wide; never rewrite history without explicit per-item approval.
This mirrors `git-commit`'s ethos: no `git add -A`, surface before staging, never
force-push or run destructive ops. Intent is also ambiguous (submodule content vs.
deliberate vendoring) — only the caller can decide.

## Tradeoff axes (when choosing)

- **Reliability** — does it ever silently return the wrong dir? (cwd-based and
  transcript-scan can; git-toplevel errors loudly instead, which is safer.)
- **Downstream imposition** — does the consumer have to install a hook/script,
  route through a wrapper, or give up `cd`? Zero-install (`git rev-parse`) wins
  unless a hard requirement forces otherwise.
- **Context independence** — works in Bash subprocess, MCP, hook, headless `-p`?
  None work everywhere; the env var specifically does not reach Bash subprocesses.

## Provisional lean

- **Single root:** `git rev-parse --show-toplevel` with a marker walk-up as the non-git
  fallback — imposes nothing downstream, fails loudly. **Probed (v2.1.150):**
  `CLAUDE_PROJECT_DIR` is `<unset>` in the Bash tool (docs claim it's exported there —
  the docs are wrong for this version; trust the probe). `CLAUDE_CODE_SESSION_ID` *is*
  present, so a session-keyed file is readable from anywhere.
- **Optional session-start cache:** a SessionStart hook can compute the root once and
  expose it via `$CLAUDE_ENV_FILE` (verified working on a fresh session). But this is a
  *cache over detection, not a replacement* — the hook still runs `git-roots.sh` /
  `git rev-parse` to compute the value, so the detection logic must still be correct
  (garbage in → garbage cached, more confidently). Adopt only if per-call re-walk cost
  matters, and guard the resume bug (#52774). Where hard cwd stability is wanted,
  `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1` pins cwd to the launch dir.
- **All roots (multi-root):** run the drift check first; on a conforming repo use
  canonical git (`submodule status --recursive` / `foreach`). Don't trust the
  superproject-climb or `git submodule` until the gitlink is confirmed present —
  repair to conform first (validated above).

Both still need a `runner.py` probe capturing exact outputs before earning a row in
`confirmed-facts.md`.

## Consuming from a skill — the interface

The helper ships as `scripts/git-roots.sh` bundled in each skill that needs it (mechanical,
stateless — a per-skill copy, not a deployed shared artifact). A skill invokes it by
absolute path via the **official `${CLAUDE_SKILL_DIR}` substitution** — the skill's own
folder, resolved regardless of cwd:

```
sh ${CLAUDE_SKILL_DIR}/scripts/git-roots.sh root    # superproject path, one line (answers even under drift)
sh ${CLAUDE_SKILL_DIR}/scripts/git-roots.sh roots   # all operable roots; drift -> exit 1 -> git-doctor
sh ${CLAUDE_SKILL_DIR}/scripts/git-roots.sh self     # the script's own dir (script-side runtime self-location)
```

**`!`-injection on load (Claude-specific).** A SKILL.md `` !`cmd` `` line runs `cmd` once
when the skill loads and replaces the placeholder with its stdout — useful to auto-inject
the project root/conformance status into context without a runtime tool call:
`` Project root: !`sh ${CLAUDE_SKILL_DIR}/scripts/git-roots.sh root` ``. **Probed
(v2.1.150, undocumented by Anthropic):** the `!` command runs in the **session/project
cwd, NOT the skill folder** — so relative `./scripts/…` fails; `${CLAUDE_SKILL_DIR}` *does*
substitute inside `!` lines (both measured). Using git-roots' `self` to fetch the skill
dir is therefore circular — you already used `${CLAUDE_SKILL_DIR}` to locate the script.
Portability caveat: the SKILL.md format is the open Agent Skills standard, but
dynamic-context `!`-injection and `${CLAUDE_SKILL_DIR}` are Claude extensions — don't
assume other agents honor them.

**`${CLAUDE_SKILL_DIR}` is the only documented placeholder for a skill's own folder**
(docs: code.claude.com/docs/en/skills). It is substituted into SKILL.md before the model
runs the command, so the Bash tool receives a concrete absolute path. Pitfalls confirmed:
`<THIS-FILE-DIR>` is **not a real feature** (it only "works" when the model guesses the
path — several of our skills had this latent bug); `${CLAUDE_PLUGIN_ROOT}` is undocumented;
relative paths are unreliable (cwd not guaranteed). So: skills locate *any* bundled sibling
file via `${CLAUDE_SKILL_DIR}/…` — that is the harness-provided answer to "where is my
skill folder," and the helper's `self` mode is only for a script finding its own neighbors
at runtime, not for SKILL.md authoring.

## Quarantined reference

Prior implementations of the hook / wrapper / resolver levers, plus the friction and
decision logs that recorded their failure modes, are staged at
[`../quarantine/project-dir-history/`](../quarantine/project-dir-history/) — mine for
ideas, don't cite.
