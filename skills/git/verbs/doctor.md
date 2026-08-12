# git doctor

The repo-health doctor. The driver's detector scans the problem domains that gate everyday work; each domain's repair process is a section of this file, dispatched only when its domain is flagged — a healthy repo (the common case) pays just the detector, cheap enough to run before any commit or push.

## Variables

- `{verb}` — `ci` runs the CI domain on demand (optionally `audit` | `harden` | `reconcile`); empty runs the pre-flight detector across the always-on domains.

## Rules

- **Detect cheap, repair lazy.** `doctor-detect` is local and fast; a domain's repair process runs only when its domain is flagged.
- **Severity gates the process.** `BLOCKING` (submodule drift — committing through it escalates Tier 1 into Tier 2 history pollution) halts until resolved or deliberately deferred. `ADVISORY` (default-branch, CI) is surfaced, never blocks.
- **Conform, don't circumvent.** Repairs restore canonical git structure; never a workaround. Per-domain risk-tiering and scoping live in the domain sections; the driver's repairs refuse the cases that need a deliberate decision.

## Process

1. `{verb}`: first token of this verb's arguments
2. If `{verb}` is `ci`: Call: [CI domain](#ci-domain) (`{ci-args}`: remainder of this verb's arguments); Exit process — on-demand CI domain
3. `{detect}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py doctor-detect` — bind `{status}`, `{problems}` (each `{domain, severity, detail}`), `{superproject}`, `{submodules}` (the per-path state table, each row carrying its driver-computed `disposition`)
4. If `{status}` is `not-a-repo`: Exit process: not a git repository
5. If `{status}` is `healthy`: Exit process: the ### healthy report
6. For each `{problem}` in `{problems}`, dispatch by `{problem}`.domain:
    - `submodule` → Call: [Submodule domain](#submodule-domain) (`{detect}` is its diagnosis input)
    - `submodule-routing` → Call: [Submodule domain](#submodule-domain) (routing-gap mode — write the missing native key)
    - `default-branch` → Call: [Default-branch domain](#default-branch-domain) (`{detail}`: `{problem}`.detail)
    - `ci` → Call: [CI domain](#ci-domain) (`{ci-args}`: `audit`)
7. Emit the ### result report

## Report

### healthy

```
Repo health: clean — no blocking or advisory problems detected.
```

### result

```
Repo health:
{per domain handled: <domain> (<severity>) — repaired | deferred | advised, with its domain's surface}
Blocking unresolved: {yes — do not commit/push until resolved | none}
Next: {what the caller must decide, or — proceed}
```

## Submodule domain

Diagnoses and repairs submodule conformance so canonical git (`submodule status --recursive`, `foreach`, `--show-superproject-working-tree`) works. Dispatched only when the detector flags submodule drift (BLOCKING) or a routing gap. The driver runs every repair and computes each row's disposition; this domain gets approval and dispatches — the deliberate cases (tier 2, unknown intent) are refused by the driver even if asked.

### Rules

- **Conform, don't circumvent** — repairs restore proper submodule structure (gitlinks) so standard git commands operate; never substitute a filesystem-scan workaround for git's own machinery.
- **Every repair is scoped to one broken path** — the driver's subcommands take explicit paths; never project-wide.
- **The tier boundary is the driver's, enforced mechanically:**
    - *Tier 1 — index-only* (`tier1-repair`: gitlink missing, interior files staged as blobs, **0 commits in history**): reversible. Propose with the state row + what `sub-repair` will do; apply on approval. The driver refuses any path with history.
    - *Tier 2 — history-polluted* (`tier2-surface-only`: interior files committed to superproject history): destructive to fix (history rewrite → SHA churn, force-push, broken clones). **Never automatic.** Surface with a heavy warning as a separate, deliberate decision; there is no driver subcommand for it.
- **Postpone → stop.** If the caller declines a repair, halt — do not proceed to commit. Committing while a submodule is staged-as-blobs is exactly what escalates Tier 1 into Tier 2.
- Submodule **name ≠ path** is legal — the driver resolves by `.gitmodules` `.path`; this domain always passes paths.
- **Routing native keys live in the parent's `.gitmodules`, never in the submodule.** Detection decides routing by default; the four-key vocabulary (`branch`, `update`, `x-integration`, `x-contribute`) is the only override surface, written via `write-native-key` on approval (the driver validates key and value). Never write `.claude/git/*` into a submodule.

### Process

1. `{detect}`: the caller's doctor-detect JSON (re-run `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py doctor-detect` if stale). Bind `{superproject}` and the `{submodules}` state rows (`{state, path, staged, history, disposition}`). Conformance needs BOTH a gitlink AND a `.gitmodules` declaration — `gitsubmodules(7)`; each row's `disposition` is the driver's fixed-rule call:
    - `tier1-repair` — reversible index repair (`sub-repair`)
    - `tier2-surface-only` — destructive fix; surface only
    - `declare-or-drop` — gitlink with no declaration (invisible to `git submodule`); `sub-declare` to conform, or `gitlink-drop` to remove
    - `init` — declared but not checked out (`sub-init`)
    - `ambiguous-intent` — an on-disk repo not in `.gitmodules` and not parent-gitignored; intent unknown (forgotten submodule vs. deliberately vendored code)
    - `skip-benign` — parent-gitignored on-disk repo (umbrella pattern); intentionally not a submodule
    - `surface-anomaly` — doesn't fit a known pattern; report, don't act
2. Emit ### Submodule diagnosis (per-path state + disposition + scope counts)
3. Tier 1 — AskUserQuestion per `tier1-repair` path: approve the scoped repair? Then one batch: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py sub-repair` with one `--path {p}` per approved path — re-borders each as a gitlink and commits the batch (the "adding embedded git repository" warning is the expected outcome)
4. Init — for each `init` path: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py sub-init --path {p}`
5. Ambiguous / declare-or-drop — AskUserQuestion per path: declare + link it as a submodule (`sub-declare --path {p}`, url from its origin), leave as vendored content (no action), drop the orphan gitlink (`gitlink-drop --path {p}`, `declare-or-drop` only), or stop for manual handling. Act only on the chosen option; never guess intent.
6. Tier 2 — present the history-rewrite warning per `tier2-surface-only` path; do NOT act — require a separate explicit instruction
7. Routing native-key gaps (when the detector flagged `submodule-routing`) — for each declared submodule with no `branch =`:
    1. `{current}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py read --cwd {superproject}/{path} -- rev-parse --abbrev-ref HEAD`
    2. If `{current}` is `HEAD` (detached): surface — `{path}` is detached with no declared branch; normalize it onto a branch first (there is no branch to record yet)
    3. Else: AskUserQuestion — record `branch = {current}`? On approval: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py write-native-key --path {path} --key branch --value {current}`
8. Integration override (when a checkpoint routing gap points here — e.g. `edits-to-readonly` — or the user wants a path detection wouldn't pick) — only ever a deliberate override, never to restate what detection already reads:
    1. AskUserQuestion — write `x-integration = <read-only|direct|pr>`? Use it to force a PR on an unprotected branch, pin a writable repo as read-only, or admit a deliberate direct-land; leave unset to let detection decide. On approval: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py write-native-key --path {path} --key x-integration --value {v}`
    2. If the submodule's origin is a fork and the contribution target is ambiguous: AskUserQuestion — `x-contribute = <upstream|origin>`? On approval: the same `write-native-key` with `--key x-contribute`
9. `{verify}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py doctor-detect` — bind the fresh `{status}`
10. Return to caller: ### Submodule result

### Submodule diagnosis

```
Repo: {superproject}
Submodule conformance (every detected boundary, declared or on-disk):
{per-path: <path> — <state> → <disposition> (staged: {staged}, history: {history})}
Tier 1 (reversible index repair): {tier1-list}
Tier 2 (history rewrite — needs deliberate decision): {tier2-list}
Undeclared (intent decision): {undeclared-list}
Uninitialized: {uninit-list}
```

### Submodule result

```
Submodule domain:
Repaired (Tier 1): {repaired-list + commit}
Initialized: {init-list}
Declared / dropped: {declare-drop-list}
Deferred (Tier 2 / postponed): {deferred-list}
Native keys written: {key-list}
Verify: {status healthy = conforming | still drifting — see diagnosis}
Blocking unresolved: {yes — do not commit until resolved | none}
```

## Default-branch domain

Two related advisory findings on the repo's default branch: `origin/HEAD` unset (branch-resolving verbs fall through to their fallback) and a default that isn't `main` (the modern standard the repo silently contradicts). Non-blocking — convenience and conformance, not a safety gate. Each fix is gated on approval and declinable; the repo keeps whatever it has if you decline. The driver runs both fixes.

### Process

1. `{detail}`: the detector's `default-branch` problem detail — it names which finding fired (unset pointer vs non-`main` default) and, for the latter, the current default `{default}`.
2. Set `origin/HEAD` — when the finding is the unset pointer:
    1. AskUserQuestion — set `refs/remotes/origin/HEAD` now? A local, reversible pointer that makes branch resolution work without a network call; the driver resolves the true default from the forge (fallback `main`).
    2. If approved: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py origin-head-set` — bind `{origin_head}` and its `{source}` (forge vs fallback) for the report
3. Rename to the `main` standard — when the finding is `{default}` ≠ `main`:
    1. AskUserQuestion — rename `{default}` to `main` across every remote now? This is the modern standard, not a hard requirement — decline to keep `{default}`. The rename is outward-facing: it changes what new clones check out and touches every remote's forge default.
    2. If declined: surface the finding in the report unchanged — the repo keeps `{default}`, no gloss over the contradiction.
    3. If approved: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py default-branch-rename --old {default}` — the driver runs the canonical order (local rename → publish `main` everywhere → flip each forge default (github via gh, gitlab via glab, local-path remotes directly) → delete `{default}` per remote → repoint HEADs and prune), with progressive output.
    4. If BLOCKED (a remote refused to delete `{default}` — protected there, or an unflippable forge): surface the driver's message verbatim — it names what completed and the manual unprotect → delete → re-protect-`main` path. Protection carry-over is deliberate and manual; never silently drop a default branch's protection.
4. Return to caller:
    - Default branch: `{default}` — `{renamed to main | kept (rename declined) | rename halted (see driver surface)}`
    - `origin/HEAD`: `{set → {origin_head} ({source}) | already set | left unset (verbs fall back)}`
    - Remotes updated: `{from the driver's output | — none}`

## CI domain

The GitHub Actions CI-config domain. Runs on demand (`/git doctor ci [audit|harden|reconcile]`) or when the detector flags workflow files in the change. The driver diagnoses deterministically; this domain emits its findings verbatim, proposes scoped edits, applies only on approval — never rewrites a workflow wholesale. Config hardening, not code review.

### Variables

- `{ci-verb}` — first token of `{ci-args}`: `audit` (default, report-only), `harden` (apply fixes on approval), or `reconcile` (required-check ↔ job-name only).
- `{branch}` — `--branch <name>` for `reconcile`; the driver defaults to the repo default.

### Rules

- **The driver is the source of truth.** `gitflow.py ci-audit` / `ci-reconcile` classify; this domain emits their findings verbatim and proposes fixes from the `fix` hints — never inventing findings or severity.
- **Severity is the driver's call.** `high` — supply-chain / privilege (unpinned actions, broad `GITHUB_TOKEN`); `medium` — robustness (no job timeout); `low` — efficiency (no concurrency on PR-feedback workflows).
- **`audit` and `reconcile` are read-only.** Only `harden` writes, and only after explicit approval of a presented diff. Never edit a workflow not surfaced by the audit.
- **SHA pins come resolved from the driver.** `ci-audit --resolve` resolves each unpinned action's ref to its commit SHA and supplies the exact `pinned_line`; apply that line verbatim — never invent a SHA. A finding without a `pinned_line` (resolution failed) is surfaced, not guessed.
- **Pair pins with an updater.** When proposing SHA pins, recommend (or, on approval, scaffold) `.github/dependabot.yml` with the `github-actions` ecosystem so pins stay current via reviewed PRs.

### Process

1. `{ci-verb}`: first token of `{ci-args}` (default `audit`); `{branch}`: `--branch` value if given
2. If `{ci-verb}` is `reconcile`: Call: [Reconcile](#reconcile); Return to caller
3. `{audit}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py ci-audit` (append ` --resolve` when `{ci-verb}` is `harden` — pre-resolves every SHA pin)
4. Bind from `{audit}` JSON: `{clean}`, `{severity-counts}`, `{results}` (per-file findings, each with check / severity / detail / fix, plus `pinned_line` for resolved pins)
5. `{reconcile}`: Call: [Reconcile](#reconcile) — fold its mismatches in as additional findings (a required check matching no job is a `high`: the PR can never merge)
6. Emit the ### CI audit report grouped by severity
7. If `{ci-verb}` is `audit`: Return to caller — report only
8. If `{ci-verb}` is `harden`:
    1. If `{clean}` AND no reconcile mismatch: Return to caller — already hardened; nothing to fix
    2. For each `{finding}` in `{results}` (high → low): propose the edit — the `pinned_line` for an unpinned action (skip + surface any without one), else the `fix` hint (top-level `permissions: contents: read`, `timeout-minutes`, `concurrency` block)
    3. Present all proposed edits as one batched diff. AskUserQuestion — apply all / select / cancel; never finalize without explicit approval (confirm-shared-intent)
    4. On approval: apply each via Edit
    5. If any SHA pin was applied AND no `.github/dependabot.yml`: offer to scaffold it (github-actions, weekly)
9. Emit the ### CI harden report

### Reconcile

1. `{rc}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py ci-reconcile` (append ` --branch {branch}` when given)
2. Bind: `{protection}`, `{required-contexts}`, `{job-names}`, `{required-without-matching-job}`, `{jobs-not-required}`
3. If `{protection}` is false: Return to caller: no branch protection — nothing to reconcile
4. Return to caller:
    - `{required-without-matching-job}`: required checks that map to no job — these hang as "Expected — waiting" and block every PR (unless an external check supplies them); fix the name or remove from protection
    - `{jobs-not-required}`: jobs that gate nothing until added to protection

### CI audit

```
CI audit: .github/workflows ({workflow-count} workflows)
Status: {clean ? hardened : findings by severity — high {h} / medium {m} / low {l}}
{per finding, grouped high→low: <file> — <check>: <detail>  → <fix>}
Required checks: {reconcile summary — mismatches or "all required checks map to a job"}
Next: `/git doctor ci harden` to apply the fixes (gated on review).
```

### CI harden

```
Applied: {count} fix(es) — {per applied: <file> <check>}
Skipped: {declined or deferred}
Dependabot: {scaffolded | already present | declined}
Next: commit the workflow changes; required-check reconciliation needs branch-protection edits (admin).
```
