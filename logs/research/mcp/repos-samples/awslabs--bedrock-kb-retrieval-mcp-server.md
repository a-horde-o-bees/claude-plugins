# Sample

Mirrors of `https://github.com/awslabs/mcp/tree/main/src/bedrock-kb-retrieval-mcp-server`. AWS Bedrock knowledge-base MCP server — boto3-direct KB discovery, NL querying, data-source filtering, and region/permission-gated reranking; tag-scoped access. Apache-2.0; default branch `main`; sub-package in awslabs/mcp monorepo (parent stars carry; per-server last-commit not captured individually).

## Server runtime

### Python with raw MCP SDK

Python `>=3.10` server using the raw `mcp[cli]>=1.23.0` SDK directly — no FastMCP wrapper. Runtime dependency surface is one of the leanest observed: 4 packages — `boto3>=1.37.24`, `loguru>=0.7.3`, `mcp[cli]>=1.23.0`, `pydantic>=2.11.1`. boto3 is sync by nature so handlers are likely sync; no `httpx` is used because boto3 owns all network I/O.

## Transport

### stdio

stdio is the only supported transport. Default; not configurable from the README.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools-only surface — knowledge-base discovery, data-source listing, natural-language KB querying, result filtering by data source, and result reranking. No resources, prompts, sampling, or roots.

### Capability probing and conditional surfacing

Reranking is conditional on AWS region and IAM permissions — feature gate via capability probing at start, rather than failing at tool-call time.

## Configuration delivery

### Environment variables

Configuration via env vars: `AWS_PROFILE`, `AWS_REGION`, `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` (including STS), and `KB_INCLUSION_TAG_KEY` for tag-scope override.

## Authentication

### Cloud-native identity / credential chain

AWS standard credential chain — configured profile, direct env credentials, or STS session tokens — resolved by the AWS SDK. No MCP-level auth on top.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per deployment — one AWS credential context per process.

### Tag-based resource scoping

Knowledge-base scoping enforced server-side via AWS tag filters: only knowledge bases tagged with `mcp-multirag-kb=true` (default; overridable via `KB_INCLUSION_TAG_KEY`) are surfaced. Tag enforcement happens at the server, not in LLM prompts.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx awslabs.bedrock-kb-retrieval-mcp-server@latest` — published on PyPI as `awslabs.bedrock-kb-retrieval-mcp-server` and runnable through uvx without prior install.

### Windows .exe variant

Documented Windows path: `uv tool run --from awslabs.bedrock-kb-retrieval-mcp-server@latest awslabs.bedrock-kb-retrieval-mcp-server.exe`.

### Docker / OCI image

Dockerfile present; documented build: `docker build -t awslabs/bedrock-kb-retrieval-mcp-server .`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `awslabs.bedrock-kb-retrieval-mcp-server` mapped to `awslabs.bedrock_kb_retrieval_mcp_server.server:main`. Quoted dotted name in `[project.scripts]` matches the dotted PyPI package name.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Version manager convention: `uv`. `requires-python = ">=3.10"`. Lock file presence not captured.

## Schema and types

### Pydantic v2 models

Pydantic v2.11 for structured payloads with the raw `mcp` SDK.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Per-server Dockerfile under `src/bedrock-kb-retrieval-mcp-server/`.

## Observability

### loguru (Python)

`loguru` for application logging.

## Repository layout

### Monorepo of namespace-prefixed packages

Sub-package inside the `awslabs/mcp` monorepo of `awslabs.*` namespace-prefixed PyPI packages.

## Domain logic and embedded intelligence

### Pass-through tool wrappers

Uses boto3 directly (`boto3>=1.37.24`) — thin SDK wrapper, no AWS CLI wrapping (unlike the aws-api sibling). Tools map onto Bedrock KB API operations.

## CI

### Monorepo CI inheritance

CI inherited from parent monorepo; no workflow at sub-server level.

## Host integration

### Monorepo catalog

Host integrations aggregated in the parent monorepo's catalog rather than per-sub-server.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No Claude Code plugin or skill wrapper at this sub-package.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Active development

Default branch `main`; active maintenance via parent monorepo.
