---
log-role: queue
---

# Plugin init auto-stages deployed files to git

## Purpose

When a plugin's `init()` produces files under tracked deployment directories (`.claude/ocd/`, `.claude/rules/`, `logs/<type>/`, etc.) and the project has a git root, the init step should `git add` the newly-deployed files itself. Today the agent has to make a judgment call when `git status` surfaces a freshly-deployed file as untracked — should it be committed, gitignored, or surfaced as suspicious? — and that judgment is fragile.

The 2026-04-26 sandbox/log-research checkpoint hit this: `setup init` produced `.claude/ocd/enabled-systems.json` (records which systems are enabled in the checkout), the file landed untracked, and the agent excluded it from the checkpoint commit on the assumption it was per-environment local state. The directory it lives in is fully tracked (`paths.csv`, `navigator.db`, deployed templates), so the new file should travel with the repo too — but the agent had to be corrected to make that call. Eliminating the judgment call by having init stage its own outputs makes the deployment contract self-consistent: if it's deployed, it's tracked.

## Approach

Extend the deployment contract (per python.md *Init/Status Contract*) so that `init()` implementations stage their produced files when:

- A git root exists at `environment.get_project_dir()`
- The deployed file is inside the project tree (not under `~/.claude/` or some other out-of-tree location)
- The file is not already gitignored at its destination path

Implementation hooks naturally into the existing `setup.deploy_files` / `setup.deploy_paths_csv` helpers — the same place that already writes the deployed file becomes the place that runs `git add`. No per-system change required if every system delegates writes through those helpers.

## Why this fits with /ocd:git's existing autonomy

The `/ocd:git` skill already automates commit grouping, message drafting, derivative-commit collection (via `/checkpoint`), and push. The deployment-side staging slots in upstream of that — `setup init` runs, files land, they're staged, the next commit picks them up via the existing `git add <path>` flow. Symmetric: `/ocd:git` automates downstream of the working tree; `setup init` automates upstream into the working tree.

This also means `/checkpoint`'s "stage by name" rule still holds — the staged paths are explicit, named by init at write time, never `git add -A`.

## Edge cases

- **Files that should NOT be tracked** — credentials, per-machine paths, build artifacts. These should not be deployed to a tracked directory in the first place. If they are, that's a separate fix (move them to a gitignored location), not an exception to this rule.
- **Initial deploy on a fresh checkout** — first `init()` produces hundreds of files; staging them all in one shot is fine, the resulting commit is a single "Deployed — initial install" entry that matches today's pattern.
- **Force-rebuild (`init(force=True)`)** — files that get reinstalled (e.g. `navigator.db` wipe-and-recreate) should still be staged so the resulting blob change appears in the next commit. Same flow.
- **No git root** — silently skip the staging step. The deploy still works; it just doesn't auto-track.

## Consequences

- Agent never has to judge whether a deployed file should be tracked — by definition, if init produced it inside a tracked tree, it travels.
- `/checkpoint`'s derivative-commit step becomes more reliable: auto-init outputs are already staged when the post-init `git status --short` runs.
- Future systems that add new deployed files don't need each contributor to remember to track them — the contract handles it.

## Prerequisites

- Audit existing `setup.deploy_files` / `setup.deploy_paths_csv` call sites to confirm every deployed-file write routes through the staging point
- Decision on whether the staging behavior is opt-in (a flag on `deploy_files`) or universal (all deployments stage by default). Universal is simpler; opt-in preserves an escape hatch for legitimately-untracked deploys.
