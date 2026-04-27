# Sample

## Identification

### url

https://github.com/awslabs/mcp/tree/main/src/aws-api-mcp-server

### stars

parent monorepo (awslabs/mcp) — sub-server has no independent star count

### last-commit

not captured individually (sub-server within actively-maintained monorepo)

### license

Apache-2.0

### default branch

main

### one-line purpose

AWS API MCP server — wraps the AWS CLI with `call_aws`, `suggest_aws_commands`, and an experimental `get_execution_plan` for NL-to-CLI guidance.

## Language and runtime

### language(s) + version constraints

Python `>=3.10`.

### framework/SDK in use

FastMCP 2.x (`fastmcp>=3.0.1`) alongside raw `mcp>=1.23.0` — both are declared dependencies.

## Transport

### supported transports

stdio (default, single-user); streamable-http (with optional OAuth).

### how selected

CLI / environment flag; OAuth configured via issuer + JWKS endpoints.

## Distribution

### every mechanism observed

PyPI package `awslabs.aws-api-mcp-server`; `uvx` invocation; `pip install`; Docker image published to AWS ECR; clone-from-source for development.

### published package name(s)

`awslabs.aws-api-mcp-server` (PyPI).

### install commands shown in README

- `uvx awslabs.aws-api-mcp-server@latest`
- `pip install awslabs.aws-api-mcp-server`
- Docker pull from public ECR

## Entry point / launch

### command(s) users/hosts run

`uvx awslabs.aws-api-mcp-server@latest`; `python -m awslabs.aws_api_mcp_server.server`; Docker run.

### wrapper scripts, launchers, stubs

Console script `awslabs.aws-api-mcp-server` → `awslabs.aws_api_mcp_server.server:main`.

## Configuration surface

### how config reaches the server

Environment variables (`AWS_PROFILE`, `AWS_REGION`, transport mode, OAuth endpoints, feature flags for experimental tools); CLI flags; Docker `-e` env injection for containerized runs.

## Authentication

### flow

stdio mode — AWS credential chain (profile or env); streamable-http — optional OAuth issuer + JWKS, or no-auth mode.

### where credentials come from

Standard AWS credential resolution (env vars, `~/.aws/credentials`, profile).

## Multi-tenancy

### tenancy model

Single-user only — README explicitly states "NOT designed for multi-tenant environments". Each instance requires dedicated credentials and working directory.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools only — `call_aws` (executes validated AWS CLI commands), `suggest_aws_commands` (NL → CLI mapping), `get_execution_plan` (experimental, feature-flagged).

## Observability

### logging destination + format, metrics, tracing, debug flags

`python-json-logger` + `loguru` dependencies imply structured JSON logging; specifics not extracted.

## Host integrations shown in README or repo

Not enumerated per host in the sub-server README — parent monorepo aggregates host examples.

## Claude Code plugin wrapper

### presence and shape

None at sub-server level; awslabs publishes via the MCP server catalog only.

## Tests

### presence, framework, location, notable patterns

pytest + pytest-asyncio + pytest-cov + pytest-mock declared as dev deps.

## CI

### presence, system, triggers, what it runs

Parent monorepo runs GitHub Actions; sub-server-specific CI config not extracted.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; images published to AWS public ECR.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`pre-commit`, `commitizen`, `ruff`, `pyright` in dev deps — implies enforced commit convention and type-checking.

## Repo layout

### single-package / monorepo / vendored / other

Sub-package inside the awslabs/mcp monorepo under `src/aws-api-mcp-server/`; self-contained `pyproject.toml` per sub-server.

## Notable structural choices

Wraps the AWS CLI (not boto3) — ships `awscli==1.44.81` as a pinned direct dependency and invokes CLI commands on behalf of the LLM.

Depends on both `mcp` SDK and `fastmcp` — one server bridging two SDK generations.

Pinning to a specific awscli version (1.44.81 exact) is unusual — suggests CLI behavior is part of the tested contract.

`lxml`, `requests`, `python-frontmatter`, `importlib_resources` suggest embedded documentation or spec assets are bundled in-package.

Read/write guard via feature flag (`get_execution_plan` experimental).

## Unanticipated axes observed

Sub-server as a first-class Python package — every monorepo sub-server has its own `pyproject.toml`, console script, and PyPI release, so consumers install one sub-server without pulling the rest.

CLI-wrapping vs SDK-wrapping as a server-design axis — this sub-server wraps a CLI; sibling `bedrock-kb-retrieval-mcp-server` uses boto3 directly.

Explicit anti-multi-tenancy statement — not just silence; the README documents the boundary.

Optional OAuth on streamable-http with configurable issuer/JWKS — a richer auth story than most Python MCP servers, which typically bypass auth and rely on the stdio channel.

## Python-specific

### SDK / framework variant

Both raw `mcp` and FastMCP 2.x — `mcp>=1.23.0` and `fastmcp>=3.0.1` declared together. Import pattern not captured directly (would need source read); dependency shape implies mixed use.

### Python version floor

`requires-python = ">=3.10"`.

### Packaging

Build backend: `hatchling`. Lock file not captured; `uv` recommended in README (likely `uv.lock`). Version manager convention: `uv` / `uvx` invocation throughout README.

### Entry point

`[project.scripts]` console script — `awslabs.aws-api-mcp-server = awslabs.aws_api_mcp_server.server:main`. Host-config snippet shape: `uvx awslabs.aws-api-mcp-server@latest`.

### Install workflow expected of end users

`uvx awslabs.aws-api-mcp-server@latest` (zero-install via uv).

### Async and tool signatures

Sync vs async not captured from README alone; FastMCP 3.x conventions support both.

### Type / schema strategy

`pydantic>=2.10.6` — Pydantic v2 schemas. FastMCP auto-derives from function signatures by convention.

### Testing

pytest + pytest-asyncio + pytest-cov + pytest-mock. Fixture style not captured.

### Dev ergonomics

pre-commit, ruff, pyright, commitizen — commit-style enforcement pipeline.

### Notable Python-specific choices

Bundles pinned `awscli==1.44.81` — a CLI tool distributed as a Python dependency of an MCP server.

Mixes `loguru` and `python-json-logger` — dual logging paths.

`importlib_resources` for packaged asset access.

`setuptools>=69.0.0` as a runtime dep (unusual for a hatchling-built package) — suggests setuptools-style entry-point resolution used at runtime.

## Gaps

Exact console-script implementation details, async vs sync tool signatures without reading source, whether OAuth validation is real JWT verification or a stub, exact sub-server CI config (inherits from monorepo), Docker image tagging scheme.
