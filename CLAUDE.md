# Project Instructions

Operational procedures for agents working in the claude-plugins marketplace repository. Read the sibling `ARCHITECTURE.md` before acting.

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

`x.y.z` semver in each plugin's `.claude-plugin/plugin.json`. Tags live on main; no release branches.

**Pre-commit hook auto-bumps `z`** on every commit that stages changes to the plugin tree other than `plugin.json` itself. This keeps Claude Code's reload detection firing as dev-channel users track main. Commits that stage only `plugin.json` skip the auto-bump — that's the escape hatch release cuts use.

**Release cut:** bump `y`, reset `z = 0`, commit with only `plugin.json` staged, tag `v<x.y.0>` on that commit, push main + tag. `scripts/release.sh` automates the sequence; `.github/workflows/release.yml` fires on tag push to verify tag-commit version alignment, run tests, and create the GitHub release.

**Patch release:** tag a specific main commit as `v<current-version>`. No plugin.json edit required — the auto-bump already assigns each commit a unique patch-level version. The tag is the "deliberate release" signal; the commit's z value is just its place in the dev sequence.

**Pre-first-release:** `plugin.json` stays at `0.0.z` until the first `v0.1.0` release is cut. After that, the release series tracks whatever `y` is at the most recent tag; z auto-increments between tags.

## Plugin Reference

When implementing plugin infrastructure (hooks, MCP servers, dependency management, environment variables), check the official Claude Code plugin docs first: https://code.claude.com/docs/en/plugins-reference

This is the primary source for patterns, supported fields, and examples. Fetch the page and review relevant sections before designing new plugin features.

## Editing Rules, Conventions, and Patterns

Edit templates under each owning system's directory — rules in `plugins/ocd/systems/<system>/rules/` for system-scoped rules or `plugins/ocd/systems/rules/templates/` for project-wide rules; conventions in `plugins/ocd/systems/conventions/templates/`; patterns in `plugins/ocd/systems/patterns/templates/`. Never edit deployed copies in `.claude/` — a guard hook blocks those writes. Run `/checkpoint` to rectify deployed state: its auto-init step force-runs every system's `init()`, prunes orphans, and reconciles any DB backups.

## Adding Python Dependencies

Add the package to the target plugin's `pyproject.toml` under `[project.dependencies]`. The plugin's SessionStart hook detects the change on next session start (via `diff -q` against the cached copy) and reinstalls into the plugin's isolated venv automatically.

Prerequisite: `uv` must be installed on the user's system.

## System and Global Tool Dependencies

Tools installed globally on the user's system (npm globals, system packages, standalone binaries) cannot be auto-installed by plugins — they require user action. Skills that depend on these tools check availability at runtime in their Route and provide corrective install guidance:

```
1. Verify tool available — bash: `command -v <tool>`
    1. If not found: Exit to user — `<tool>` is required; install with `<install command>`
```

Use `SessionStart` hooks for Python packages (isolated in plugin venv). Use runtime checks in skills for everything else.

## Testing

- All tests: `bin/plugins-run tests` (or `bash scripts/test.sh`, which delegates to it). Scope flags: `--plugin <name>` for a single plugin's suite, `--project` for project-level tests only.
- Tests at a clean ref in a detached worktree: `bin/plugins-run sandbox-tests --ref <ref>`. Worktree is always removed before return.
- Project tests in `tests/`, per-plugin tests isolated by `pythonpath`.
- Plugin configs: `tests/plugins/<plugin>/pyproject.toml` under `[tool.pytest.ini_options]`; project config: root `pyproject.toml`.

## Project-level tooling

Project-level operations (test orchestration, one-time project setup) live under `tools/` and `bin/plugins-run` at project root — not inside any plugin. Anything tied to this repo's development infrastructure belongs here so it doesn't ship to downstream consumers of the plugins.

- `bin/plugins-run setup` — configure local git hookspath (run once per checkout).
- `bin/plugins-run tests [--plugin <name> | --project]` — run suites in the current tree.
- `bin/plugins-run sandbox-tests [--ref <ref>]` — run suites in a detached worktree at a given ref.
