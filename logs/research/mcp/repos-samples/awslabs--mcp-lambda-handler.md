# Sample

Mirrors of `https://github.com/awslabs/mcp/tree/main/src/mcp-lambda-handler`. Framework (not server) for building Lambda-hosted MCP servers — decorator-based tool declaration on API Gateway with pluggable DynamoDB session state. Apache-2.0; default branch `main`; sub-package in awslabs/mcp monorepo, deliberately packaged small (3 runtime deps). This artifact breaks the "every sub-package is a server" assumption — it is infrastructure for building servers.

## Server runtime

### Python with hand-rolled MCP

Python `>=3.10`. No dependency on the official `mcp` SDK or `fastmcp` — the protocol surface is implemented directly against Lambda request/response shapes. The serverless HTTP surface bridges MCP framing onto API Gateway events. Runtime deps: `python-dateutil`, `boto3`, `botocore` only — the smallest trustworthy surface, no Pydantic. Decorator-style ergonomics (`@mcp.tool()`) reproduced atop the custom implementation.

## Transport

### HTTP via API Gateway in front of Lambda

Inherently HTTP — there is no stdio path. The MCP-over-HTTP endpoint (`/mcp`) is exposed as an API Gateway route invoking a Lambda handler. Transport is fixed at deployment time.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools-only — declared via `@mcp.tool()` decorator in the user's Lambda module (the user authors tool functions; this package executes them).

## Configuration delivery

### Environment variables

Lambda environment variables; session-backend choice (NoOp, DynamoDB, or custom class) configured via constructor.

## Authentication

### Upstream-delegated (gateway authorizer)

Authentication delegated to API Gateway + Lambda Authorizer — bearer tokens in `Authorization` header validated upstream of the handler. Application code never sees raw tokens; the authorizer's output reaches the server.

## Multi-tenancy

### Per-request tenancy with externalized session state

Lambda invocations are naturally isolated per-request; pluggable session backend (DynamoDB) keyed by session ID enables persistent state per tenant across requests. NoOp backend is the stateless default; DynamoDB backend the persistent option; custom-backend interface allows others.

## Distribution channel

### PyPI via pip / pipx

PyPI package `awslabs.mcp-lambda-handler`; install for local dev via `pip install -e .[dev]`.

### Lambda deployment package

Embedded as a library dependency inside the user's Lambda deployment package — the artifact ships as part of the consumer's Lambda zip rather than as a standalone server.

## Entry point and launch

### Library import inside a user's handler

No standalone command. Consumer imports `from awslabs.mcp_lambda_handler import MCPLambdaHandler` and writes a Lambda handler that delegates: `def lambda_handler(event, context): return mcp.handle_request(event, context)`. A console script `awslabs.mcp-lambda-handler` mapped to `awslabs.mcp_lambda_handler.server:main` is declared but primary use is library import.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. `requires-python = ">=3.10"`. Version manager convention: pip emphasized for editable install (`pip install -e .[dev]`); `uv` not emphasized.

## Schema and types

### Hand-authored tool schemas

No Pydantic dependency — tool schema strategy likely dataclasses or TypedDict; schemas hand-authored without an SDK to derive them.

### Async model (cross-cutting)

Lambda handlers are typically sync; tool functions likely sync `def`.

## Container artifacts

### No container artifacts

No Dockerfile at this level — Lambda zip is the packaging target.

## Observability

### CloudWatch via Lambda

Implicit CloudWatch logging via the Lambda runtime; X-Ray tracing can layer on. No specific logging framework declared in deps.

## Deployment topology

### Serverless (Lambda + API Gateway)

Server code runs in Lambda fronted by API Gateway. Per-request invocation; cold-start sensitivity; statelessness enforced by the substrate; session state externalized to DynamoDB via the pluggable backend.

## Repository layout

### Server-framework sub-package

Sub-package within the `awslabs/mcp` monorepo that is itself a library for building servers, not a server. Structural category for infrastructure-tier artifacts inside a server-monorepo.

## Extension points

### Middleware module slot

Pluggable session-management abstraction — NoOp (stateless), DynamoDB (persistent), or custom-backend interface implemented by the consumer. Externalizes session state to DynamoDB matching serverless best practice.

## CI

### Monorepo CI inheritance

CI inherited from parent monorepo; no workflow at sub-server level.

## Test stack

### Dev extras gating test deps

Dev extras installable via `pip install -e .[dev]`; specific test framework not extracted.

## Host integration

### No host integration documentation

Not a host-configured server — deployed as Lambda + API Gateway; consumers configure their MCP client to hit the API Gateway URL rather than launching a process.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No Claude Code wrapper — this artifact is infrastructure for building remote MCP servers.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Active development

Default branch `main`; maintained via parent monorepo.
