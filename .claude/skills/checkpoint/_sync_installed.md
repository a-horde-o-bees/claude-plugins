# Sync (Installed)

> Workflow component for `/checkpoint` when `sync_mode` is `installed`. Reads `.claude/installed-skills.json` and reinstalls any declared user-scope skill whose source plugin version has changed since last install via `npx skills add`.

> No restart recommendation — `npx skills` symlinks the new artifacts into `~/.claude/skills/<name>/` and Claude Code refreshes its `<available_skills>` registry mid-session.

### Process

1. {sync-output}: bash: `uv run .claude/skills/checkpoint/scripts/sync_skills.py`
2. Return to caller: {sync-output}
