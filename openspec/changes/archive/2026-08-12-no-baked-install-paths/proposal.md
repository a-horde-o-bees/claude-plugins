# No baked install paths in durable hosts

## Why

For non-skill hosts the tool rewrote `${CLAUDE_SKILL_DIR}` to the dependency's absolute folder — an install-dependent path baked into a durable file. On a plugin-consumer machine the plugin's folder is superseded on every update and no gate re-runs, so the paths rot silently. Ephemeral payloads (apply-over-queue) may bake absolute paths; durable hosts must not.

## What Changes

- **BREAKING** — flattening a dependency that references its bundled files via `${CLAUDE_SKILL_DIR}` into a non-skill host is refused with an error naming the dependency; the absolute-path rewrite for non-skill hosts is removed.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skill-dependency-flattening` — non-skill hosts refuse install-dependent material.

## Impact

- `~/.claude/skills/skill-authoring/scripts/flatten_skills.py`
