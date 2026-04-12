# /ocd-permissions skill: install, consolidate, review, and debug Claude Code settings across three layers

## Purpose

Skill design agreed upon 2026-03-27. Not yet implemented.

Workflows:
1. **Install** — merge recommended permissions template into project or user settings
2. **Consolidate** — scan settings.local.json for entries worth promoting to project or user level
3. **Review** — show current state across all three settings layers; surface overlaps and conflicts
4. **Debug** — analyze transcripts for commands user approved but settings don't cover; surface candidates for allow list

Key decisions:
- Skill owns the recommended permissions template
- Merge, not replace — preserves existing hooks and settings
- Lives in ocd plugin alongside auto-approval script
