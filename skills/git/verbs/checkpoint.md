# git checkpoint

> Bundle the checkpoint for the current branch. Routes every repo — parent and submodules alike — by detection (live git/forge state + parent-owned native `.gitmodules` keys), never a config file. The orchestrator sequences; the verbs own their gates, recursion, and message authoring; the project's only config is augmentations, root-only and optional.

## Dependencies

- `verbs/commit.md`, `verbs/push.md`, `verbs/ci.md` — the commit/push/CI verbs; each recurses depth-first into declared submodules, inherited here for free.
- `verbs/pr-status.md`, `verbs/pr-open.md`, `verbs/pr-merge.md` — the PR loop run for a `pr`-integrated repo. Gating lives in these; this verb only sequences them.
- `scripts/pr.py routes` — the one mechanical detection pass that routes the parent and every declared submodule.
- `.claude/git/checkpoint.md` (optional, root-only) — `## Augmentations` steps; never routing. Absent ⇒ pure detection.

## Variables

- `{branch}` — `--branch <name>`; defaults to current. Explicit `--branch` must match current (the push verb enforces this).
- `{path}` — the parent repo's integration (`pr` | `direct`), read from `pr.py routes` (the `path: "."` entry). Not a config value and not a user choice. `--path <pr|direct>` is **internal only** — the parent passes its decided integration into a recursive submodule run, so a parent `x-integration` override the submodule can't see in its own `.gitmodules` is still honored.
- `{paths}` — optional `--paths <pathspec>...`; scopes the whole checkpoint to those paths. Empty = the whole tree. Passed to `/git commit` and exposed to the pre-land augmentation.
- `{base-mode}` — `--base-mode`: the one explicit override — land directly on the base even when detection says `pr` (the admin/direct-land exception).
- `{auto}` — `--auto`: hands-off. Threaded verbatim to `/git pr-open` and `/git pr-merge`; the verbs own what it bypasses. Checkpoint adds no auto behavior of its own.
- `{feature-branch}` — the topic-derived `<area>/<topic>` branch auto-created when checkpointing a `pr` repo from its base branch.
- `{root}` — the superproject toplevel (`git rev-parse --show-toplevel`), captured so the router returns to it after `cd`-ing into a submodule.
- `{pin-only}` — submodule paths the parent only pins (PR-governed ones it landed; vendored ones). Passed as `--pin-only` to the commit/push verbs.
- `{ledger}` — per-submodule routing outcomes (landed PR + pinned sha / pin-only / direct), surfaced in the report and on a halt.
- `{pre-land}`, `{on-main}` — augmentation steps from the root `checkpoint.md` `## Augmentations`, each empty when there is no file or the step isn't declared.

## Rules

- **Detection is the source of truth.** One `pr.py routes` pass routes the parent and every submodule from live permission / fork / default-branch-protection plus parent-owned native `.gitmodules` keys (`branch`, `update`, `x-integration`, `x-contribute`). There is no `Path:` config and no per-repo routing markdown. `/git doctor` writes the native keys for gaps.
- **The parent's path is detected, not chosen.** A protected default branch → `pr`; unprotected → `direct`. Integration is a repo property, read from the default branch — running a checkpoint from a feature branch still reads the repo as `pr`. `--base-mode` is the sole deliberate exception (direct-land on a `pr` repo, admin).
- **One routing pre-flight; any gap halts.** The pass runs before anything is committed. Any gap — undeterminable permission, an undeclared push branch, edits to a read-only repo — halts up front, parent and submodule alike, with the exact native-key fix (`git config -f .gitmodules …`) or a `/git doctor` pointer. No mid-flight bootstrap, no silent fallback, no proceeding on ambiguity.
- **The parent pins merged shas, never unmerged ones.** A PR-governed submodule whose PR does not land halts the whole checkpoint — the ledger names what already landed (irreversibly) vs. halted, and landed submodules are skipped on re-run. After a submodule lands, checkpoint reconciles its HEAD to origin's merged tip before recording the pin advance.
- **Augmentations are honored, not hardcoded.** The root `checkpoint.md` may declare project steps to run *before the commit* (pre-land — e.g. a version bump) and *after content reaches the base* (on-main — e.g. a delivery sync). This verb runs them at those points and carries none of their content. The file holds augmentations only — never routing — and is optional; absent ⇒ pure detection flow.
- **No optimistic merge.** Merge runs through `/git pr-merge`, whose hard gate (red or pending CI, conflicts, behind-base) exits rather than merging on unknown state. Under `--auto` the merge verb watches in-flight CI to green and merges in the same run; only a hard failure halts.
- **Skip the commit/push portion silently when nothing is pending** — not an error. The PR/merge phase still proceeds on a feature branch.

