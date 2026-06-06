# /git-checkpoint — project config

Path: direct

This repo integrates by committing straight to the base branch and pushing — no
PR, no feature-branch lifecycle. `/git-checkpoint` on any branch runs
commit → push.

## Augmentations

- **Pre-commit** — run `python3 scripts/publish-skills.py` to regenerate the
  committed skill mirror (`skills/`) from the live source (`~/.claude/skills/`),
  so the mirror rides in the same commit. The drift guard
  (`publish-skills.py --check`) keeps the mirror from being hand-edited out of
  sync.
- **Post-push** — run `python3 scripts/checkpoint-sync.py marketplace` and relay
  its output, including any restart recommendation. This refreshes how *other*
  machines consume the marketplace; local availability is already satisfied by
  the live source in `~/.claude/skills/`.

There is no per-checkpoint version bump. The single plugin's version moves only
when cutting a release (`/git-release`).
