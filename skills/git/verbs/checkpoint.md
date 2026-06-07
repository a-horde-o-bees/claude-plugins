# git checkpoint

> Bundle the checkpoint for the current branch. Branches on the project's configured path: the full feature-branch lifecycle to a merged base, or commit + push + CI on the base. The orchestrator owns the sequence; the verbs own their gates, recursion, and message authoring; the project owns its augmentations via `.claude/git/checkpoint.md`.

## Dependencies

- `verbs/commit.md`, `verbs/push.md`, `verbs/ci.md` — the commit/push/CI verbs; each recurses depth-first into declared submodules, inherited here for free.
- `verbs/pr-status.md`, `verbs/pr-open.md`, `verbs/pr-merge.md` — the feature-branch PR loop (the `pr` path). Gating lives in these; this verb only sequences them.
- `partials/checkpoint-bootstrap.md` — the project config bootstrap on first run.
- `.claude/git/checkpoint.md` — the project config: integration `Path:` + `## Augmentations` steps.

## Variables

- `{branch}` — `--branch <name>`; defaults to current. Explicit `--branch` must match current (the push verb enforces this).
- `{path}` — `--path`; else the config's `Path:`; else `pr`.
- `{paths}` — optional `--paths <pathspec>...`; scopes the whole checkpoint to those paths — only they are committed and landed, the rest of the working tree stays parked. Empty = the whole tree. Passed to `/git commit` and exposed to the pre-land augmentation for scoping its bump.
- `{base-mode}` — `--base-mode` present: land directly on the base branch (the admin/direct-land exception) instead of auto-creating a feature branch under `pr`.
- `{auto}` — `--auto` present: hands-off. Threaded verbatim to `/git pr-open` and `/git pr-merge`; the verbs own what it bypasses (the description review gate; soft-blocker prompts; the pending-CI watch). Checkpoint adds no auto behavior of its own.
- `{feature-branch}` — the topic-derived `<area>/<topic>` branch auto-created when checkpointing from the base branch under `pr`.
- `{root}` — the superproject toplevel (`git rev-parse --show-toplevel`), captured so the router returns to it after `cd`-ing into a submodule for a recursive run.
- `{pin-only}` — submodule paths the parent only pins (PR-governed ones it landed; vendored ones). Passed as `--pin-only` to the commit/push verbs so they skip re-processing them.
- `{ledger}` — per-submodule routing outcomes (landed PR + pinned sha / pin-only / direct), surfaced in the report and on a halt.

## Rules

- **The orchestrator sequences; the verbs gate.** Checkpoint does not re-check CI, mergeability, or reviews — it calls the verbs, which gate and exit with the surface. A verb's exit halts the checkpoint.
- **Path selects the flow.** `pr` → on a feature branch, run the PR lifecycle; on the base branch with pending in-scope changes, auto-create a feature branch named from the change topic, then run it. `direct` → any branch runs commit + push + CI, no PR. Landing directly on the base under `pr` is the explicit exception — `--base-mode`.
- **Repos route by detection, not a config file.** Before the parent commits, one mechanical pass (`pr.py routes`) routes the parent and every declared submodule — viewerPermission, fork/upstream, branch protection — combined with parent-owned native `.gitmodules` overrides (`update=`, `x-integration=`). A protected, owned working branch → the submodule's FULL PR lifecycle runs in place (recurse → commit → push → CI → open PR → merge → cleanup) and lands first; an unprotected owned branch → direct push via the verbs; a vendored (READ/NONE) repo → pin-only, never pushed. Routing lives in the parent; nothing is written into a submodule.
- **The parent pins merged shas, never unmerged ones.** A PR-governed submodule whose PR does not land halts the whole checkpoint — the ledger names what already landed (irreversibly) vs. halted, and landed submodules are skipped on re-run. After a submodule lands, checkpoint reconciles its HEAD to origin's merged tip before the parent records the pin advance, guarding a stale local sha (the `git pull` no-op case).
- **One routing pre-flight; any gap halts.** The `pr.py routes` pass runs before anything is committed. Any gap — undeterminable permission, an undeclared push branch, edits to a read-only repo — halts up front with the exact native-key fix (`git config -f .gitmodules …`) or a `/git doctor` pointer, parent and submodule alike. No mid-flight bootstrap, no silent fallback to a guessed branch, no proceeding on ambiguity.
- **Augmentations are honored, not hardcoded.** `checkpoint.md` may declare project steps to run *before the commit* (pre-land — e.g. the version bump) and *after content reaches the base* (on-main — e.g. a delivery sync). This verb runs them at those points and carries none of their content; the project owns its bump, delivery, and the scripts they name. Absent config ⇒ pure generic flow.
- **No optimistic merge.** Merge runs through `/git pr-merge`, whose hard gate (red or pending CI, conflicts, behind-base) exits rather than merging on unknown state. If CI is still in flight at the merge gate, checkpoint stops there and the merge completes on a re-invocation once green. Under `--auto`, the merge verb watches in-flight CI to green and merges in the same run instead of stopping; only a hard failure (red CI, conflict, behind-base) halts.
- **Skip the commit/push portion silently when nothing is pending** — not an error. The PR/merge phase still proceeds on a feature branch.

