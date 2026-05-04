# Sample

Mirrors of `https://github.com/shreyaskarnik/huggingface-mcp-server`. Hugging Face Hub MCP server — uses all three MCP surfaces (tools + resources + prompts) with a custom `hf://` URI scheme; Smithery-first distribution; single-file server kept at repo root. ~70 stars, MIT, default branch `main`. Last commit not surfaced.

## Server runtime

### Python with raw MCP SDK

Raw `mcp` Python SDK (not FastMCP). Import pattern `from mcp.server import Server` style. Python version via `.python-version` (exact value not surfaced).

## Transport

### stdio

stdio (MCP default); stdio-only.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

All three MCP primitives exercised in one server. Tools: search/info on models, datasets, spaces, papers, collections. Prompts: `compare-models`, `summarize-paper`. Resources: custom `hf://` URI scheme exposed via MCP resources — the custom URI scheme exposes a vendor-native namespace (Hugging Face Hub) addressable through MCP resources rather than `file://` or `http://`. Two MCP prompts shipped alongside the tool surface.

## Configuration delivery

### Environment variables

`HF_TOKEN` optional environment variable.

## Authentication

### API key (optional, for higher rate limits)

`HF_TOKEN` env var optional — present grants higher rate limits and private-repo access; absent still works for public/read-only operations.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user.

## Distribution channel

### Smithery registry

Distributed via Smithery CLI as `@shreyaskarnik/huggingface-mcp-server` — `npx -y @smithery/cli install @shreyaskarnik/huggingface-mcp-server --client claude`. Smithery-first distribution.

### Source clone with `uv run` from source tree

Source clone alternative: `uv sync && uv run huggingface_mcp_server.py`.

## Entry point and launch

### Bare interpreter + script path

Bare script `huggingface_mcp_server.py` at repo root; no console script. Host-config snippet shape `uv run <path>/huggingface_mcp_server.py`.

### Source-tree `uv run`

`uv sync && uv run huggingface_mcp_server.py` — uv-from-source invocation.

## Build and packaging

### Hatchling + uv (Python)

Build backend likely hatchling (uv convention); not directly verified. `uv.lock` likely present.

### Python version pinning

`.python-version` file present; exact value not surfaced.

## Schema and types

### Pydantic v2 models

Pydantic via MCP SDK; schema auto-derived from signatures.

### Async model (cross-cutting)

Mix of sync and async (MCP SDK accepts both).

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

## Host integration

### Claude Desktop

macOS/Windows config paths shown in README.

### Smithery / Glama discovery

Registered with Smithery; install command goes through Smithery CLI.

## Repository layout

### Single-package flat layout

Flat layout — main server file (`huggingface_mcp_server.py`) at repo root; `src/huggingface/` for helpers. Hybrid flat-with-helper-subpackage shape: a single hackable script at root with supporting modules in a sibling `src/` package.

## Safety and security posture

### Read-only by default with explicit write flag

README explicitly scopes the server to read-only access; no write tools shipped.

## Developer ergonomics

### Inspector/debug tooling references

MCP CLI via `mcp[cli]` implied as a developer dependency.

### Sample MCP client configs in repo

Claude Desktop JSON snippet shipped in README.

## Documentation surface

### README as the canonical surface

README is the canonical surface.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
