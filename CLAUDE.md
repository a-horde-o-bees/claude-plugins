# Project Instructions

Operational procedures for agents working in the claude-plugins marketplace repository. Read the sibling `architecture.md` before acting.

## Development Workflow

When user asks to "checkpoint" progress: skill: `/checkpoint`

## Audit Skill Invocation

Before invoking `/audit-*`, check whether `/checkpoint` is needed so the skill reads current content. These skills read deployed governance files (`.claude/rules/`, `.claude/conventions/`) and cached plugin files (target skill's SKILL.md and components). If template edits have not synced to deployed copies, if the target skill has uncommitted changes, or if the plugin cache is out of date relative to recent work, prompt the user to confirm running `/checkpoint` before proceeding. Uncommitted unrelated work is fine — only changes that affect what the skill reads matter.

## Skill Testing Modes

Two ways to exercise a skill during development:

- **Real invocation** — run via slash command (e.g., `/ocd:status`). Goes through the plugin cache. Claude Code loads everything under `plugins/<plugin>/` at session start — `SKILL.md` and every supporting file (component blocks, prompt fragments, anything in the skill directory). Edits are invisible to real invocations until `/checkpoint` refreshes the cache. Use for end-to-end orchestration verification.
- **Ad-hoc** — spawn a general-purpose agent via the Task tool with an explicit prompt that tells it to Read the skill's files by absolute path. Bypasses the cache — the agent reads from disk, so the latest edits propagate immediately. Use for iterating on component-file content (criteria, prompt fragments, shared instruction blocks) without the `/checkpoint` cycle between edits.

Ad-hoc validates instruction content; real invocation validates orchestration. Before closing out skill work, verify via real invocation after a `/checkpoint`.

## Versioning

`x.y.z` in each plugin's `.claude-plugin/plugin.json`. Main and release branches live in disjoint version spaces — `(x,y,z)` never points at more than one commit across branches.

**Main** tracks `0.0.z` permanently. `z` is a monotonic dev build counter, bumped automatically by the git pre-commit hook on every commit to catch Claude Code's reload detection. Main is never released from directly.

**Release branches** own real semver:

- When cutting a new release `x.y.0`: branch from main, bump `plugin.json` to `x.y.0`, run release prep (content curation, doc regeneration). All prep commits hold `plugin.json` at `x.y.0`. Tag at the final commit.
- Patch releases on a release branch: bump `plugin.json` to `x.y.(z+1)` on the patch commit and tag.
- Main continues z-incrementing in `0.0.z` space, unaffected by the release cut.

## Plugin Reference

When implementing plugin infrastructure (hooks, MCP servers, dependency management, environment variables), check the official Claude Code plugin docs first: https://code.claude.com/docs/en/plugins-reference

This is the primary source for patterns, supported fields, and examples. Fetch the page and review relevant sections before designing new plugin features.

## Editing Rules, Conventions, and Patterns

Edit templates under each owning system's directory — rules in `plugins/ocd/systems/<system>/rules/` for system-scoped rules or `plugins/ocd/systems/rules/templates/` for project-wide rules; conventions in `plugins/ocd/systems/conventions/templates/`; patterns in `plugins/ocd/systems/patterns/templates/`. Never edit deployed copies in `.claude/` — a guard hook blocks those writes. Run `/checkpoint` to rectify deployed state: its auto-init step force-runs every system's `init()`, prunes orphans, and reconciles any DB backups.

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
