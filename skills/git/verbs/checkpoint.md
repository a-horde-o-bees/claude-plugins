# git checkpoint

Bundle the checkpoint for the current branch. The driver's preflight routes every repo — parent and submodules alike — by detection (live git/forge state + parent-owned native `.gitmodules` keys), never a config file, and computes the per-submodule plan; this verb sequences the verbs over that plan. Judgment stays here: the feature-branch name, and every land/halt surface.

## Dependencies

- `scripts/gitflow.py checkpoint-preflight` — the one mechanical pass: branch resolution, routing, gaps, the per-submodule plan (`sub-prep` / `sub-reconcile` / `branch-create` are its mechanical companions).
- `verbs/commit.md`, `verbs/push.md`, `verbs/ci.md` — the commit/push/CI verbs; each handles declared submodules via the driver, inherited here for free.
- `verbs/pr-status.md`, `verbs/pr-open.md`, `verbs/pr-merge.md` — the PR loop run for a `pr`-integrated repo. Gating lives in these; this verb only sequences them.
- `.claude/git/checkpoint.md` (optional, root-only) — `## Augmentations` steps; never routing. Absent ⇒ pure detection.

## Variables

- `{branch}` — `--branch <name>`; defaults to current. Explicit `--branch` must match current (the preflight enforces this).
- `{paths}` — optional `--paths <pathspec>...`; scopes the whole checkpoint. Empty = the whole tree.
- `{base-mode}` — `--base-mode`: the one explicit override — land directly on the base even when detection says `pr` (the admin/direct-land exception).
- `{auto}` — `--auto`: hands-off. Threaded verbatim to `/git pr-open` and `/git pr-merge`; the verbs own what it bypasses. Checkpoint adds no auto behavior of its own.
- `{path}` — `--path <pr | direct>`, **internal only**: a parent passes its decided integration into a recursive submodule run, so a parent `x-integration` override the submodule can't see in its own `.gitmodules` is still honored. Forwarded to the preflight.
- `{feature-branch}` — the topic-derived `<area>/<topic>` branch auto-created when checkpointing a `pr` repo from its base branch.
- From the preflight JSON: `{default-branch}`, `{root}`, `{effective-path}`, `{pending}`, `{needs-feature-branch}`, `{pin-only}` (submodule paths the parent only pins), `{land}` (pr-integrated submodules with work to land), `{ledger}` (per-submodule routing outcomes, surfaced in the report and on a halt), `{augmentations}` (`present` + declared step names — the machine-carried signal that the root `checkpoint.md` has steps to honor).
- `{pre-land}`, `{on-main}` — augmentation steps from the root `checkpoint.md` `## Augmentations`, each empty when there is no file or the step isn't declared.

## Rules

- **Detection is the source of truth.** The preflight routes the parent and every submodule from live permission / fork / default-branch-protection plus parent-owned native `.gitmodules` keys (`branch`, `update`, `x-integration`, `x-contribute`). There is no `Path:` config and no per-repo routing markdown. `/git doctor` writes the native keys for gaps.
- **The parent's path is detected, not chosen.** Integration is a repo property, read from the default branch — a checkpoint run from a feature branch still reads the repo as `pr`. `--base-mode` is the sole deliberate exception (direct-land on a `pr` repo, admin).
- **One preflight; any gap halts.** It runs before anything is committed. Any gap — undeterminable permission, an undeclared push branch, edits to a read-only repo — halts up front with the exact native-key fix or a `/git doctor` pointer. No mid-flight bootstrap, no silent fallback, no proceeding on ambiguity.
- **The parent pins merged shas, never unmerged ones.** A PR-governed submodule whose PR does not land halts the whole checkpoint — the ledger names what already landed (irreversibly) vs. halted, and landed submodules are skipped on re-run. After a submodule lands, `sub-reconcile` pins it to origin's merged tip (refusing over a dirty tree).
- **Augmentations are honored, not hardcoded.** The root `checkpoint.md` may declare project steps to run *before the commit* (pre-land — e.g. a version bump) and *after content reaches the base* (on-main — e.g. a delivery sync). This verb runs them at those points and carries none of their content. The file holds augmentations only — never routing — and is optional.
- **No optimistic merge.** Merge runs through `/git pr-merge`, whose hard gate (red or pending CI, conflicts, behind-base) exits rather than merging on unknown state. Under `--auto` the merge verb watches in-flight CI to green and merges in the same run; only a hard failure halts.
- **Skip the commit/push portion silently when nothing is pending** — not an error. The PR/merge phase still proceeds on a feature branch.

## Process

