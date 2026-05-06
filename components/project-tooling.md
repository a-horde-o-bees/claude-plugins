# Project-level tooling

Project-level operations (test orchestration, one-time project setup) live under `tools/` and `bin/project-run` at project root — not inside any plugin. Anything tied to this repo's development infrastructure belongs here so it doesn't ship to downstream consumers of the plugins.

## Commands

| Command | Purpose |
|---------|---------|
| `bin/project-run setup` | Configure local git hookspath (run once per checkout) |
| `bin/project-run tests [--plugin <name> \| --project]` | Run suites in the current tree |
| `bin/project-run sandbox-tests [--ref <ref>]` | Run suites in a detached worktree at a given ref |

See `testing.md` for full test invocation patterns.

## Layout

- `tools/testing/` — test discovery, runner, venv resolution, detached-worktree wrapper
- `tools/setup/` — git hookspath configuration
- `bin/project-run` — bash entry point that resolves the project venv and dispatches to `tools/` modules

The boundary keeps dev infrastructure outside plugin trees. Each plugin remains shippable to end users without leaking project-level orchestration.
