# /git-checkpoint — project config

Path: pr

This repo integrates via feature branch → PR → merge (branch protection requires
`test`, `validate`). Checkpointing from `main` auto-creates a feature branch named
from the change topic and runs the PR lifecycle; the base branch is touched
directly only by an admin bypass — pass `--base-mode` to `/git-checkpoint`.

## Augmentations

- **Pre-commit** — run `python3 scripts/publish-skills.py` to regenerate the
  committed skill mirror (`skills/`) from the live source (`~/.claude/skills/`),
  so the mirror rides in the same commit. The pre-commit drift guard
  (`publish-skills.py --check`) keeps the mirror from being hand-edited out of
  sync.
- **On-main** — after content lands on `main`, run
  `python3 scripts/checkpoint-sync.py marketplace` and relay its output,
  including any restart recommendation. This refreshes how *other* machines
  consume the marketplace; local availability is already satisfied by the live
  source in `~/.claude/skills/`.

There is no per-checkpoint version bump. The single plugin's version moves only
when cutting a release (`/git-release`).