1. Preflight (before anything is committed):
    1. `{pre}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py checkpoint-preflight` — append ` --branch {branch}` when `--branch` given, ` --paths {paths}` when set, ` --base-mode` when set, ` --path {path}` when internally supplied
    2. If BLOCKED (detached HEAD, branch mismatch, or routing gaps): Exit process: the driver's output verbatim — each gap as `{repo}: {gap} → {fix}`, with a `/git doctor` pointer. No mid-flight bootstrap, no guessing.
    3. Bind from `{pre}` JSON: `{branch}`, `{default-branch}`, `{root}`, `{effective-path}`, `{pending}`, `{needs-feature-branch}`, `{pin-only}`, `{land}`, `{ledger}`

2. Land pr-integrated submodules — for each `{sub}` in `{land}` (each is a full lifecycle of its own):
    1. Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py sub-prep --path {sub.path}` — normalize off detached HEAD; BLOCKED (divergence) → Exit process: `{ledger}`
    2. Bash: `cd {sub.path}` — make the submodule the working directory for the recursive run
    3. `{sub-report}`: Call: verbs/checkpoint.md --path `{sub.integration}` + ` --auto` if `{auto}` — full lifecycle in the submodule: commit → push → CI → open PR → merge (gated) → cleanup, recursing its own sub-submodules
    4. Bash: `cd {root}` — return to the superproject
    5. If `{sub-report}` did not land the PR (gate halt — pending/red CI, conflicts, unmet reviews): Exit process: submodule `{sub.path}`'s PR did not land. Landed this run: `{ledger}`. Resolve in `{sub.path}`, then re-invoke (landed submodules are skipped). The parent is not pinned to an unmerged sha
    6. Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py sub-reconcile --path {sub.path}` — pin to the merged tip; `{merged}`: its `pinned`
    7. add `{sub.path}` to `{pin-only}`; `{ledger}` += `{sub.path}: landed PR, pinned {merged}`

3. Load augmentations — driven by `{augmentations}` from the preflight JSON (the mechanical signal; do not rely on remembering this step). If `{augmentations}.present`: Read `{augmentations}.file` — bind its `## Augmentations` steps (`{pre-land}`, `{on-main}`), each empty if not declared. Else: both empty.
4. Branch under `pr` — when `{needs-feature-branch}`, or when `{effective-path}` is `pr` AND `{branch}` == `{default-branch}` AND step 2 landed a submodule (the pin advance must route through a PR too):
    1. `{feature-branch}`: author a kebab-case `<area>/<topic>` name from the in-scope change — `{area}` the single plugin or directory the scope sits under (else a short domain word), `{topic}` what the change does. Derive from the diff, not from prompt text.
    2. Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py branch-create --name {feature-branch}` — carries the working tree onto the new branch
    3. `{branch}`: `{feature-branch}` — subsequent steps route to the feature-PR lifecycle

5. Pre-land — if `{pre-land}`: Bash: run it (e.g. the version bump), before committing so CI validates the result. When `{paths}` is set, scope the augmentation to it so only in-scope plugins bump.
6. Commit + push + CI (every context) — pass `--pin-only {p}` for each `{p}` in `{pin-only}` so the verbs skip submodules checkpoint already landed or pins:
    1. `{commit-report}`: Call: verbs/commit.md `{paths}` + ` --auto` if `{auto}` + ` --pin-only {p}` for each `{pin-only}` — pass `--on-base` when `{branch}` == `{default-branch}` so the verb's base guard permits the intentional base commit
    2. `{push-report}`: Call: verbs/push.md --branch `{branch}` + ` --pin-only {p}` for each `{pin-only}`
    3. `{ci-report}`: Call: verbs/ci.md --branch `{branch}`

7. Base mode — when `{effective-path}` is `direct` OR `{branch}` == `{default-branch}`:
    1. If `{on-main}`: Bash: run it (content is on the base now — e.g. delivery sync); `{sync-report}`: its output
    2. Emit the ### base-mode report and stop

8. Feature-PR lifecycle — when `{effective-path}` is `pr` AND `{branch}` ≠ `{default-branch}`:
    1. `{pr-status}`: Call: verbs/pr-status.md --branch `{branch}`
    2. If `{pr-status}` reports no open PR: Call: verbs/pr-open.md + ` --auto` if `{auto}`
    3. `{merge-report}`: Call: verbs/pr-merge.md --cleanup + ` --auto` if `{auto}` — gates internally; on pending/red CI, conflicts, behind-base, or unmet reviews it exits with the surface and checkpoint stops here. On merge-ready it merges, deletes the head, and syncs the base
    4. If the merge completed and `{on-main}`: Bash: run it (content just landed on the base); `{sync-report}`: its output

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
