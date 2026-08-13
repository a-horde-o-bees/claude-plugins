# Settings-file host registry

## Why

Non-skill flatten hosts are kept in the loop by a hardcoded path in the mirror-sync gate and a prose list in doctrine — a second opted-in file would silently drift, and nothing gives users a sanctioned place to declare hosts. Claude Code's settings.json convention already solves per-scope configuration; the flatten tool should borrow it.

## What Changes

- `settings.skill-authoring.json` at user level (`~/.claude/`) and project level (nearest `.claude/` above cwd) carries `{"hosts": [...]}`; the tool unions and dedups both automatically on suite-scoped invocations — no flag.
- Hosts resolve references against the running tool's own sibling suite, so a plugin update regenerates them against the superseding versions; relative project entries resolve against the project root.
- The sync gate's hardcoded CLAUDE.md check is deleted (the registry covers it); skill-authoring's lint pass simplifies back to `--check <skills-root>`.
- The user CLAUDE.md becomes the first registered host.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skill-dependency-flattening` — host discovery via per-skill settings files replaces per-invocation host naming.

## Impact

- `~/.claude/skills/skill-authoring/scripts/flatten_skills.py`, `~/.claude/skills/skill-authoring/SKILL.md`
- `scripts/sync_skills.py`
- `~/.claude/settings.skill-authoring.json` (new)
