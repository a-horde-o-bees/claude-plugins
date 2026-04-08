---
pattern: "*"
depends:
  - .claude/rules/ocd-design-principles.md
---

# Workflow

Project-specific operational patterns governing how agents work day-to-day in this project.

## Working Directory

Working directory must remain project root for the entire session. Use absolute paths or tool flags instead of changing directories.

- No `cd`, `pushd`, `popd` — use `git -C <path>` for submodule operations
- Use relative paths from project root for `.claude/` scripts
- Compound commands (`&&`, `||`, `;`, `|`) are supported — each part checked independently against approval patterns

## Agents

- Minimize agent count — each agent independently loads context and rediscovers project; default to single agent processing tasks sequentially within one context

## Testing

- Verify new code by writing tests, not ad-hoc bash commands — when checking that something works, add a test to the relevant test file and run it; test fixtures handle environment setup automatically while ad-hoc commands require inline env vars that need manual approval
- Run only tests directly affected by current changes, scoped to narrowest relevant test file
- Run broader suites only when explicitly requested
- Exception: run full suite after structural changes (moves, renames, refactors) and before checkpoints — broken imports and cascading failures won't surface in narrow tests

## Naming

- Skill frontmatter `name` field uses plugin-name prefix — `ocd-navigator` not `navigator`; surfaces plugin name during search

## Package Structure

All packages (skills, plugin infrastructure) use standard Python entry points:

- `__main__.py` — agent-facing CLI; invoked via `python3 run.py <package> <command>`
- `__init__.py` — facade; public interface that `__main__.py` imports via `from . import *`
- Hook scripts are standalone modules invoked individually by hooks.json — no facade or `__main__.py`

## Interpreter

- `python3` not `python` — explicit interpreter version
- No shebangs, no execute permissions — scripts are invoked via interpreter prefix
