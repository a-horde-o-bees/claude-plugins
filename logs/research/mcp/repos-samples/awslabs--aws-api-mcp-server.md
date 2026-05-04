# Sample

Mirrors of `https://github.com/awslabs/mcp/tree/main/src/aws-api-mcp-server`. AWS API MCP server — wraps the AWS CLI with `call_aws`, `suggest_aws_commands`, and an experimental `get_execution_plan` for NL-to-CLI guidance. Apache-2.0, default branch `main`, sub-server inside the awslabs/mcp monorepo.

## Server runtime

### Python with both MCP SDK and FastMCP declared

Hybrid path — `pyproject.toml` declares both `mcp>=1.23.0` and `fastmcp>=3.0.1` as dependencies; one server bridging two SDK generations. Import patterns not directly captured. Async/sync tool signatures not surfaced from README alone.

## Transport

### stdio

Default transport for single-user mode; AWS credential chain (profile or env) provides identity.

### Streamable HTTP

Optional streamable-HTTP mode with optional OAuth issuer + JWKS configuration.

### Selection mechanism

CLI flag / environment variable. OAuth configured via issuer + JWKS endpoints (separate concern from transport selection).

## Capability surface

### Tools-only, hand-curated narrow surface

Tools only — `call_aws` (executes validated AWS CLI commands), `suggest_aws_commands` (NL → CLI mapping), `get_execution_plan` (experimental, feature-flagged).

### Capability gating flags (per-tool, per-category, write-mode)

Experimental tool (`get_execution_plan`) gated behind a feature flag.

## Configuration delivery

### Environment variables

`AWS_PROFILE`, `AWS_REGION`, transport mode env, OAuth endpoints, feature flags for experimental tools.

### CLI flags

CLI flag surface for transport selection and feature toggles.

## Authentication

### Cloud-native identity / credential chain

stdio mode — AWS credential chain (env vars, `~/.aws/credentials`, profile). Single-user only.

### OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)

streamable-HTTP mode — optional OAuth with configurable issuer + JWKS endpoints, or a no-auth mode. A richer auth story than typical Python MCP servers; whether OAuth validation is real JWT verification or stub not captured.

## Multi-tenancy

### Single-user / single-tenant per process

README explicitly states "NOT designed for multi-tenant environments." Each instance requires dedicated credentials and working directory.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published as `awslabs.aws-api-mcp-server` on PyPI; canonical install `uvx awslabs.aws-api-mcp-server@latest`.

### PyPI via pip / pipx

`pip install awslabs.aws-api-mcp-server` documented as an alternative.

### Docker / OCI image

Docker image published to AWS public ECR.

### Source clone with editable install

Clone-from-source documented for development.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` console script `awslabs.aws-api-mcp-server` → `awslabs.aws_api_mcp_server.server:main`. Quoted dotted name pattern lets the dotted PyPI name match the dotted console-script name.

### `uvx <package>`

Host-config snippet shape: `uvx awslabs.aws-api-mcp-server@latest`.

### Module invocation / `python -m <module>` fallback

`python -m awslabs.aws_api_mcp_server.server` documented.

### Docker container entrypoint

Docker run as an alternative launch form.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Version manager convention: uv / uvx invocation throughout README. Lock file not captured (uv.lock recommended in README).

### Python version pinning

`requires-python = ">=3.10"`.

### Pin discipline (Python)

Tight: bundles `awscli==1.44.81` exact pin (CLI behavior is part of the tested contract); ranged on `mcp>=1.23.0`, `fastmcp>=3.0.1`, `pydantic>=2.10.6`.

## Schema and types

### Pydantic v2 models

`pydantic>=2.10.6` declared — Pydantic v2 schemas. FastMCP auto-derives from function signatures by convention; with hybrid SDK path some hand-registration also likely.

### FastMCP auto-derivation from type hints

FastMCP 3.x conventions support auto-derivation from typed signatures.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

### Published Docker image

Images published to AWS public ECR.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio + pytest-cov + pytest-mock declared as dev deps.

### Linter/formatter test gate

ruff + pyright in dev deps.

## CI

### Monorepo CI inheritance

Parent monorepo runs GitHub Actions; sub-server-specific CI config not extracted.

## Host integration

### Monorepo catalog

Sub-server README defers host-integration examples to the parent monorepo catalog rather than enumerating per host.

## Observability

### loguru (Python)

`loguru` for application logging; sometimes paired with `python-json-logger` — dual logging paths in one server.

## Repository layout

### Monorepo of namespace-prefixed packages

Sub-package inside the awslabs/mcp monorepo under `src/aws-api-mcp-server/` with its own `pyproject.toml` and PyPI release. Each sub-server independently published and installable.

## Safety and security posture

### Anti-multi-tenancy disclaimer

README explicitly states "NOT designed for multi-tenant environments" — documents the boundary rather than letting users assume.

## Developer ergonomics

### `pre-commit` framework

`pre-commit` declared in dev deps.

### `commitizen`

`commitizen` declared in dev deps — commit-message convention enforcement.

### Linter and type-checker stack

ruff, pyright in dev deps.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.
