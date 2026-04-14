# Project Instructions

Operational procedures for agents working in the claude-plugins marketplace repository. Read the sibling `architecture.md` before acting.

## Development Workflow

When user asks to "checkpoint" progress: skill: `/checkpoint`

## Evaluation Skill Invocation

Before invoking `/evaluate-*`, check whether `/checkpoint` is needed so the skill reads current content. These skills read deployed governance files (`.claude/rules/`, `.claude/conventions/`) and cached plugin files (target skill's SKILL.md and components). If template edits have not synced to deployed copies, if the target skill has uncommitted changes, or if the plugin cache is out of date relative to recent work, prompt the user to confirm running `/checkpoint` before proceeding. Uncommitted unrelated work is fine — only changes that affect what the skill reads matter.

## Skill Testing Modes

Two ways to exercise a skill during development:

- **Real invocation** — run via slash command (e.g., `/evaluate-governance`). Goes through the plugin cache. Claude Code loads everything under `plugins/<plugin>/` at session start — `SKILL.md` and every supporting file (component blocks, prompt fragments, anything in the skill directory). Edits are invisible to real invocations until `/checkpoint` refreshes the cache. Use for end-to-end orchestration verification.
- **Ad-hoc** — spawn a general-purpose agent via the Task tool with an explicit prompt that tells it to Read the skill's files by absolute path. Bypasses the cache — the agent reads from disk, so the latest edits propagate immediately. Use for iterating on component-file content (criteria, prompt fragments, shared instruction blocks) without the `/checkpoint` cycle between edits.

Ad-hoc validates instruction content; real invocation validates orchestration. Before closing out skill work, verify via real invocation after a `/checkpoint`.

## Versioning

`x.y.z` in each plugin's `.claude-plugin/plugin.json`:

- `x` — major; starts at `0` until a change breaks previous setups
- `y` — public release; cohesive set of changes ready for consumers; resets `z`
- `z` — every commit; required for plugin reload to detect changes

## Plugin Reference

When implementing plugin infrastructure (hooks, MCP servers, dependency management, environment variables), check the official Claude Code plugin docs first: https://code.claude.com/docs/en/plugins-reference

This is the primary source for patterns, supported fields, and examples. Fetch the page and review relevant sections before designing new plugin features.

## Editing Rules, Conventions, and Patterns

Edit templates in `plugins/ocd/templates/{rules,conventions,patterns}/`, never deployed copies in `.claude/`. Run `/sync-templates` to push changes to deployed copies for testing. The pre-commit hook runs the same sync automatically at commit time. A guard hook blocks direct edits to deployed copies.

## Adding Python Dependencies

Add the package to the target plugin's `requirements.txt`. The plugin's SessionStart hook detects the change on next session start and reinstalls into the plugin's isolated venv automatically.

Prerequisite: `uv` must be installed on the user's system.

## System and Global Tool Dependencies

Tools installed globally on the user's system (npm globals, system packages, standalone binaries) cannot be auto-installed by plugins — they require user action. Skills that depend on these tools check availability at runtime in their Route and provide corrective install guidance:

```
1. Verify tool available — bash: `command -v <tool>`
    1. If not found: Exit to user — `<tool>` is required; install with `<install command>`
```

Use `SessionStart` hooks for Python packages (isolated in plugin venv). Use runtime checks in skills for everything else.

## Testing

- All tests: `bash scripts/test.sh`
- Project tests in `tests/`, per-plugin tests isolated by `pythonpath`
- Plugin configs: `plugins/<plugin>/pytest.ini`; project config: `pyproject.toml`
