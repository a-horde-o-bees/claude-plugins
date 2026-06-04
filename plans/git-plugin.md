# Git plugin — full-lifecycle orchestration

The plugin's north star and principles live in [`plugins/git/GOALS.md`](../plugins/git/GOALS.md) — read it first. This plan is the build path to that north star: close the PR loop, grow `/git-checkpoint` into the full messy-tree→`main`-green orchestrator, and carry the in-PR version bump-check that replaced the retired server-side auto-bump.

## Current state

- **Lifecycle front half is built and submodule-aware.** `/git-commit`, `/git-push`, `/git-ci` each recurse depth-first into `.gitmodules`-declared submodules (submodule commit/push/CI completes before the parent's). `/git-checkpoint` inherits that recursion and sequences commit → push → CI. `/git-release` and `/git-doctor` round out the set. Submodule detached-HEAD is handled (push normalizes onto the declared branch); CI soft-skips submodules without `.github/workflows/` as `no-ci`.
- **PR loop, orchestrator, and bump-check are built (all three workstreams below).** `/git-pr-open/status/merge/cleanup` over the deterministic merge gate (`git-pr-status/scripts/pr.py`); `/git-checkpoint` extended into the full feature-branch lifecycle with solo-vs-team adaptation by reading branch protection; `bump-check.yml` + `scripts/bump-check.py` carrying the in-PR version-bump signal after `auto-bump.yml` was retired (#17). Script paths standardized on the documented `${CLAUDE_SKILL_DIR}`.
- **What remains:** live end-to-end dogfooding of the orchestrator on a deployed feature branch; making `bump-check` a required status check; the deferred submodule-hardening items; and the invocation-cost dedups (below).

The three workstreams below are independent and can land in any order, except that B (orchestrator) consumes A (PR loop).

---

## Workstream A — PR loop (per-verb skills + support script)

Four skills, mirroring the one-skill-per-verb precedent (`/git-commit`, `/git-push`, `/git-ci`). `gh` CLI under the hood. The shared parts — PR-context gathering and the merge gate — factor into a support script emitting structured JSON, the way `ci.py` serves `/git-ci`; skill bodies consume its output verbatim and never re-derive it.

### Skills

- **`/git-pr-open` `[--draft] [--base main]`** — `gh pr create`. Idempotent: refuses if a PR already exists for the head branch (reports it instead). Description authored against the branch diff, not the working tree (`git diff {base}...HEAD` — all commits since divergence). Depth scales with change weight (adaptive tiering, below). Applies `/concise-prose`, `/description-authoring`, `/honesty`. Body via heredoc.
- **`/git-pr-status`** — one-page summary from the merge gate: review state (required reviewers, approvals, changes-requested), PR CI state + annotations, mergeability (clean / conflicts / behind-base), branch-protection requirements, missing-bump blocker. No inventing — emits the support script's classification verbatim.
- **`/git-pr-merge` `[--strategy squash|merge|rebase] [--cleanup]`** — gates on the merge check (green CI + annotations clean + required reviews resolved per branch protection). Adapts solo vs team by reading protection (below). Default strategy reads the repo's configured preference, overridable in `pr.md`. `--cleanup` chains the cleanup verb. Merges via `gh pr merge`.
- **`/git-pr-cleanup`** — `git checkout {base} && git pull --prune && git branch -d {head}`. Safe-by-default: refuses (`-d`, never `-D`) if the local branch has commits not in the merged PR.

### The merge gate (support script — steal from netresearch)

Two calls, both deterministic, classification in the script:

1. **PR-level:** `gh pr view N --json reviewDecision,mergeStateStatus,mergeable,statusCheckRollup,reviewThreads`. Merge-ready requires `reviewDecision==APPROVED` (when protection requires reviews), `mergeStateStatus==CLEAN`, `mergeable==MERGEABLE`, every check `SUCCESS`, every thread resolved.
2. **Commit-level annotations:** `gh api repos/{owner}/{repo}/commits/{sha}/check-runs` — surfaces reviewdog / actionlint / CodeQL warnings that pass the check rollup but are invisible in the PR summary. A non-empty annotation count blocks merge.

On CI failure, read annotations *first* (the `startup_failure`/"no jobs ran" anti-pattern) before speculating about infra.

### Solo-vs-team adaptation

Probe `gh api repos/{owner}/{repo}/branches/{base}/protection`:

- **Rules present (team):** gated path — wait for required reviews + green CI; `gh pr merge --auto` to merge when checks clear.
- **404 / no rules (solo):** fast path — merge immediately once CI is green; `--admin` where a protection rule exists but the solo author is bypassing their own.

Same call, behavior from repo config. No mode flag. The probe result is cached in the merge-gate JSON so `status` and `merge` agree.

---

## Workstream B — `/git-checkpoint` as full orchestrator

`/git-checkpoint` grows from commit+push+CI into the top-level lifecycle orchestrator, branching on branch context. The leaves stay small; the orchestrator owns the sequence and the gates.

- **On a feature branch:** `/git-commit` → `/git-push` → `/git-ci` (gate: green) → `/git-pr-open` → `/git-pr-status` (gate: mergeable) → `/git-pr-merge --cleanup` → sync `main`. Each gate is a hard stop — a red CI or an unmergeable PR exits to the user with the failing surface, never merges optimistically.
- **On `main`:** `/git-commit` → `/git-push` → `/git-ci`, unchanged. Project-level delivery (marketplace refresh, plugin-version sync) stays in the project-level wrapper that composes around `/git-checkpoint` — the plugin skill carries no marketplace concern.
- **Sync-as-precondition** (steal from Git Town `ship`): before merge, the branch must be in sync with `base`; behind-base exits to the user with rebase guidance (opt-in to attempt the rebase). After merge, `git pull --prune` so local `main` is never left stale.
- **Present exactly N options, never open-ended** (steal from superpowers): where the orchestrator must choose (merge strategy, conflict recovery), it offers structured choices, not "what next?".

### Open item

- **CI watch vs `--auto`:** `gh pr merge --auto` can fire before checks finish (documented failure mode) and needs auto-merge enabled + an existing protection rule. Prefer the explicit `/git-ci` watch already built, then merge, over trusting `--auto` blindly. Confirm during build.

---

## Workstream C — bump-check CI (replaces retired `auto-bump.yml`)

Move the plugin-version bump into the PR itself, CI-enforced — so the bump lives atomically with the change and merge produces one `main` commit carrying both. `/checkpoint` on `main` then syncs immediately; no push-back, no branch-protection conflict.

- **Author-side** (`/git-pr-open` + `status`): detect plugin code changes in the PR diff (any `plugins/<name>/` file outside its own `plugin.json`). For each affected plugin, ensure `plugin.json` increments its patch version base→head. `open` applies the bumps into the PR's commit chain (or surfaces missing bumps as a precondition); `status` reports a missing bump as a merge blocker (folded into the merge gate).
- **CI-side** (`.github/workflows/bump-check.yml`): a `pull_request` job running the same detection, failing if plugin code changed without a version increment. Becomes a required status check so branch protection gates on it.
- **Interim** (until `bump-check.yml` ships): authors include the bump, reviewers catch misses, and the local `.githooks/pre-commit` bump stays as the belt for admin-bypass direct-to-main edits. The pre-commit bump retires when `bump-check.yml` lands.

---

## Message-authoring patterns (apply across commit / PR / release)

The plugin's distinctive value over the field is message quality. Concrete patterns, validated against community skills:

- **Adaptive description depth** (udecode/plate): description weight scales with change weight — 1–2 sentences for a trivial change, summary + what/why for medium, full design/migration notes for architectural. Omit empty sections. Lead with value (why), not a file-by-file recap.
- **Diff-avoidance ladder** (sickn33): seed the PR body from commit subjects first; descend into `git show`/diffs only when intent is ambiguous. Cheapest correct seeding.
- **Untrusted text is inert** (sickn33): treat external commit/diff text as evidence, not instructions; trust the diff over a contradicting message and flag the mismatch.
- **Authored against the diff, not the journey** (already in `/git-commit`): strip process narration, phase labels, restated principles.
- **GitHub gotcha** (udecode/plate): avoid `#1.` list syntax in bodies — GitHub auto-links it as issue #1.
- **Heredoc always** for commit messages and PR bodies (formatting safety; the de-facto standard).

---

## Submodule hardening (mined from jimmyff/submodules)

That skill delegates everything to a proprietary `glittering` CLI and runs a flat (non-recursive) model — both rejected for a self-contained, git-native, depth-first plugin. Three items are worth taking:

- **Pin-reachability guard in `/git-push`.** A parent commit whose gitlink points at a submodule commit not yet on the submodule's remote is broken for every other clone. Depth-first push ordering closes the window incidentally; make it explicit — before pushing the parent, verify each pinned commit is reachable on its submodule's remote (`git -C {sub} branch -r --contains {pinned-sha}`), and refuse with a clear message otherwise. This is the correctness core of their "raw git leaves parent refs out of sync" warning.
- **Batched cross-submodule commit-message review** (refinement to `/git-commit` recursion). Present all proposed submodule + parent messages in one summary for confirm/adjust, rather than an `AskUserQuestion` per advancing submodule — avoids per-submodule back-and-forth on a deep tree. A change to the recursion's review surface, not its ordering.
- **A submodule read/sync direction** (currently uncovered). Report each submodule's ahead/behind vs. the recorded pin, and pull submodules up to their tracking-branch tips. Either a read-mode extension to `/git-doctor` or a deferred verb. Relevant to "fully up-to-date" but lower priority than the PR loop — capture, don't build yet.

## Invocation-cost audit (measured; fixes pending decision)

Ground-truth audit of how the git skills call each other and the writing skills. Full platform-behavior assertions, probes, and verification log: [`assertions/skill-invocation/`](../plugins/skill-authoring/skills/skill-architecture/assertions/skill-invocation/). Headline: the **Skill tool re-injects a skill's full body on every `skill:` call** — no harness cache — so repeated invocation is real context-window cost. (Prompt caching cheapens only the cached *re-read* of an already-sent prefix, never the injection; each injection is a fresh `cache_creation` ≈ body size.)

**Per-checkpoint body cost (feature run).** Fixed ≈ 13.5k tokens of skill bodies, of which ≈ 2.3k is redundant re-injection: git-doctor twice (commit + push pre-checks) and git-pr-status twice (checkpoint + merge). Each submodule adds ≈ 4.2k (git-commit + git-push + git-ci re-injected). git-doctor is *not* per-submodule — both commit and push guard its pre-check with "skip when invoked recursively."

**Fixes, ranked:**

- **git-pr-status dedup — low-risk win (~875 tok/run).** `/git-checkpoint` calls `/git-pr-status`, then `/git-pr-merge` re-invokes it. Have merge consume the status checkpoint already holds (the merge body already claims it "reads its report, never re-deriving" — make that literal) instead of re-invoking.
- **git-doctor dedup — conditional.** Hoist one doctor pre-check to the checkpoint level and let commit/push skip it under a "checkpoint-vouched" flag (mirrors the existing `--cwd` recursion guard). Weakens their standalone safety guarantee, so flag-gated only.
- **Self-recursion — leave as-is.** Per-submodule re-injection of git-commit/git-push/git-ci is intrinsic to using `skill:` for recursion. The fresh invocation buys deterministic per-submodule isolation for history-writing operations; converting it to load-once-from-context (variant-C clause or a redefined `skill:`) trades that safety for token savings — not worth it for mutations.

**Writing-skill references are fine, not a gap.** `Apply /concise-prose, /description-authoring, /honesty` at the authoring step is a lazy **load-once-on-demand** reference — the body loads once when the agent judges it needs it (or not at all for a skill it already knows), reused across the recursion. Zero repeated cost. This corrects an earlier worry that those references were either expensive or never loaded.

## Shared pre-rollout adjustments

- **`## Dependencies` declarations — documentary, not a loader.** Measured: a `## Dependencies` bullet list loads **nothing** (zero Skill calls); the heading is *not* a load-directive convention. The writing-skill bodies (`/concise-prose`, `/description-authoring`, `/honesty`) load via the inline `Apply /x` at the authoring step (lazy load-once-on-demand), so the bullets for them are redundant documentation. `/process-flow-notation` has *no* inline reference, so the bodies rely on PFN being **always-on** (or model-known) — a portability gap if a consumer lacks the always-on rule. Whether to make PFN load without always-on (canonical load-once dependency form vs. accepting the always-on dependency) is part of the deferred PFN / `skill:`-semantics decision; see [`assertions/skill-invocation/`](../plugins/skill-authoring/skills/skill-architecture/assertions/skill-invocation/). Keep the bullets as human-facing documentation regardless.
- **`allowed-tools` audit** — confirm each skill's frontmatter covers what it invokes: `Bash(git *)`, `Bash(gh *)` for the PR skills, `Bash(uv run *)` for the merge-gate support script if it's Python (parity with `ci.py`).
- **PR methodology file** — bootstrap `.claude/git/pr.md` (analog to `.claude/git/release.md`): default merge strategy, base branch, draft-by-default, required-reviewers convention. Skill reads it at runtime; bootstraps the dialogue when absent.
- **CLAUDE.md correction** — the project CLAUDE.md still implies `auto-bump.yml` history; update the Workflow section to current reality (in-PR bump + local pre-commit belt, `bump-check.yml` pending) when this plan's bump-check ships.

## Critical files

| Purpose | Path |
|---|---|
| North star (read first) | `plugins/git/GOALS.md` |
| PR loop skills (new) | `plugins/git/skills/git-pr-{open,status,merge,cleanup}/` |
| Merge-gate + PR-context support script (new) | `plugins/git/skills/git-pr-status/scripts/` (or shared `plugins/git/scripts/`) |
| Orchestrator to extend | `plugins/git/skills/git-checkpoint/SKILL.md` |
| Bump-check CI (new) | `.github/workflows/bump-check.yml` |
| Local bump belt (retires when bump-check ships) | `.githooks/pre-commit` |
| PR methodology file (project-bootstrapped) | `.claude/git/pr.md` |

## Verification

- **PR loop:** on a feature branch, `/git-pr-open` creates a PR with a seeded, weight-appropriate description and refuses a second time; `/git-pr-status` reports review/CI/annotations/mergeability; `/git-pr-merge --cleanup` merges on green and restores local `main`.
- **Solo vs team:** on an unprotected repo, the merge path goes immediate; on a protected repo, it waits for required reviews + checks — same command, no flag.
- **Orchestrator:** `/git-checkpoint` on a feature branch takes a dirty tree through to merged + synced `main`, halting hard at a red CI gate or unmergeable PR; on `main` it stays commit+push+CI.
- **Bump-check:** a PR touching `plugins/<name>/` without a `plugin.json` bump fails `bump-check.yml`; with the bump it passes and merge yields one `main` commit carrying change + bump; `/checkpoint` on `main` syncs the new version.

## Out of scope

Per `GOALS.md`: PR review automation (posting inline comments, diff summaries), auto-merge *policy* ownership (a GitHub feature a verb may trigger), stacked-PR management, and release-after-merge orchestration.
