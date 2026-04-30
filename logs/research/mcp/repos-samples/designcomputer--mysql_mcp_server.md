# Sample

## Identification

### url

https://github.com/designcomputer/mysql_mcp_server

### stars

1.2k

### last-commit

v0.2.2 released April 18, 2025 (date inferred from release).

### license

MIT

### default branch

main

### one-line purpose

MySQL MCP server — exposes tables as MCP resources and executes SQL via tools; least-privilege user guidance built in.

## Language and runtime

### language(s) + version constraints

Python (93.2%), Dockerfile (6.8%); Python version floor declared as `>=3.11` in pyproject.toml. Specific runtime version not stated in fetched README content.

### framework/SDK in use

Anthropic MCP Python SDK (raw `mcp>=1.0.0`; not fastmcp).

## Transport

### supported transports

stdio.

### how selected

Implicit — only stdio is documented; README describes it as "stdio-based protocol server rather than standalone application".

## Distribution

### every mechanism observed

PyPI, Smithery installer, pip.

### published package name(s)

`mysql-mcp-server`.

### install commands shown in README

`pip install mysql-mcp-server`; `npx -y @smithery/cli install mysql-mcp-server --client claude`.

## Entry point / launch

### command(s) users/hosts run

Via `uv` or `uvx` package runners. README explicitly discourages `python ...` direct invocation, framing the server strictly as an MCP-protocol bridge for hosts.

### wrapper scripts, launchers, stubs

Dockerfile.

## Configuration surface

### how config reaches the server

Environment variables — `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`.

## Authentication

### flow

MySQL username/password.

### where credentials come from

Environment variables. README emphasizes "never commit" credentials and restricting to minimum-permission DB users.

## Multi-tenancy

### tenancy model

Single database connection per server; no per-request tenancy.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Resources — MySQL tables listed as resources, table contents readable. Tools — SQL query execution with error handling. Logging mentioned as "comprehensive."

## Observability

### logging destination + format, metrics, tracing, debug flags

Described as "comprehensive logging"; specifics not surfaced.

## Host integrations shown in README or repo

### Claude Desktop

`claude_desktop_config.json` example.

### VS Code

`mcp.json` example.

### Other editors/CLIs

Not enumerated.

## Claude Code plugin wrapper

### presence and shape

Not present.

## Tests

### presence, framework, location, notable patterns

pytest-based (`pytest.ini`, `requirements-dev.txt`); `tests/` directory.

## CI

### presence, system, triggers, what it runs

GitHub Actions (test.yml badge); workflow specifics not extracted.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

MCP Inspector debugging support referenced; JSON config examples for hosts.

## Repo layout

### single-package / monorepo / vendored / other

Single-package Python — `src/mysql_mcp_server/`, `tests/`, `.github/workflows/`, pyproject.toml.

## Notable structural choices

Exposes tables as MCP resources (not only tools) — one of the few DB MCP servers to use the resource surface. README explicitly frames direct Python invocation as incorrect usage, enforcing the "protocol bridge" mental model. Security guidance is baked into the README (least-privilege user, never commit credentials).

## Unanticipated axes observed

Resources-as-tables pattern is rare — most DB MCP servers expose everything through tools. README's emphasis on non-direct invocation is an explicit agent-posture choice.

## Python-specific

### SDK / framework variant

Raw `mcp` Python SDK — `mcp>=1.0.0`; no fastmcp. Import pattern: low-level MCP server API (inferred).

### Python version floor

`requires-python = ">=3.11"` — higher than the corpus's 3.10 mode. CI matrix not extracted.

### Packaging

Build backend: `hatchling.build`. Lock file: not explicitly noted in fetched content. Version manager convention: README uses uv/uvx; `pytest.ini` + `requirements-dev.txt` coexist with pyproject.toml (dual-config).

### Entry point

`[project.scripts]`: `mysql_mcp_server = "mysql_mcp_server:main"`. README host-config snippets show `uv --directory /path/to/repo run mysql_mcp_server` (dev) and `uvx --from mysql-mcp-server` (VS Code).

### Install workflow expected of end users

`pip install mysql-mcp-server`, Smithery CLI for one-shot host setup, from-source with venv. README explicitly frames direct `python ...` invocation as incorrect.

### Async and tool signatures

pytest configured (`pytest.ini`); pytest-asyncio not confirmed in fetched content. Source-level sync/async not inspected.

### Type / schema strategy

Low-level MCP SDK — hand-authored schemas likely; uses both tool and resource surfaces.

### Testing

pytest via separate `pytest.ini` and `requirements-dev.txt` (legacy split; pyproject.toml does not carry dev extras). `tests/` directory present.

### Dev ergonomics

Not observed beyond test config and Smithery CLI integration.

### Notable Python-specific choices

Requirements split across `pyproject.toml` + `pytest.ini` + `requirements-dev.txt` — older Python project layout; most newer projects in the corpus consolidate into pyproject.toml. Python 3.11 floor is higher than most — likely driven by the MySQL connector or a typing feature.

## Gaps

Last commit date only inferred from v0.2.2 release. Logging format and destination not specified. CI workflow contents not extracted.
