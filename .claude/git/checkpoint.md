# /git-checkpoint — project config

Path: pr

This repo integrates via feature branch → PR → merge (branch protection requires
`test`, `validate`, `bump-check`). The base branch (`main`) is touched directly
only by an admin bypass — `/git-checkpoint` handles that as base-mode.

## Augmentations

- **Pre-land** — before the commit, run `python3 scripts/bump-apply.py --fetch origin/main`.
  Applies this checkpoint's integration-time plugin version bump (`z+1` of the
  freshly-fetched `main`), so the bump rides in the commit and CI validates it.
  Idempotent; a manual minor/major bump is respected. `bump-check` (required) is
  the belt.
- **On-main** — after content lands on `main` (a feature merge, or a base-mode
  push), run `python3 scripts/checkpoint-sync.py marketplace` and relay its
  output, including any restart recommendation.