## Process

1. Resolve branch:
    1. {branch}: bash: `git branch --show-current`
    2. If {branch} is empty (detached HEAD): Exit process — detached HEAD; checkout a branch first
    3. If `--branch` given and ≠ {branch}: Exit process — branch mismatch; re-invoke with `--branch {branch}` or switch branches
    4. {default-branch}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` — fallback `main`

2. Load project config:
    1. {config}: `.claude/git/checkpoint.md`
    2. If {config} does not exist AND no `--path` given: Call: partials/checkpoint-bootstrap.md ({config}: {config})
    3. {path}: `--path` if given, else `Path:` read from {config}, else `pr`
    4. If {config} exists: Read it — bind its `## Augmentations` steps ({pre-land}, {on-main}), each empty if not declared

3. Branch under `pr` (auto-create as needed) — when {path} is `pr` AND {branch} == {default-branch} AND no `--base-mode`:
    1. {pending}: bash: `git status --short -- {paths}` — pending changes in scope
    2. If {pending} is empty: skip — nothing to branch for; the flow falls through to base-mode (a no-op) or, if a PR is already open for an existing branch, drives it
    3. {feature-branch}: author a kebab-case `<area>/<topic>` name from the in-scope change — {area} the single plugin or directory the scope sits under (else a short domain word), {topic} what the change does (e.g. `writing/rules-self-carrying-polarity`). Derive from the diff, not from prompt text.
    4. bash: `git checkout -b {feature-branch}` — carries the working tree onto the new branch
    5. {branch}: {feature-branch} — subsequent steps route to the feature-PR lifecycle

4. Routing pre-flight + land PR-governed submodules (before the parent commits) — one mechanical pass routes the parent and every submodule; any gap halts up front:
    1. {root}: bash: `git rev-parse --show-toplevel`
    2. {routes}: bash: `python3 ${CLAUDE_SKILL_DIR}/scripts/pr.py routes` (append ` --paths {paths}` when {paths} is set) — one pass over the parent + every declared submodule, each repo's `{path, integration, sync, gaps, branch, perm, has_edits}` plus the combined gap list, all probes run in-process. The verb spends no context gathering routing
    3. If {routes}.ok is false: Exit process — routing is ambiguous; resolve every gap, then re-invoke. List each {routes}.gaps entry as `{repo}: {gap} → {fix}`. Run `/git doctor` to write the native keys it can. No mid-flight bootstrap, no guessing — parent and submodule gaps halt the same way
    4. {pin-only}: empty; {ledger}: empty
    5. For each {repo} in {routes}.repos with {repo}.path ≠ `.` (the submodules):
        1. {sub}: {repo}.path
        2. If {repo}.integration is `read-only`: add {sub} to {pin-only}; {ledger} += `{sub}: pin-only (vendored)`; continue
        3. If {repo}.integration is `direct`: {ledger} += `{sub}: direct (verbs push it)`; continue — left to the commit/push verbs' direct recursion
        4. {repo}.integration is `pr`:
            1. {sub-dirty}: bash: `git -C {sub} status --short`
            2. If {sub-dirty} is empty: add {sub} to {pin-only}; {ledger} += `{sub}: pin-only (already landed / no work)`; continue — nothing to land; the parent records its pin (the idempotent re-run path)
            3. {wb}: {repo}.branch. Normalize off detached HEAD (the recursive checkpoint exits on detached): {cur}: bash: `git -C {sub} rev-parse --abbrev-ref HEAD`; if {cur} is `HEAD`: {sha}: bash: `git -C {sub} rev-parse HEAD`; {decl}: bash: `git -C {sub} rev-parse --verify {wb} 2>/dev/null`; if {decl} is empty: bash: `git -C {sub} checkout -b {wb}`; else if {decl} == {sha}: bash: `git -C {sub} checkout {wb}`; else: Exit process — {sub}'s {wb} diverges from its detached HEAD; resolve manually
            4. bash: `cd {sub}` — make the submodule the working directory for the recursive run
            5. {sub-report}: Call: verbs/checkpoint.md --path pr + ` --auto` if {auto} — full lifecycle in {sub}: recurse its own sub-submodules, commit → push → CI → open PR → merge (gated) → cleanup
            6. bash: `cd {root}` — return to the superproject
            7. If {sub-report} did not land the PR (gate halt — pending/red CI, conflicts, unmet reviews): Exit process — submodule {sub}'s PR did not land. Landed this run: {ledger}. Resolve in {sub}, then re-invoke (landed submodules are skipped). The parent is not pinned to an unmerged sha
            8. Reconcile the pin to the merged tip (guard the `git pull` no-op): {default}: bash: `git -C {sub} symbolic-ref --short refs/remotes/origin/HEAD | sed 's@^origin/@@'` (fallback {wb}); bash: `git -C {sub} fetch origin {default}`; {merged}: bash: `git -C {sub} rev-parse origin/{default}`; {head}: bash: `git -C {sub} rev-parse HEAD`; if {head} ≠ {merged}: bash: `git -C {sub} checkout {default}` then `git -C {sub} reset --hard {merged}`
            9. add {sub} to {pin-only}; {ledger} += `{sub}: landed PR, pinned {merged}`

