# Sample

## Identification

### url

https://github.com/shibuiwilliam/mcp-server-scikit-learn

### stars

~13

### last-commit

not surfaced

### license

MIT

### default branch

main

### one-line purpose

scikit-learn MCP server — model-training and inference tools against local datasets.

## 1. Language and runtime

### language(s) + version constraints

Python 99.7%, Makefile 0.3%; Python version not explicitly surfaced.

### framework/SDK in use

raw `mcp` Python SDK (not FastMCP).

### pitfalls observed

Python version floor not surfaced.

## 2. Transport

### supported transports

stdio (MCP default).

### how selected

stdio-only

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

source clone + editable install (`pip install -e ".[dev]"`); `uv run` launch.

### published package name(s)

not confirmed on PyPI.

### install commands shown in README

`pip install -e ".[dev]"`.

### pitfalls observed

Whether PyPI publication exists not confirmed.

## 4. Entry point / launch

### command(s) users/hosts run

`uv --directory=src/mcp_server_scikit_learn run mcp-server-scikit-learn`.

### wrapper scripts, launchers, stubs

Makefile targets present (1 line in Makefile language).

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

MCP server JSON config (command/args) — no env-based config documented.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

none

### where credentials come from

N/A — operates on local data/models.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools for model training/evaluation, dataset handling, preprocessing, feature engineering, model persistence, cross-validation, hyperparameter tuning.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not documented

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON command/args snippet using `uv --directory=... run`.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest (`pytest -s -v tests/`); `tests/` directory.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions infra present (details not surfaced).

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

not observed

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Makefile for developer commands.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`src/mcp_server_scikit_learn/`).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Scopes scikit-learn around MCP: model lifecycle (train → eval → persist) becomes a tool surface rather than a notebook flow. Uses `uv --directory=...` in host config — unusual path-anchored invocation; implies no pip-installed console script for end users. `.[dev]` install pattern — dev tools via PEP 621 optional deps, not a separate requirements-dev file.

## 18. Unanticipated axes observed

Exposing an ML training pipeline over MCP raises a state-lifecycle question (where do trained models persist? who owns them?) that the tool surface implicitly answers via `model_persistence` tools.

## 19. Python-specific

### SDK / framework variant

raw `mcp` SDK; version pin not surfaced; import pattern `mcp.server`.

### Python version floor

`requires-python` value not surfaced.

### Packaging

Build backend not surfaced (uv-backed). Lock file: `uv.lock` present. Version manager convention: uv.

### Entry point

`[project.scripts]` → `mcp-server-scikit-learn`; console-script name `mcp-server-scikit-learn`; host-config snippet shape `uv --directory=src/mcp_server_scikit_learn run mcp-server-scikit-learn`.

### Install workflow expected of end users

source clone + editable pip install; one-liner `pip install -e ".[dev]"`.

### Async and tool signatures

scikit-learn is sync-only; tools likely sync.

### Type / schema strategy

Pydantic via MCP SDK.

### Testing

pytest; fixture style not inspected.

### Dev ergonomics

Makefile present.

### Notable Python-specific choices

sync tool signatures likely throughout — sklearn is sync and wrapping it async would introduce threads; staying sync is the right call for this domain. `uv --directory=<path>` in host config rather than `uvx <package>` — suggests the package isn't meant for pip-install-everywhere distribution, more for developer-installed local runs.

## 20. Gaps

Python version floor not surfaced. Whether PyPI publication exists not confirmed. Docker absence appears intentional but not stated.
