# Sample

Mirrors of `https://github.com/baryhuang/mcp-server-aws-resources-python`. AWS resources MCP server — exposes a single AST-sandboxed `exec boto3` tool (code-as-tool) rather than enumerating each AWS API. 24 stars; MIT license; default branch `main`; active on main (specific date not surfaced).

## Server runtime

### Python with raw MCP SDK

Python (95.7% of repo); raw `mcp` Python SDK with boto3 underpinning. Version pin and import pattern not surfaced; `requires-python` value not explicitly surfaced.

## Transport

### stdio

stdio — the default MCP transport.

## Capability surface

### Single code-execution tool with sandbox

Single "run boto3 code" tool — the LLM authors a Python snippet on the fly rather than calling N hand-enumerated per-API tools. AST validation gates each invocation against an explicit allowlist of permitted imports (`boto3`, `operator`, `json`, `datetime`, `pytz`, `dateutil`, `re`, `time`). Also exposes a dynamic AWS-resources resource alongside the single tool.

## Configuration delivery

### Environment variables

Env vars injected into the Docker command in the host config (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optional `AWS_SESSION_TOKEN`, `AWS_DEFAULT_REGION`, or `AWS_PROFILE`).

### Mounted credentials

Alternative path: AWS profile / credential file mounted into the container.

## Authentication

### Cloud-native identity / credential chain

AWS credentials via env vars (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optional `AWS_SESSION_TOKEN`, `AWS_DEFAULT_REGION`, `AWS_PROFILE`) resolved through the AWS SDK chain.

### Mounted file credentials

AWS credentials file mounted into the container as an alternative to env-var pass-through.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per process — one AWS credential set.

## Distribution channel

### Docker / OCI image

`docker pull buryhuang/mcp-server-aws-resources:latest`. Multi-architecture image publishing covers `linux/amd64`, `arm64`, and `arm/v7` for broader platform coverage.

### Smithery registry

Smithery installable: `npx -y @smithery/cli install mcp-server-aws-resources-python --client claude`. Smithery as a distribution vector alongside Docker and source.

### Source clone with editable install

uv-based source build — git clone followed by uv install.

## Entry point and launch

### Bare interpreter + script path

Server entry at `src/mcp_server_aws_resources/server.py`. Console-script name not surfaced.

### Docker container entrypoint

Containerized launch via `docker run -i` against the published multi-arch image; host config invokes Docker as the command.

## Build and packaging

### Hatchling + uv (Python)

`pyproject.toml` present; build backend not surfaced. Version manager convention: uv. Lock file presence not surfaced.

## Schema and types

### Hand-authored tool schemas

Single hand-authored tool schema — input is a Python code string. Schema strategy details otherwise not surfaced.

### Async model (cross-cutting)

Synchronous code execution; asyncio/anyio usage not surfaced — sync handlers throughout.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

### Multi-architecture image publishing

Multi-arch images published for `linux/amd64`, `arm64`, `arm/v7`.

## Test stack

### No tests / not surfaced

Test details not surfaced in the README excerpt.

## CI

### GitHub Actions

`.github/` workflow directory present.

## Repository layout

### Single-package src-layout

Single package under `src/mcp_server_aws_resources/`.

## Safety and security posture

### AST validation with import allowlist

User-supplied Python is parsed to AST and validated against an explicit allowlist (`boto3`, `operator`, `json`, `datetime`, `pytz`, `dateutil`, `re`, `time`) before execution. Trust depends entirely on the allowlist's tightness.

## Host integration

### Claude Desktop

JSON `mcpServers` Docker command with env injection or AWS profile mount.

### Smithery / Glama discovery

Smithery CLI-installable via `@smithery/cli install`.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not observed.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

Active on main; specific date not surfaced.