5. Pre-land — if {pre-land}: bash: run it (e.g. the version bump), before committing so CI validates the result. When {paths} is set, scope the augmentation to it (the augmentation references `{paths}` — e.g. the bump runs `--paths {paths}`) so only in-scope plugins bump.
6. Commit + push + CI (every context) — pass `--pin-only {p}` for each {p} in {pin-only} so the verbs skip submodules checkpoint already landed or pins:
    1. {commit-report}: Call: verbs/commit.md {paths} + ` --auto` if {auto} + ` --pin-only {p}` for each {pin-only} — pass `--on-base` when {branch} == {default-branch} (an intentional base commit) so the verb's base guard permits it. `--auto` auto-consumes the landed submodules' pin advances
    2. {push-report}: Call: verbs/push.md --branch {branch} + ` --pin-only {p}` for each {pin-only}
    3. {ci-report}: Call: verbs/ci.md --branch {branch}

7. Base mode — when {path} is `direct` OR {branch} == {default-branch}:
    1. If {on-main}: bash: run it (content is on the base now — e.g. delivery sync); {sync-report}: its output
    2. Emit the ### base-mode report and stop

8. Feature-PR lifecycle — when {path} is `pr` AND {branch} ≠ {default-branch}:
    1. {pr-status}: Call: verbs/pr-status.md --branch {branch}
    2. If {pr-status} reports no open PR: Call: verbs/pr-open.md + ` --auto` if {auto}
    3. {merge-report}: Call: verbs/pr-merge.md --cleanup + ` --auto` if {auto} — runs the shared gate script directly (fresh, no round-trip) and gates internally; on pending/red CI, conflicts, behind-base, or unmet reviews it exits with the surface and checkpoint stops here. Under `--auto` it instead watches in-flight CI to green and admin-overrides soft blockers where the viewer has rights. On merge-ready it merges, deletes the head, and syncs the base.
    4. If the merge completed and {on-main}: bash: run it (content just landed on the base); {sync-report}: its output

9. Emit the ### feature-mode report

## Report

### base-mode

```
Branch: {branch} (base, path={path})
Submodules: {ledger or — none declared}
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
On-main: {sync-report or none}
Checkpoint complete.
```

### feature-mode

```
Branch: {branch} → {default-branch}  (auto-created from topic | existing)
Submodules: {ledger or — none declared}
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
PR: {opened #N | already open #N}
Merge: {merge-report} — merged via <strategy> + cleanup | halted at gate (<surface>)
On-main: {sync-report or — not reached}
```
