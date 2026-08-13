# Flatten non-skill hosts

## Why

confirm-shared-intent is @-imported into the user CLAUDE.md — a runtime include that carries frontmatter noise, verifies nothing, and links nothing. Every other force-loaded dependency in the system is build-time materialized and freshness-gated; CLAUDE.md should be a flatten host like any other.

## What Changes

- `flatten_skills.py` accepts non-skill host files (e.g. `~/.claude/CLAUDE.md`) via an explicit `--skills-root`; references resolve against that root, and `${CLAUDE_SKILL_DIR}` in units rewrites to the absolute dependency folder, since no dispatcher binds the variable outside a skill invocation.
- The user CLAUDE.md replaces its @-import with a `/confirm-shared-intent` reference and a materialized region.
- Automation: the mirror-sync freshness gate also checks the user CLAUDE.md; skill-authoring's lint pass names non-skill hosts in the refresh/check routine.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skill-dependency-flattening` — non-skill host files join the contract.

## Impact

- `~/.claude/skills/skill-authoring/scripts/flatten_skills.py`, `~/.claude/skills/skill-authoring/SKILL.md`
- `~/.claude/CLAUDE.md`
- `scripts/sync_skills.py` (freshness gate)
