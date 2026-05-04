# Sample

Pass-1 Phase-1a partial for bin 3. Functional decomposition of awslabs--bedrock-kb-retrieval-mcp-server, awslabs--mcp-lambda-handler, awslabs--mcp, awslabs--openapi-mcp-server, baryhuang--mcp-server-aws-resources-python, bhauman--clojure-mcp, blazickjp--arxiv-mcp-server, chroma-core--chroma-mcp, organized by role with implementation paths as sub-sections.

## Server runtime

The language and framework that runs the MCP protocol message loop. Determines the SDK surface tool authors write against, sync vs async semantics, schema-derivation strategy, and which interpreter has to be present on the deployment host.

### Python with raw `mcp` SDK

Direct use of Anthropic's `mcp` Python SDK without the FastMCP convenience layer. Tool authors interact with the lower-level `mcp.server` API; schema and protocol framing are handled explicitly rather than auto-derived from function signatures. Appropriate when the server has a small, fixed tool surface that doesn't benefit from decorator magic, when dependency minimalism matters (lean dep sets of 3-4 packages observed), or when the SDK was adopted before FastMCP became canonical and the migration cost outweighs the benefit. Frequently pinned exactly (`mcp[cli]==1.6.0`) or floored loosely (`mcp[cli]>=1.23.0`); the `[cli]` extra adds the inspector tooling. Pydantic is pulled in transitively; tool input schemas auto-derive from signatures via the SDK's idiom.

### Python with FastMCP

Decorator-driven framework on top of the raw SDK. `@mcp.tool()` declarations turn ordinary Python functions into MCP tools with schemas auto-derived from type hints. Appropriate when the server has many tools or expects to grow them, when authors want async-throughout semantics by default, and when the FastMCP-specific log-level convention (`FASTMCP_LOG_LEVEL`) is acceptable as part of the operational surface. Version pinning observed at FastMCP 2.x or 3.x (`fastmcp>=3.0.1`, `fastmcp>=3.2.2,<4`) — caret-pinned upper bounds on major versions appear in stricter projects.

### Python custom protocol implementation

Hand-rolled MCP wire-format handling without depending on either `mcp` or `fastmcp` as a runtime package. Appropriate when the deployment substrate (e.g., AWS Lambda + API Gateway events) doesn't fit the SDK's process-loop assumptions, when the dependency footprint must be minimal (3-package surface observed: `python-dateutil`, `boto3`, `botocore`), or when protocol framing is bridged onto a different request/response shape (HTTP event JSON rather than stdio JSON-RPC). Constrains the server to re-implement message framing, capability negotiation, and tool dispatch independently; trades SDK reuse for substrate fit. Decorator-style ergonomics (`@mcp.tool()`) can be reproduced atop the custom implementation.

### Clojure with nREPL bridge

Clojure JVM runtime exposing MCP tool calls as nREPL evaluations. The MCP protocol is bridged onto a REPL connection rather than a process-IO transport — tool invocations become forms evaluated in the running REPL. Appropriate when the target ecosystem (Clojure, ClojureScript via Shadow-cljs, Babashka, Basilisp, Scittle) is itself REPL-driven and structure-aware editing requires live access to a running runtime. Constrains the user to start an nREPL process and keep it co-resident; opens the door to multi-environment detection and switching between REPL flavors at runtime.

## Transport

How protocol messages travel between host and server. Drives single-tenant vs multi-tenant capacity, deployment shape (process vs HTTP service), and which authentication mechanisms are even applicable.

### stdio

