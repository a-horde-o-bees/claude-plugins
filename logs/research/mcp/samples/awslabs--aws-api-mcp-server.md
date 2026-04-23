# awslabs/mcp (sub-server: aws-api-mcp-server)

## Identification
- url: https://github.com/awslabs/mcp/tree/main/src/aws-api-mcp-server
- stars: parent monorepo (awslabs/mcp) — sub-server has no independent star count
- last-commit (date or relative): not captured individually (sub-server within actively-maintained monorepo)
- license: Apache-2.0
- default branch: main
- one-line purpose: AWS API MCP server — wraps the AWS CLI with `call_aws`, `suggest_aws_commands`, and an experimental `get_execution_plan` for NL-to-CLI guidance.

## 1. Language and runtime
- language(s) + version constraints: Python `>=3.10`
- framework/SDK in use: FastMCP 2.x (`fastmcp>=3.0.1`) alongside raw `mcp>=1.23.0` — both are declared dependencies
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default, single-user); streamable-http (with optional OAuth)
- how selected: CLI / environment flag; OAuth configured via issuer + JWKS endpoints
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI package `awslabs.aws-api-mcp-server`; `uvx` invocation; `pip install`; Docker image published to AWS ECR; clone-from-source for development
- published package name(s): `awslabs.aws-api-mcp-server` (PyPI)
- install commands shown in README:
  - `uvx awslabs.aws-api-mcp-server@latest`
  - `pip install awslabs.aws-api-mcp-server`
  - Docker pull from public ECR
- pitfalls observed:
  - **Sub-server as a first-class Python package** — every monorepo sub-server has its own `pyproject.toml`, console script, and PyPI release, so consumers install one sub-server wi...
  - what couldn't be determined: exact console-script implementation details, async vs sync tool signatures without reading source, whether OAuth validation is real JWT verification...

## 4. Entry point / launch
- command(s) users/hosts run: `uvx awslabs.aws-api-mcp-server@latest`; `python -m awslabs.aws_api_mcp_server.server`; Docker run
- wrapper scripts, launchers, stubs: console script `awslabs.aws-api-mcp-server` → `awslabs.aws_api_mcp_server.server:main`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables (AWS_PROFILE, AWS_REGION, transport mode, OAuth endpoints, feature flags for experimental tools); CLI flags; Docker `-e` env injection for containerized runs
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: stdio mode — AWS credential chain (profile or env); streamable-http — optional OAuth issuer + JWKS, or no-auth mode
- where credentials come from: standard AWS credential resolution (env vars, `~/.aws/credentials`, profile)
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: **single-user only — README explicitly states "NOT designed for multi-tenant environments"**. Each instance requires dedicated credentials and working directory.
- pitfalls observed:
  - **Explicit anti-multi-tenancy statement** — not just silence; the README documents the boundary

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: tools only — `call_aws` (executes validated AWS CLI commands), `suggest_aws_commands` (NL → CLI mapping), `get_execution_plan` (experimental, feature-flagged)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: `python-json-logger` + `loguru` dependencies imply structured JSON logging; specifics not extracted
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
Not enumerated per host in the sub-server README — parent monorepo aggregates host examples
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none at sub-server level; awslabs publishes via the MCP server catalog only
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: pytest + pytest-asyncio + pytest-cov + pytest-mock declared as dev deps
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: parent monorepo runs GitHub Actions; sub-server-specific CI config not extracted
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile present; images published to AWS public ECR
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `pre-commit`, `commitizen`, `ruff`, `pyright` in dev deps — implies enforced commit convention and type-checking
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: sub-package inside the awslabs/mcp monorepo under `src/aws-api-mcp-server/`; self-contained `pyproject.toml` per sub-server
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Wraps the AWS CLI (not boto3) — ships `awscli==1.44.81` as a pinned direct dependency and invokes CLI commands on behalf of the LLM
- Depends on both `mcp` SDK and `fastmcp` — one server bridging two SDK generations
- Pinning to a specific awscli version (1.44.81 exact) is unusual — suggests CLI behavior is part of the tested contract
- `lxml`, `requests`, `python-frontmatter`, `importlib_resources` suggest embedded documentation or spec assets are bundled in-package
- Read/write guard via feature flag (`get_execution_plan` experimental)

## 18. Unanticipated axes observed
- **Sub-server as a first-class Python package** — every monorepo sub-server has its own `pyproject.toml`, console script, and PyPI release, so consumers install one sub-server without pulling the rest
- **CLI-wrapping vs SDK-wrapping** as a server-design axis — this sub-server wraps a CLI; sibling `bedrock-kb-retrieval-mcp-server` uses boto3 directly
- **Explicit anti-multi-tenancy statement** — not just silence; the README documents the boundary
- **Optional OAuth on streamable-http** with configurable issuer/JWKS — a richer auth story than most Python MCP servers, which typically bypass auth and rely on the stdio channel

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: **both** — `mcp>=1.23.0` and `fastmcp>=3.0.1` declared together
- version pin from pyproject.toml: `mcp>=1.23.0`, `fastmcp>=3.0.1`
- import pattern observed: not captured directly (would need source read); dependency shape implies mixed use

### Python version floor
- `requires-python` value: `>=3.10`

### Packaging
- build backend: `hatchling`
- lock file present: not captured; `uv` recommended in README (likely `uv.lock`)
- version manager convention: `uv` / `uvx` invocation throughout README

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: `[project.scripts]` — `awslabs.aws-api-mcp-server = awslabs.aws_api_mcp_server.server:main`
- actual console-script name(s): `awslabs.aws-api-mcp-server`
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): `uvx awslabs.aws-api-mcp-server@latest`

### Install workflow expected of end users
- install form + one-liner from README: `uvx awslabs.aws-api-mcp-server@latest` (zero-install via uv)

### Async and tool signatures
- sync `def` or `async def`: not captured from README alone; fastmcp 3.x conventions support both

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: `pydantic>=2.10.6` — Pydantic v2 schemas
- schema auto-derived vs hand-authored: FastMCP auto-derives from function signatures by convention

### Testing
- pytest / pytest-asyncio / unittest / none: pytest + pytest-asyncio + pytest-cov + pytest-mock
- fixture style: not captured

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: pre-commit, ruff, pyright, commitizen — commit-style enforcement pipeline

### Notable Python-specific choices
- Bundles pinned `awscli==1.44.81` — a CLI tool distributed as a Python dependency of an MCP server
- Mixes `loguru` and `python-json-logger` — dual logging paths
- `importlib_resources` for packaged asset access
- `setuptools>=69.0.0` as a runtime dep (unusual for a hatchling-built package) — suggests setuptools-style entry-point resolution used at runtime

## 20. Gaps
- what couldn't be determined: exact console-script implementation details, async vs sync tool signatures without reading source, whether OAuth validation is real JWT verification or a stub, exact sub-server CI config (inherits from monorepo), Docker image tagging scheme
