# awslabs/mcp (sub-server: bedrock-kb-retrieval-mcp-server)

## Identification
- url: https://github.com/awslabs/mcp/tree/main/src/bedrock-kb-retrieval-mcp-server
- stars: parent monorepo (awslabs/mcp)
- last-commit (date or relative): not captured individually
- license: Apache-2.0
- default branch: main
- one-line purpose: AWS Bedrock knowledge-base MCP server — boto3-direct KB discovery, NL querying, data-source filtering, and region/permission-gated reranking; tag-scoped access.

## 1. Language and runtime
- language(s) + version constraints: Python `>=3.10`
- framework/SDK in use: raw `mcp[cli]>=1.23.0` — no fastmcp
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio
- how selected: default; not configurable from README
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI `awslabs.bedrock-kb-retrieval-mcp-server`; `uvx`; Windows `.exe`; Docker
- published package name(s): `awslabs.bedrock-kb-retrieval-mcp-server`
- install commands shown in README:
  - `uvx awslabs.bedrock-kb-retrieval-mcp-server@latest`
  - `uv tool run --from awslabs.bedrock-kb-retrieval-mcp-server@latest awslabs.bedrock-kb-retrieval-mcp-server.exe`
  - `docker build -t awslabs/bedrock-kb-retrieval-mcp-server .`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `awslabs.bedrock-kb-retrieval-mcp-server`
- wrapper scripts, launchers, stubs: console script → `awslabs.bedrock_kb_retrieval_mcp_server.server:main`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: env vars — `AWS_PROFILE`, `AWS_REGION`, `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_SESSION_TOKEN`, `KB_INCLUSION_TAG_KEY`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: AWS credential chain via configured profile or direct env credentials (including STS session tokens)
- where credentials come from: standard AWS resolution
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user per deployment; knowledge-base scoping via AWS tag (`mcp-multirag-kb=true` by default, overridable via `KB_INCLUSION_TAG_KEY`)
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: tools — knowledge-base discovery, data-source listing, natural-language KB querying, result filtering by data source, result reranking (region/permission-gated)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: `loguru`
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
Aggregated in parent monorepo
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: not captured from README
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: parent monorepo
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: not captured
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: sub-package in awslabs/mcp
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- **Uses boto3 directly** (`boto3>=1.37.24`) — no AWS CLI wrapping, unlike the aws-api sibling
- **Tag-based KB scoping** — only knowledge bases tagged with `mcp-multirag-kb=true` are surfaced; scoping is enforced server-side via AWS tag filters, not by the LLM
- Extremely lean dependency set: 4 runtime deps (boto3, loguru, mcp, pydantic)
- Reranking is conditional on region and IAM permissions — feature gate via capability probing

## 18. Unanticipated axes observed
- **Tag-driven resource scoping as an MCP pattern** — AWS tags become the access-control boundary for which KBs the server can see. A novel solution to "too many resources in the account" without building app-level access control
- **Capability-probing at start** — reranking only exposed when region + perms allow, rather than failing at tool-call time
- **boto3-direct vs CLI-wrap split inside the same monorepo** — two design styles coexist; this sub-server represents the "thin SDK wrapper" style

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: raw `mcp[cli]>=1.23.0`
- version pin from pyproject.toml: `mcp[cli]>=1.23.0`, `boto3>=1.37.24`, `pydantic>=2.11.1`, `loguru>=0.7.3`
- import pattern observed: not captured; raw SDK pattern

### Python version floor
- `requires-python` value: `>=3.10`

### Packaging
- build backend: hatchling
- lock file present: not captured
- version manager convention: `uv`

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script
- actual console-script name(s): `awslabs.bedrock-kb-retrieval-mcp-server`
- host-config snippet shape: `uvx awslabs.bedrock-kb-retrieval-mcp-server@latest`

### Install workflow expected of end users
- install form + one-liner from README: `uvx awslabs.bedrock-kb-retrieval-mcp-server@latest`

### Async and tool signatures
- sync `def` or `async def`: boto3 is sync by nature — likely sync handlers

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: Pydantic v2.11

### Testing
- pytest / pytest-asyncio / unittest / none: not captured

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: not captured

### Notable Python-specific choices
- One of the leanest Python MCP server dep sets observed (4 runtime deps)
- No httpx — boto3 owns all network I/O, which keeps the stack consistent with AWS SDK conventions

## 20. Gaps
- what couldn't be determined: async/sync pattern in handlers, specific reranker API used, tag-filter implementation details, test presence