Process spawned by the host; JSON-RPC framed over stdin/stdout. Default and most common path. Implies single-tenant per process (one user's session per spawned server), local deployment (host launches the binary), and no in-protocol auth (the host's process boundary is the trust boundary; servers inherit credentials from the host's environment). Appropriate when the server is invoked locally, configuration is static for the session, and the server has no multi-user obligations. Configurability is generally none — the SDK defaults handle it and there is no transport selection in user-facing config.

### HTTP via API Gateway in front of Lambda

The MCP-over-HTTP endpoint is exposed as an API Gateway route that invokes a Lambda handler implementing the protocol. Inherently HTTP, no stdio path. Appropriate when the server must be reachable by remote clients, when serverless cost/scale economics fit the workload, and when authentication can be delegated upstream to API Gateway authorizers. Constrains the server to per-request statelessness (sessions externalized) and Lambda response-size limits (streaming responses become a concern).

### nREPL connection

JSON-RPC layered over an nREPL session rather than process IO. The MCP server is itself driven through the REPL protocol. Appropriate only when the target language ecosystem already centers on nREPL; constrains every user to start a REPL.

### SSE (removed) and Streamable HTTP (planned)

Observed as a deliberate transport-narrowing signal: SSE was supported and then removed on a dated boundary, with a future Streamable HTTP path announced as the planned replacement. Appropriate for projects following upstream MCP transport evolution; carries the ongoing maintenance cost of tracking the spec.

## Capability surface

The pattern by which the server exposes work to the LLM — what the LLM sees and how operations are described.

### Hand-authored fixed tool set

Each tool is written as a Python (or Clojure) function with explicit name, schema, and implementation. Tool count typically under 20 per server. Appropriate when the API surface is small and stable, when descriptions can be tuned for LLM clarity, and when implementation detail matters per-tool. Examples in this bin span 6 tools (arXiv search/download/read/list/semantic/citation), 12 tools (Chroma collection + document CRUD), and bundled tool sets per AWS service.

### Spec-driven dynamic tool generation

Tools, resources, and prompts materialize at server start from one or more parsed OpenAPI specs. No hand-authored tool definitions; the spec is the source of truth. GET-with-query-params is mapped to MCP tools (LLMs handle parameterized search better as tools than resources); other GETs become resources; mutating operations become tools. Auto-enriched descriptions (response codes, parameter examples) materially reduce token cost vs naive rendering. Appropriate when the upstream API has well-maintained OpenAPI documentation and when the server is meant to front a moving target without per-version code changes. Constrains LLM behavior to whatever description quality the OpenAPI fields carry; every spec change is a contract change for the agent.

### Single code-execution tool with sandbox

A single tool accepts a code string (e.g., a `boto3` Python snippet) and executes it server-side under an AST validator + import allowlist. Replaces N hand-enumerated per-API tools with one flexible primitive. Appropriate when the underlying SDK is too large to enumerate, when LLM agility (composing API calls in one call) matters more than tool-level discoverability, and when the sandboxing mechanism is trustworthy enough for the deployment context. Constrains the security surface to the sandbox quality.

### Massive tool catalog with category grouping

50+ tools spanning read-only file ops, code evaluation, structure-aware editing, shell execution, and agent-based analysis. Appropriate when the server is positioned as a comprehensive ecosystem assistant rather than a single-API bridge. Demands strong filtering controls (profile selection, tool include/exclude flags) so callers can scope what surfaces.

### Bundled prompts alongside tools

MCP prompts are shipped as a first-class artifact rather than only tools. Examples include research-workflow prompts (literature review, analysis) and operation-specific prompts auto-generated per OpenAPI operation. Appropriate when the server's domain has well-known recurring workflows that benefit from canonical prompt scaffolding; uses the MCP prompts primitive more deeply than tool-only servers.

### Bundled "agent SOPs" alongside tools

Pre-built structured operating procedures shipped with the server, separate from raw tools — opinionated workflows that compose underlying tool calls. Appropriate when the server author wants to ship not just API access but a curated operational layer on top.

## Configuration delivery

How runtime parameters reach the server process.

### Environment variables

Configuration via env vars set by the host's `env` block in the MCP client config (Claude Desktop, Cursor, etc.). Common conventions include `AWS_PROFILE`, `AWS_REGION`, `FASTMCP_LOG_LEVEL`, and provider-prefixed patterns like `CHROMA_<PROVIDER>_API_KEY` that give uniform surfaces across embedding back-ends. Appropriate when the host config already exposes an env block and when secrets must not appear in argv. Common with stdio transports because the launching host owns the environment.

### CLI arguments

Configuration via flags on the command line set in the host's `args` block. Examples include `--storage-path`, `--client-type ephemeral|persistent|http|cloud`, `--api-name`, `--spec-url`, `--additional-specs`, `--include-tags`, `--exclude-tags`. Appropriate when configuration is structurally part of the server's identity (which spec to mount, which backing store to use) and when the user expects to run multiple differently-configured instances side by side.

### `.env` file

Optional file referenced via `--dotenv-path`, layered on top of env-var resolution. Appropriate when secrets are managed via dotfile conventions and the user wants to decouple host config from credential material.

### Project-local config file

Project-relative file (e.g., `.clojure-mcp/config.edn`) carrying typed configuration in the language's native data format. Appropriate when configuration is workspace-scoped and relatively rich (tool filters, profile selection, formatting preferences), and when the language already has a canonical data-format convention.

### Mounted credential file

Host's credential file (e.g., `~/.aws/credentials`) bind-mounted into a container so the server inherits the user's existing credential context without re-encoding it. Appropriate when the credential format is established and the user already manages it externally.

## Authentication

Where the trust boundary sits and what proves identity at it.

### AWS credential chain

Standard AWS SDK credential resolution — `AWS_PROFILE`, AWS SSO, instance roles, env credentials, STS session tokens. No MCP-level auth; the SDK chain handles everything. Appropriate when the server is an AWS API bridge and the user already manages AWS credentials. Constrains tenancy to whatever AWS profile/region is active at process launch.

### API key

Provider API keys passed as env vars or CLI args, often using a provider-prefixed convention (`CHROMA_OPENAI_API_KEY`, `CHROMA_COHERE_API_KEY`). Appropriate when the server fronts a SaaS API that authenticates per-call with a static key.

### Per-spec authentication

Each upstream API mounted into the server can carry its own auth config (Basic, Bearer, API key in header/query/cookie, AWS Cognito). Appropriate when the server composes many APIs and each has its own credential context.

### Upstream-delegated (API Gateway authorizer)

Authentication happens before the request reaches the server — a Lambda authorizer validates bearer tokens in the `Authorization` header and the application code never sees raw credentials. Appropriate when the deployment substrate has its own auth tier and re-implementing it inside the server adds no value.

### None

No auth layer; the server speaks to a public API or trusts the host's process boundary. Appropriate for public-data servers (e.g., arXiv search) that enforce only client-side rate limits, and for stdio servers where the host launching the process is the trust boundary.

### Optional external LLM API keys

Server is locally trusted but optionally calls out to external LLMs (Anthropic, OpenAI, Google Gemini) for agent-augmented tools; those keys come from env vars when present. Appropriate when the server's core function works without LLM access but optional features benefit from it.

## Multi-tenancy and resource scoping

How the server divides work and resources between callers or contexts.

### Single-user per process

One credential context, one workspace, no in-protocol tenancy. Appropriate for stdio servers where the host launches one process per user session. The dominant pattern.

### Per-request tenancy with externalized session state

Each request carries its own tenant identity; persistent session state is held in an external store (e.g., DynamoDB) keyed by session ID. Appropriate for HTTP/serverless deployments where the process is shared across users and statelessness is enforced by the substrate.

### Tag-based resource scoping

Server-side filtering of which upstream resources are visible based on a tagging convention (e.g., AWS resource tag `mcp-multirag-kb=true`, overridable via env var). Tag enforcement happens at the server, not in LLM prompts. Appropriate when the upstream account contains many resources and the user wants to limit MCP visibility without building app-level access control. Treats infrastructure tagging as the access-control boundary.

### Multi-spec composition

Single server fronts multiple upstream APIs concurrently; each spec has its own HTTP client and auth. Appropriate when the server is positioned as a gateway between one MCP host and many SaaS APIs.

### Mode-switched backing store

Single binary supports multiple backing-store targets (in-memory ephemeral, durable local, remote self-hosted, SaaS) chosen at launch via flags. Appropriate when the same protocol surface should adapt to radically different deployment economics without forking the server. Replaces "multiple servers per backend" with "one server, mode flag."

### Capability probing and conditional surfacing

Optional capabilities (e.g., reranking) only surface when probed-at-start checks pass — the right region is configured and the IAM identity has the necessary permissions. Replaces tool-call-time failure with start-time exclusion. Appropriate when capabilities are credential- or region-conditional and users benefit from never seeing what won't work.

## Distribution channel

How the server reaches the user's machine for installation.

### PyPI via uvx

Published Python package invoked via `uvx <package>@latest` or `uv tool install <package>`. Host config typically has `"command": "uvx"`, `"args": ["<package>@latest"]`. The `uv tool install` form persists the binary in the user's tool dir; `uvx` form fetches per-invocation. Appropriate for Python servers; requires `uv` on the user's system. Frequently the canonical README install path.

### PyPI via pip

Standard pip install (`pip install <package>` or `pip install '<package>[extra]'`). Appropriate when the user prefers traditional Python install conventions or when the server requires editable installs (`pip install -e .[dev]`). Optional extras (e.g., `[yaml]`, `[prometheus]`, `[all]`, `[pdf]`) gate heavier dependencies behind explicit user opt-in.

### Docker image

Image built from in-tree Dockerfile; users pull and run via `docker run` with env injection or volume mounts. Multi-arch publication (linux/amd64, arm64, arm/v7) extends platform reach. Appropriate when the deployment must be language-runtime-independent or when the server has heavy native dependencies. Frequently shipped alongside PyPI as an alternative.

### Smithery CLI

`npx -y @smithery/cli install <name> --client claude` — registry-mediated install for MCP servers. Appropriate when the author wants to be discoverable through the Smithery catalog and benefit from its host-config wiring.

### Source clone with uv

Git clone + `uv` build for users who want to run from source. Appropriate as a fallback when no canonical package is published or when the user is contributing.

### Lambda deployment package

Server packaged as a Lambda deployment artifact (zip), included as a library dependency in a user's Lambda package. Appropriate for the serverless-MCP framework pattern where users deploy their own infrastructure.

### Language-native installer

Language-specific tool installer for non-Python ecosystems (e.g., `clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`). Appropriate when the language has its own canonical distribution mechanism that users in that ecosystem already understand.

### Per-host one-click install URL

URL-protocol install button shown in README per host (Kiro, Cursor, VS Code, Windsurf, Cline, Claude Code). Bypasses JSON copy-paste entirely for supported hosts. Appropriate as a primary-surface ergonomic when many hosts need to be supported and the author is willing to encode per-host install URLs.

### Windows .exe

Windows-specific binary launcher (e.g., `uv tool run --from <package> <package>.exe`). Appropriate when Windows users need an executable form distinct from the POSIX entry point.

## Entry point

What command the user (or host) actually invokes to launch the server.

### Console script via `[project.scripts]`

Python package declares `[project.scripts]` mapping a name to `module:main`. The script becomes available on PATH after install. Common names follow the package name (`arxiv-mcp-server`, `chroma-mcp`, `awslabs.<service>-mcp-server`). Quoted dotted names (`"awslabs.aws-api-mcp-server" = "awslabs.aws_api_mcp_server.server:main"`) are valid pyproject syntax and let dotted PyPI names match dotted console-script names.

### Bare module script

User runs the source file directly (`src/<name>/server.py`). Appropriate for Docker-first servers where the entry point is the container's CMD rather than a distributed binary.

### Library import inside a user's handler

No standalone command; the package is imported into a user-authored Lambda handler that delegates to it (`mcp.handle_request(event, context)`). Appropriate when the artifact is infrastructure for building servers rather than a server itself.

### Language-tool launcher

Language-native command (e.g., `clojure -Tmcp start`, `clojure-mcp-light` profile). Appropriate when the language toolchain provides the launcher idiom users in that ecosystem expect.

### Containerized entry

`docker run` is the canonical launch; the host config has `"command": "docker"`, `"args": [...]`. Appropriate when Docker is the primary distribution and the in-container CMD wraps the actual server invocation.

## Observability

What the server emits about its operation and how it's collected.

### loguru

Python `loguru` library used for application logging. Appropriate when the server wants log formatting and rotation without configuring stdlib logging by hand. Common in awslabs-pattern servers.

### MCP SDK stderr logging

Default logging path provided by the MCP SDK; messages appear on stderr where the host can capture them. Configurable level via `FASTMCP_LOG_LEVEL` env var when FastMCP is in use.

### CloudWatch via Lambda

Implicit logging to CloudWatch Logs because the server runs in Lambda; X-Ray tracing can layer on. Appropriate when the deployment substrate provides a logging tier the server inherits for free.

### CloudTrail audit logging

Audit-tier logging (who called what tool when) captured in CloudTrail rather than application logs. Appropriate when the server's calls have compliance significance and a separate audit trail matters.

### Prometheus metrics

Optional metrics endpoint enabled via an install extra (`[prometheus]`). Appropriate when the server is deployed in an observable infrastructure that already scrapes Prometheus metrics; gated behind an extra to avoid imposing on users who don't need it.

### JSON-RPC notifications for capability changes

Server emits MCP-protocol notifications when tool/resource availability changes at runtime, plus startup logs of connection details and tool initialization. Appropriate when capabilities are dynamic (e.g., REPL state changes which tools are valid) and the host needs to refresh its view.

## Host integration

Which MCP-consuming hosts the server documents direct support for.

### Claude Desktop

JSON `mcpServers` config snippet in `claude_desktop_config.json`, typically showing a `uvx` or `docker run` invocation with env block. Universal floor for sample servers; nearly every server documents at least this integration.

### Claude Code

Either explicit one-click install button, a sibling `skills/` directory shipping Claude Code skills alongside the MCP server, or no first-class wrapper (host expected to consume the generic MCP surface).

### Codex

`.codex-plugin/` integration manifest in repo root — first-class plugin shape distinct from the MCP server itself. Appropriate when the author wants to ship Codex-native ergonomics rather than relying on Codex's generic MCP consumption.

### Cursor / VS Code / Windsurf / Cline / Kiro

One-click install buttons in README; integration is via URL-protocol deep links rather than copy-pasted JSON.

### Smithery registry

Server entry in the Smithery catalog; install via `@smithery/cli install <name> --client <host>`. Cross-host distribution mechanism rather than a single-host integration.

### nREPL host

The host is itself a running REPL process; the server connects to it. Native to the Clojure ecosystem.

## Container and packaging artifact

What gets built and shipped when distribution is Docker or Lambda.

### Single-stage Dockerfile

Per-server Dockerfile in the repo, used both as a build artifact (image published to a registry) and as a run-time configuration target. Common across awslabs sub-servers and many third-party servers.

### Multi-architecture image publishing

Docker images published for linux/amd64, arm64, and arm/v7. Appropriate when the user base spans Apple Silicon, Linux x86, and lower-power ARM devices.

### Lambda zip

Server packaged as a Lambda deployment artifact rather than a container. Appropriate for the serverless deployment model where API Gateway is the front door.

### Devcontainer for contributors

`.devcontainer/` configuration at repo root provides a reproducible contributor environment. Appropriate for monorepos and projects with non-trivial developer setup.

## Test stack

How the project verifies its own behavior.

### pytest with pytest-asyncio and pytest-cov

Python test suite using pytest with async support and coverage tracking. `asyncio_mode = "auto"` removes the per-test marker burden. Custom markers (`live`) gate tests that hit real APIs. Standard discovery (`python_files = "test_*.py"`, `python_classes = "Test*"`, `testpaths = ["tests"]`).

### Codecov badge integration

Coverage tracked across the repo with a Codecov badge. Appropriate when contributors should see coverage trend and gates can fail PRs that drop coverage.

### Clojure-native testing

Test directory with typical Clojure testing conventions. Appropriate when the project lives in the Clojure ecosystem and follows its idioms.

### Dev extras gating test deps

Test dependencies installed via `pip install -e .[dev]` (or equivalent extra). Keeps the runtime install lean.

## CI

How automated checks run on pushes and PRs.

### GitHub Actions

`.github/workflows/` with at least a tests workflow and badge. Common across nearly every sample. Per-server projects in monorepos may share workflows at root; standalone projects have their own.

### Pre-commit hooks

`.pre-commit-config.yaml` runs local checks (lint, format, secret scan) before commit. Appropriate for monorepos where consistency across many sub-packages must be enforced.

### Ruff lint config

`.ruff.toml` at root configures the Ruff linter as the project's lint authority. Common in modern Python projects.

### Secret-scan baseline

`.secrets.baseline` records known-allowed strings so the scanner doesn't flag them. Appropriate when secret-scanning is part of CI and false positives need a managed allow list.

### OSSF Scorecard

OSSF Scorecard integration emits a security posture rating. Appropriate for projects that want a public security score visible to consumers.

## Repository layout

How the server's source is organized relative to other artifacts in the same repo.

### Single-package layout

One Python package under `src/<name>/` with one `pyproject.toml`. Appropriate for a focused server with no companion artifacts.

### Monorepo of namespace-prefixed packages

Many sub-packages under `src/<name>/` each with their own `pyproject.toml`, all sharing a namespace prefix (e.g., `awslabs.*`). Central dev tooling at root (ruff, pre-commit, secrets baseline). Each sub-package is independently published and installable. Appropriate when one organization ships many related servers and wants consistent tooling without combining them into one package.

### Single-package plus sibling host integrations

Core MCP server in `src/<name>/` plus sibling directories shipping integrations for non-MCP hosts (`.codex-plugin/`, `skills/` for Claude Code). Appropriate when the author wants to ship native plugin formats for multiple ecosystems from one repo rather than relying on generic MCP consumption.

### Server-framework sub-package

Sub-package within an MCP-server monorepo that is itself a library for building servers, not a server. Breaks the "every sub-package is a server" assumption of the monorepo and represents a structural category for infrastructure-tier artifacts.

### Clojure project layout

Standard Clojure layout with `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, plus extensive root-level documentation files (README, PROJECT_SUMMARY, CHANGELOG, CONFIG, FAQ, BIG_IDEAS, LLM_CODE_STYLE).

## Deployment / execution model

The runtime substrate the server is designed to run inside.

### Local process spawned by host

Host process launches the server as a child process, communicates over stdio, and tears it down when the session ends. Default model for stdio servers.

### Containerized local process

Host launches `docker run` as the server command; the container is a transparent execution wrapper around the same stdio loop. Appropriate when language runtimes can't be assumed on the host or when bundled native deps make installation painful.

### Serverless (Lambda + API Gateway)

Server code runs in Lambda, fronted by an HTTPS API Gateway endpoint. Per-request invocation; cold-start sensitivity; statelessness enforced by the substrate; session state externalized to DynamoDB. Appropriate when the server must be reachable by remote clients and serverless economics fit the workload.

### REPL-resident

Server code runs inside a long-lived REPL process; the host connects to the REPL. Appropriate only when the target ecosystem (Clojure / nREPL) already has REPL-driven development as the dominant idiom.

## Build and packaging tooling

How the source becomes an installable artifact.

### hatchling backend

`build-backend = "hatchling.build"` in `pyproject.toml`. The most common Python build backend in this bin.

### uv as Python project manager

Project uses `uv` for environment, install, and lock management. `uv.lock` committed; `.python-version` likely. Per-sub-package uv projects in monorepo layouts.

### Clojure deps.edn with tools

`deps.edn` for dependency management plus `clojure -Ttools` for tool installation and invocation. Standard Clojure project structure.

## Sandboxing

How the server constrains what code can do when it executes user-influenced operations.

### AST validation with import allowlist

User-supplied Python code is parsed to AST, validated against an explicit allowlist of permitted imports (`boto3`, `operator`, `json`, `datetime`, `pytz`, `dateutil`, `re`, `time`), and only then executed. Appropriate for code-as-tool architectures where the LLM authors small snippets server-side. Trust depends entirely on the allowlist's tightness.

### No sandboxing (trusted code path)

Server code runs whatever the developer wrote; user inputs are parameters, not code. Default for the hand-authored fixed tool set pattern.

## Versioning signals

How the project communicates change to consumers.

### Dated deprecation in repo

Removal events (e.g., SSE removal on 2025-05-26) documented in-repo with dates rather than buried in changelogs. Appropriate when transport or capability changes have material impact on consumers and signaling them clearly is part of the maintenance contract.

### Automated-release sentinel version

Version field in `pyproject.toml` carrying a bot-generated value (observed: `0.9223372036854775807.9223372036854775807`, int64-max sentinel) rather than a human-chosen number. Suggests the canonical version comes from a release pipeline, not the source file.

### Tagged release with version in changelog

Standard semver tag (e.g., `v0.3.1`, `v0.2.6`) with a changelog entry. The default expectation.

## Documentation surface

What the project ships beyond code to help users and contributors.

### Per-host README integration sections

README has labeled sections per supported host (Claude Desktop, Cursor, Codex, etc.) showing the canonical config snippet for each. Common where the server targets multiple host ecosystems.

### Multi-document deep documentation

Beyond README, the project ships PROJECT_SUMMARY, CONFIG, FAQ, BIG_IDEAS, LLM_CODE_STYLE, and similar long-form documentation. Appropriate for projects with substantial conceptual surface (50+ tools, multi-environment support) where a single README cannot cover everything.

### LLM-style guidance file

Documentation specifically aimed at LLM assistants editing the codebase (e.g., `LLM_CODE_STYLE.md`). Appropriate when contributors include AI assistants and the project wants to influence their code style.

### Token-cost annotations

README quantifies token impact of design choices (e.g., 70-75% token reduction from description enrichment in OpenAPI tool generation). Appropriate when token cost is part of the user's purchase decision.