## Process

1. Resolve branch:
    1. {branch}: bash: `git branch --show-current`
    2. If {branch} is empty (detached HEAD): Exit process — detached HEAD; checkout a branch first
    3. If `--branch` given and ≠ {branch}: Exit process — branch mismatch; re-invoke with `--branch {branch}` or switch branches
    4. {default-branch}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` — fallback `main`

2. Routing pre-flight (detect first; before anything is committed) — one mechanical pass routes the parent and every submodule from live state + native `.gitmodules` keys:
    1. {root}: bash: `git rev-parse --show-toplevel`
    2. {routes}: bash: `python3 ${CLAUDE_SKILL_DIR}/scripts/pr.py routes` (append ` --paths {paths}` when {paths} is set) — each repo's `{path, integration, sync, gaps, branch, perm, protected, has_edits}` plus the combined gap list, all probes run in-process
    3. If {routes}.ok is false: Exit process — routing is ambiguous; resolve every gap, then re-invoke. List each {routes}.gaps entry as `{repo}: {gap} → {fix}`. Run `/git doctor` to write the native keys it can. No mid-flight bootstrap, no guessing — parent and submodule gaps halt the same way
    4. {parent}: the {routes}.repos entry with path == `.`
    5. {path}: `--path` if internally supplied (a recursive submodule run), else {parent}.integration — the detected parent integration
    6. {effective-path}: `direct` if {base-mode}, else {path}
    7. {pin-only}: empty; {ledger}: empty
    8. For each {repo} in {routes}.repos with {repo}.path ≠ `.` (the submodules):
        1. {sub}: {repo}.path
        2. If {repo}.integration is `read-only`: add {sub} to {pin-only}; {ledger} += `{sub}: pin-only (vendored)`; continue
        3. If {repo}.integration is `direct`: {ledger} += `{sub}: direct (verbs push it)`; continue — left to the commit/push verbs' direct recursion
        4. {repo}.integration is `pr`:
            1. {sub-dirty}: bash: `git -C {sub} status --short`
            2. If {sub-dirty} is empty: add {sub} to {pin-only}; {ledger} += `{sub}: pin-only (already landed / no work)`; continue — nothing to land; the parent records its pin (the idempotent re-run path)
            3. {wb}: {repo}.branch. Normalize off detached HEAD: {cur}: bash: `git -C {sub} rev-parse --abbrev-ref HEAD`; if {cur} is `HEAD`: {sha}: bash: `git -C {sub} rev-parse HEAD`; {decl}: bash: `git -C {sub} rev-parse --verify {wb} 2>/dev/null`; if {decl} is empty: bash: `git -C {sub} checkout -b {wb}`; else if {decl} == {sha}: bash: `git -C {sub} checkout {wb}`; else: Exit process — {sub}'s {wb} diverges from its detached HEAD; resolve manually
            4. bash: `cd {sub}` — make the submodule the working directory for the recursive run
            5. {sub-report}: Call: verbs/checkpoint.md --path {repo}.integration + ` --auto` if {auto} — full lifecycle in {sub}, with the parent's decided integration passed in so an `x-integration` override is honored: recurse its own sub-submodules, commit → push → CI → open PR → merge (gated) → cleanup
            6. bash: `cd {root}` — return to the superproject
            7. If {sub-report} did not land the PR (gate halt — pending/red CI, conflicts, unmet reviews): Exit process — submodule {sub}'s PR did not land. Landed this run: {ledger}. Resolve in {sub}, then re-invoke (landed submodules are skipped). The parent is not pinned to an unmerged sha
            8. Reconcile the pin to the merged tip: {default}: bash: `git -C {sub} symbolic-ref --short refs/remotes/origin/HEAD | sed 's@^origin/@@'` (fallback {wb}); bash: `git -C {sub} fetch origin {default}`; {merged}: bash: `git -C {sub} rev-parse origin/{default}`; {head}: bash: `git -C {sub} rev-parse HEAD`; if {head} ≠ {merged}: bash: `git -C {sub} checkout {default}` then `git -C {sub} reset --hard {merged}`
            9. add {sub} to {pin-only}; {ledger} += `{sub}: landed PR, pinned {merged}`

3. Load augmentations (optional, root-only): {config}: `.claude/git/checkpoint.md`. If {config} exists: Read it — bind its `## Augmentations` steps ({pre-land}, {on-main}), each empty if not declared. If absent: both empty — pure detection flow, nothing to bootstrap.
4. Branch under `pr` (auto-create as needed) — when {effective-path} is `pr` AND {branch} == {default-branch}:
    1. {pending}: bash: `git status --short -- {paths}` — pending changes in scope
    2. If {pending} is empty: skip — nothing to branch for; the flow falls through to base-mode (a no-op) or, if a PR is already open for an existing branch, drives it
    3. {feature-branch}: author a kebab-case `<area>/<topic>` name from the in-scope change — {area} the single plugin or directory the scope sits under (else a short domain word), {topic} what the change does. Derive from the diff, not from prompt text.
    4. bash: `git checkout -b {feature-branch}` — carries the working tree onto the new branch
    5. {branch}: {feature-branch} — subsequent steps route to the feature-PR lifecycle

