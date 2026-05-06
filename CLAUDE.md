# claude-plugins

Project-level navigation hub for the claude-plugins marketplace repository. Read the sibling `ARCHITECTURE.md` before acting on internals.

## Universal triggers

When the user says **"checkpoint"**: skill: `/checkpoint`.

When implementing plugin infrastructure (hooks, MCP servers, dependency management, environment variables), the official Claude Code plugin docs are the primary source: <https://code.claude.com/docs/en/plugins-reference>

## Paths

Filesystem layout — every path at the root that an agent might need to read or reason about, with a one-line purpose.

| Path | Purpose |
|---|---|
| `TASKS.md` | Persistent task tracker; pointer-only, links to plans |
| `ARCHITECTURE.md` | Project-level architecture |
| `README.md` | User/contributor-facing overview |
| `MARKETPLACE-STANDARDS.md` | Marketplace conventions |
| `CHANGELOG.md` | Release history |
| `LICENSE` | Project license |
| `pyproject.toml` | Project Python dependencies and config |
| `uv.lock` | Locked Python dependency versions |
| `pyrightconfig.json` | Pyright type-checker configuration |
| `components/` | Reference content; topic per file — apply guidance when its trigger fires |
| `components/audit-skill-invocation.md` | Pre-flight check before invoking `/audit-*` skills (run `/checkpoint` first when content has shifted) |
| `components/skill-testing-modes.md` | Real invocation vs ad-hoc Task agent for skill development |
| `components/plugin-bin-invocation.md` | Bare-name (`ocd-run`) vs full-path (`plugins/ocd/bin/ocd-run`) and when to use each |
| `components/versioning.md` | `x.y.z` semver, pre-commit auto-bump, release cuts via `/ocd:git release`, patch releases |
| `components/template-edit-paths.md` | Where rule/convention/log templates live; never edit deployed copies under `.claude/` |
| `components/python-dependencies.md` | Adding a package to a plugin's `pyproject.toml` and the `SessionStart` reinstall |
| `components/external-tool-dependencies.md` | Runtime check pattern for npm globals / system packages skills depend on |
| `components/testing.md` | `bin/project-run tests` flag surface and layout |
| `components/project-tooling.md` | `bin/project-run` commands and `tools/` layout |
| `components/architectural-boundaries.md` | What the plugin layer can control vs what's harness-determined |
| `workflows/` | Top-down procedures (currently empty at project root — operational procedures live in skills under each plugin) |
| `plans/` | Active and upcoming workstreams; access via `TASKS.md` links |
| `plugins/` | Plugin systems; each subdirectory carries its own `CLAUDE.md` |
| `logs/` | Project log entries by type (decision, pattern, research, friction, idea, problem); routing per `log.md` rule |
| `tests/` | Project-level test suites; runtime per `components/testing.md` |
| `tools/` | Project-tooling scripts invoked via `bin/project-run` |
| `scripts/` | Standalone Python scripts (e.g., manifest validation) |
| `bin/` | Entry-point shims (e.g., `project-run`) |
| `.claude/` | Project-deployed Claude Code settings, rules, conventions |
| `.claude-plugin/` | Marketplace manifest |
| `.githooks/` | Git hooks (e.g., pre-commit version bump) |

## Cold-pickup

Read `TASKS.md`. Other paths load as the work calls for them.
