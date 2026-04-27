# Sample

## Identification

### url

https://github.com/awslabs/mcp/tree/main/src/mcp-lambda-handler

### stars

parent monorepo

### last-commit (date or relative)

not captured individually

### license

Apache-2.0

### default branch

main

### one-line purpose

Framework (not server) for building Lambda-hosted MCP servers — decorator-based tool declaration on API Gateway with pluggable DynamoDB session state.

## 1. Language and runtime

### language(s) + version constraints

Python `>=3.10`

### framework/SDK in use

custom — does not depend on `mcp` or `fastmcp` as a runtime dep; implements the serverless HTTP surface directly

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

HTTP (via AWS API Gateway → Lambda)

### how selected

deployment-time; there is no stdio path — this is inherently HTTP

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI package `awslabs.mcp-lambda-handler`; embedded as a library dependency inside a user's Lambda package

### published package name(s)

`awslabs.mcp-lambda-handler`

### install commands shown in README

`pip install -e .[dev]` (for local development)

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

none — **this is a library, not a standalone server**. The user writes a Lambda handler that delegates to `MCPLambdaHandler`

### wrapper scripts, launchers, stubs

console script `awslabs.mcp-lambda-handler` → `awslabs.mcp_lambda_handler.server:main` declared but primary use is library import

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Lambda environment variables, session backend configuration (NoOp or DynamoDB or custom class)

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

delegated to API Gateway + Lambda Authorizer — bearer tokens in `Authorization` header validated upstream of the handler

### where credentials come from

API Gateway authorizer output; application never sees raw tokens

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

**per-request tenant model** — Lambda invocations are naturally isolated; session backend (DynamoDB) keyed by session ID allows persistent state per tenant across requests

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools — declared via `@mcp.tool()` decorator in the user's Lambda module

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

CloudWatch Logs (implicit via Lambda); X-Ray tracing can layer on; no specific logging framework listed in deps

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

Not a host-configured server — deployed as Lambda + API Gateway; consumers configure their MCP client to hit the API Gateway URL

- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none — this artifact is infrastructure for building remote MCP servers

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

dev extras installable via `pip install -e .[dev]` but test framework not extracted

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

parent monorepo

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

no Dockerfile at this level — Lambda is the packaging target (zip archive)

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

example Lambda handler in README showing `mcp.handle_request(event, context)`

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

sub-package in awslabs/mcp; deliberately packaged small

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- **Not an MCP server — a framework for building Lambda-hosted MCP servers**. Breaks the "server" assumption of the sample
- **Pluggable session management** — NoOp (stateless) or DynamoDB (persistent) with a custom-backend interface
- **Decorator-driven tool declaration** (`@mcp.tool()`) — familiar FastMCP pattern but reimplemented on top of Lambda request/response shapes rather than `fastmcp`
- **Zero dependency on the `mcp` Python SDK or `fastmcp`** — instead, declares `python-dateutil`, `boto3`, `botocore` only; implies protocol wire format is implemented directly against Lambda events
- **API Gateway as the transport layer** — the MCP-over-HTTP endpoint (`/mcp`) is an API Gateway route, and authentication is offloaded to Lambda Authorizers
- Smallest dependency footprint of any awslabs sub-server observed (3 deps)

## 18. Unanticipated axes observed

- **"Server" vs "server-framework"** — a sub-package in an MCP-server monorepo that is itself not a server but a library for building servers. Reveals a structural category the sample schema doesn't anticipate
- **Protocol implementation without the official SDK** — the package presumably re-implements MCP message framing on top of API Gateway events rather than importing `mcp`
- **Session management as a pluggable extension point** — most MCP servers are single-process stateless or single-process stateful; this one externalizes session state to DynamoDB, matching serverless best practice
- **Infrastructure-dependent auth** (API Gateway Authorizer) — authentication is architecturally outside the server, not inside it
- **Serverless deployment model** as a first-class target — cold-start sensitivity, statelessness, external session stores all become design concerns

## 19. Python-specific

### SDK / framework variant

- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: **custom** — neither `mcp` nor `fastmcp` imported
- version pin from pyproject.toml: N/A (not a consumer of either SDK)
- import pattern observed: consumer imports `from awslabs.mcp_lambda_handler import MCPLambdaHandler` and uses `@mcp.tool()` decorator

### Python version floor

- `requires-python` value: `>=3.10`

### Packaging

- build backend: hatchling
- lock file present: not captured
- version manager convention: pip (`pip install -e .[dev]`); `uv` not emphasized

### Entry point

- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script declared (`awslabs.mcp-lambda-handler`) but primary usage is library import inside a Lambda handler — `def lambda_handler(event, context): return mcp.handle_request(event, context)`
- actual console-script name(s): `awslabs.mcp-lambda-handler`
- host-config snippet shape: N/A — deployed as Lambda, invoked via HTTPS endpoint

### Install workflow expected of end users

- install form + one-liner from README: `pip install -e .[dev]` for local; in production, included as a dependency in the Lambda deployment package

### Async and tool signatures

- sync `def` or `async def`: Lambda handlers are typically sync; tool functions likely sync `def`

### Type / schema strategy

- Pydantic / dataclasses / TypedDict / raw dict / Annotated: not captured — no Pydantic dependency listed, so likely dataclasses or TypedDict

### Testing

- pytest / pytest-asyncio / unittest / none: dev extras exist; specifics not extracted

### Dev ergonomics

- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: not captured; Lambda testing typically via SAM or Lambda local invoke

### Notable Python-specific choices

- Pure-stdlib HTTP protocol handling (no Pydantic, no mcp-sdk, no fastmcp) — the smallest trustworthy surface
- `python-dateutil` as the only non-AWS runtime dep — suggests time-sensitive session token handling
- boto3 + botocore pair (rather than just boto3) — explicit, enables DynamoDB session backend

## 20. Gaps

### what couldn't be determined

whether MCP protocol is re-implemented byte-for-byte or piggybacks on a subset; exact session schema for the DynamoDB backend; how `@mcp.tool()` decorator maps to the protocol without `fastmcp`; test framework; whether streaming responses are supported given Lambda response-size constraints