5. Pre-land — if {pre-land}: bash: run it (e.g. the version bump), before committing so CI validates the result. When {paths} is set, scope the augmentation to it so only in-scope plugins bump.
6. Commit + push + CI (every context) — pass `--pin-only {p}` for each {p} in {pin-only} so the verbs skip submodules checkpoint already landed or pins:
    1. {commit-report}: Call: verbs/commit.md {paths} + ` --auto` if {auto} + ` --pin-only {p}` for each {pin-only} — pass `--on-base` when {branch} == {default-branch} so the verb's base guard permits the intentional base commit
    2. {push-report}: Call: verbs/push.md --branch {branch} + ` --pin-only {p}` for each {pin-only}
    3. {ci-report}: Call: verbs/ci.md --branch {branch}

7. Base mode — when {effective-path} is `direct` OR {branch} == {default-branch}:
    1. If {on-main}: bash: run it (content is on the base now — e.g. delivery sync); {sync-report}: its output
    2. Emit the ### base-mode report and stop

8. Feature-PR lifecycle — when {effective-path} is `pr` AND {branch} ≠ {default-branch}:
    1. {pr-status}: Call: verbs/pr-status.md --branch {branch}
    2. If {pr-status} reports no open PR: Call: verbs/pr-open.md + ` --auto` if {auto}
    3. {merge-report}: Call: verbs/pr-merge.md --cleanup + ` --auto` if {auto} — gates internally; on pending/red CI, conflicts, behind-base, or unmet reviews it exits with the surface and checkpoint stops here. On merge-ready it merges, deletes the head, and syncs the base
    4. If the merge completed and {on-main}: bash: run it (content just landed on the base); {sync-report}: its output

9. Emit the ### feature-mode report

## Report

### base-mode

```
Branch: {branch} (base, path={effective-path} — detected)
Submodules: {ledger or — none declared}
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
On-main: {sync-report or none}
Checkpoint complete.
```

### feature-mode

```
Branch: {branch} → {default-branch}  (auto-created from topic | existing)   path={effective-path} — detected
Submodules: {ledger or — none declared}
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
PR: {opened #N | already open #N}
Merge: {merge-report} — merged via <strategy> + cleanup | halted at gate (<surface>)
On-main: {sync-report or — not reached}
```
