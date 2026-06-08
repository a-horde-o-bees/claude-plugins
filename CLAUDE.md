# claude-plugins

The distribution mirror for skills authored in `~/.claude/skills/`. The published plugin is `skills/` (see `.claude-plugin/`); everything else is packaging and the sync tooling that produces the mirror.

## `skills/` is generated — never edit it directly

`skills/` is regenerated from `~/.claude/skills/` per `.claude/skill-manifest.json`. Edit the live source at `~/.claude/skills/<skill>/`, then sync.

## sync-skills

When I say **"sync-skills"**:

1. `python3 scripts/reconcile_manifest.py` — diff the manifest against the live source. Present any **new** live skills not yet in the manifest and ask which to add (apply with `reconcile_manifest.py --add <names>`); surface **removed**/**changed** for awareness.
2. `python3 scripts/sync_skills.py` — regenerate `skills/` from `~/.claude/skills/` per the manifest.

Then run `/git checkpoint` to branch, commit, and PR the updated mirror. **Sync before checkpoint** — `main` is pr/protected, so the mirror changes must already be in the working tree when checkpoint detects what to branch.
