# Sample

Pass-1 Phase-1a partial for bin 3. Atomic knowledge chunks from assigned samples (awslabs--bedrock-kb-retrieval-mcp-server, awslabs--mcp-lambda-handler, awslabs--mcp, awslabs--openapi-mcp-server, baryhuang--mcp-server-aws-resources-python, bhauman--clojure-mcp, blazickjp--arxiv-mcp-server, chroma-core--chroma-mcp), organized by divergence axes. Phase-1b merger will unify with other partials.

## Artifact category

The corpus is not uniform — beyond "an MCP server", the bin surfaces variants worth distinguishing.

### Single-purpose MCP server

The default shape — one server fronting one domain. Examples: [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`baryhuang--mcp-server-aws-resources-python`].

### Server-framework (library, not server)

[`awslabs--mcp-lambda-handler`] is a library for *building* Lambda-hosted MCP servers, not itself an MCP server. Re-implements MCP wire format on Lambda events; the user writes their own server using its `@mcp.tool()` decorator and `mcp.handle_request(event, context)` dispatch. Reveals a structural category the per-server schema does not anticipate.

### Spec-driven server (tools materialize from external schema)

[`awslabs--openapi-mcp-server`] generates tools, resources, and prompts at server start by parsing one or more OpenAPI specs. No hand-authored tool definitions. Major design axis vs. code-driven servers — implications for docs drift (spec is source of truth), testing (every spec change is a contract change), and LLM behavior (tool descriptions inherit spec quality).

### Code-as-tool server (one tool wraps an interpreter)

[`baryhuang--mcp-server-aws-resources-python`] exposes a single `exec boto3` tool with AST-validation sandbox + import allowlist (boto3, operator, json, datetime, pytz, dateutil, re, time). Inverts the per-API enumeration default — one flexible code-execution tool versus N hand-enumerated tools.

### Multi-server monorepo (umbrella)

[`awslabs--mcp`] is a 40+ server monorepo with `src/<service>/` per server, namespace-prefixed PyPI packages (`awslabs.<service>-mcp-server`), and central dev tooling at root. A preview "aggregated" server (`aws-mcp-server`) bundles SOPs + CloudTrail audit, suggesting a future where per-service servers become composable primitives under a curated orchestrator.

## Language and runtime

### Python

The bin's dominant language: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`].

#### Version floor

- `>=3.10` — [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`chroma-core--chroma-mcp`]
- `>=3.11` — [`blazickjp--arxiv-mcp-server`] (higher than typical; suggests use of newer typing / exception-group features)
- Not surfaced — [`baryhuang--mcp-server-aws-resources-python`]

### Clojure / JVM

[`bhauman--clojure-mcp`] runs on JDK 17+ (inferred), Clojure 99.9% of source. Distributed as a Clojure tools install (`clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp`) — a non-Python distribution path entirely.

## SDK / framework variant

The Python ecosystem splits along "raw `mcp`", "FastMCP", or "custom (no SDK)".

### raw `mcp` SDK

- `mcp[cli]>=1.23.0` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `mcp[cli]==1.6.0` (exact pin) — [`chroma-core--chroma-mcp`]
- `mcp` (raw, version not surfaced) — [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`]

Notable: [`chroma-core--chroma-mcp`] pins exactly `==1.6.0`, an unusually tight pin for a 2025 vendor server (most vendor servers have migrated to FastMCP).

### FastMCP

- `fastmcp>=3.2.2,<4` — [`awslabs--openapi-mcp-server`]
- Dual `mcp>=1.23.0` AND `fastmcp>=3.0.1` — [`awslabs--mcp`] (sampled `aws-api-mcp-server/pyproject.toml`)
- Inferred via `FASTMCP_LOG_LEVEL` env-var convention — [`awslabs--mcp`]

### Custom (no MCP SDK)

[`awslabs--mcp-lambda-handler`] depends on neither `mcp` nor `fastmcp` — re-implements protocol wire format directly against Lambda events. Smallest dependency footprint of any awslabs sub-server (3 deps: python-dateutil, boto3, botocore).

### Non-Python protocols

[`bhauman--clojure-mcp`] uses Anthropic's MCP plus nREPL for REPL-driven evaluation transport — JSON-RPC framing inside an nREPL connection.

## Transport

### stdio

Dominant in this bin: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`].

[`awslabs--mcp`] explicitly notes SSE was removed on 2025-05-26; "Streamable HTTP" planned replacement is in-development. Wholesale SSE removal with a documented date — deliberate transport-narrowing rather than maintaining both during transition.

### HTTP (API Gateway → Lambda)

[`awslabs--mcp-lambda-handler`] — inherently HTTP, no stdio path. The MCP-over-HTTP endpoint (`/mcp`) is an API Gateway route.

### nREPL (REPL-as-transport)

[`bhauman--clojure-mcp`] — JSON-RPC inside nREPL connection. REPL-as-transport is unusual for MCP; entry point selection at launch lets the same artifact serve CLI, Claude Desktop, or other MCP clients with environment-specific connection patterns.

### Configurable client mode (not transport per se, but launch-time runtime selection)

[`chroma-core--chroma-mcp`] — single binary picks ephemeral / persistent / http / cloud backing store via CLI flags / env at launch. Not transport switching, but a parallel "one binary, many runtime modes" axis.

## Distribution

### PyPI + uvx

The dominant Python install path: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`].

- `uvx awslabs.bedrock-kb-retrieval-mcp-server@latest` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `uv tool install arxiv-mcp-server` — [`blazickjp--arxiv-mcp-server`]
- `uvx chroma-mcp` — [`chroma-core--chroma-mcp`]

### PyPI via pip

[`awslabs--openapi-mcp-server`] uses `pip install` with extras (`[yaml]`, `[prometheus]`, `[all]`). Exception to the uvx convention; CLI args are heavy (`--api-name`, `--api-url`, `--spec-url`) so `pip install` + direct invocation makes sense.

[`awslabs--mcp-lambda-handler`] uses `pip install -e .[dev]` (library, not invoked standalone).

### Docker

Most samples ship Dockerfiles: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`].

Multi-arch Docker images (linux/amd64, arm64, arm/v7) — [`baryhuang--mcp-server-aws-resources-python`]; broader platform coverage including arm/v7 is unusual.

### Smithery CLI

[`baryhuang--mcp-server-aws-resources-python`] — `npx -y @smithery/cli install mcp-server-aws-resources-python --client claude`. A distribution vector alongside Docker and source.

### Windows .exe

[`awslabs--bedrock-kb-retrieval-mcp-server`] — `uv tool run --from awslabs.bedrock-kb-retrieval-mcp-server@latest awslabs.bedrock-kb-retrieval-mcp-server.exe`.

### Optional install extras

- `[pdf]` — [`blazickjp--arxiv-mcp-server`]: separates core arXiv client from heavier PDF processing deps
- `[yaml]`, `[prometheus]`, `[all]` — [`awslabs--openapi-mcp-server`]
- `[sentence-transformers]` — [`chroma-core--chroma-mcp`]: locally-embedded collections without OpenAI/Cohere/Voyage keys

### JVM tools-installer

[`bhauman--clojure-mcp`] — `clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`. Non-Python install path.

## Naming convention

### Namespace-prefixed PyPI

[`awslabs--mcp`] uses `awslabs.<service>-mcp-server` — prevents collision with other AWS-adjacent packages and makes provenance scannable from the package name alone. Quoted dotted console-script name (`"awslabs.aws-api-mcp-server" = "awslabs.aws_api_mcp_server.server:main"`) is valid pyproject syntax but rare; enables a dotted console-script name to match the PyPI package name.

### Plain package name

`chroma-mcp`, `arxiv-mcp-server`, `mcp-server-aws-resources` — typical short slug convention.

## Configuration surface

### Env vars (primary)

- AWS credentials chain — [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`]
- `KB_INCLUSION_TAG_KEY` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `FASTMCP_LOG_LEVEL` — [`awslabs--mcp`]
- `BEDROCK_KB_RERANKING_ENABLED` (per-service) — [`awslabs--mcp`]
- `ARXIV_STORAGE_PATH` — [`blazickjp--arxiv-mcp-server`]
- `CHROMA_<PROVIDER>_API_KEY` provider-prefixed convention — [`chroma-core--chroma-mcp`]

### CLI args

- `--api-name`, `--api-url`, `--spec-url`, `--additional-specs`, `--include-tags`, `--exclude-tags` — [`awslabs--openapi-mcp-server`]
- `--storage-path` — [`blazickjp--arxiv-mcp-server`]
- Backend-mode flags — [`chroma-core--chroma-mcp`] (`--client-type ephemeral|persistent|http|cloud`)
- `--dotenv-path` for `.env` — [`chroma-core--chroma-mcp`]

### Project file (declarative)

[`bhauman--clojure-mcp`] — `.clojure-mcp/config.edn` with Clojure map structure; CLI overrides for tool filtering, profile selection, nREPL parameters.

### Lambda env (deployment-bound)

[`awslabs--mcp-lambda-handler`] — Lambda environment variables; session backend selected (NoOp / DynamoDB / custom class) at construction.

## Authentication

### AWS credential chain

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`] — `AWS_PROFILE`, AWS SSO, instance roles, env credentials, STS session tokens. No MCP-level auth layer; standard AWS resolution.

### API key

- Provider-prefixed (`CHROMA_OPENAI_API_KEY` etc.) — [`chroma-core--chroma-mcp`]
- For Chroma Cloud and embedding providers — [`chroma-core--chroma-mcp`]
- Optional API keys for external LLM providers (Anthropic, OpenAI, Google Gemini) for *agent tools*, not server auth — [`bhauman--clojure-mcp`]

### None / public

- arXiv public API; rate limit enforced locally (3-second minimum) — [`blazickjp--arxiv-mcp-server`]
- No built-in authentication — [`bhauman--clojure-mcp`]

### Per-API auth (multi-spec)

[`awslabs--openapi-mcp-server`] — Basic, Bearer Token, API Key (header/query/cookie), AWS Cognito; each mounted spec has its own credential context. Auth as per-spec, not per-server, supports "one gateway to many SaaS APIs" use case.

### Infrastructure-delegated auth

[`awslabs--mcp-lambda-handler`] — bearer tokens validated by API Gateway Lambda Authorizer upstream; the application never sees raw tokens. Authentication is architecturally outside the server, not inside.

## Multi-tenancy

### Single-user per process

Common shape: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`].

### Tag-driven scoping (server-enforced)

[`awslabs--bedrock-kb-retrieval-mcp-server`] — knowledge bases tagged `mcp-multirag-kb=true` (overridable via `KB_INCLUSION_TAG_KEY`) are surfaced; AWS tag filters are the access-control boundary, enforced server-side, not by the LLM. A novel solution to "too many resources in the account" without building app-level access control.

### Per-request (serverless)

[`awslabs--mcp-lambda-handler`] — Lambda invocations naturally isolated; DynamoDB session backend keyed by session ID for persistent state per tenant across requests. Pluggable session management (NoOp / DynamoDB / custom).

### Per-spec composition

[`awslabs--openapi-mcp-server`] — `--additional-specs` mounts multiple OpenAPI specs in one server, each with its own HTTP client and auth context.

## Capabilities exposed

### Tools

- Knowledge-base discovery, data-source listing, NL KB querying, result filtering, conditional reranking — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- Per-service tools per AWS service — [`awslabs--mcp`]
- Dynamically generated tools from OpenAPI ops — [`awslabs--openapi-mcp-server`]
- Single `exec boto3` tool — [`baryhuang--mcp-server-aws-resources-python`]
- 50+ tools across read-only file ops, code evaluation, structure-aware editing, shell execution, agent-based analysis — [`bhauman--clojure-mcp`]
- 6 tools (search, download, read, list, semantic search, citation graph) — [`blazickjp--arxiv-mcp-server`]
- 12 tools (collection CRUD, document ops, retrieval) — [`chroma-core--chroma-mcp`]
- Tools via `@mcp.tool()` decorator (user-authored) — [`awslabs--mcp-lambda-handler`]

### Resources

- Dynamic AWS-resources resource — [`baryhuang--mcp-server-aws-resources-python`]
- GETs other than parameterized search — [`awslabs--openapi-mcp-server`]

### Prompts

- Research analysis and literature review workflow prompts — [`blazickjp--arxiv-mcp-server`]
- Operation-specific prompts and API doc prompts auto-generated — [`awslabs--openapi-mcp-server`]
- Pre-built Agent SOPs (preview aggregator) — [`awslabs--mcp`]

### Capability probing / feature gates

- Reranking only exposed when region + IAM perms allow, rather than failing at tool-call time — [`awslabs--bedrock-kb-retrieval-mcp-server`]

## Tool-surface design

### Hand-enumerated per-API tools

Default shape across most samples: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`].

### Spec-generated tools

[`awslabs--openapi-mcp-server`] — tools materialize at server start from parsed OpenAPI spec. GET-with-query-params mapped to *tools* not *resources* — explicit deviation from MCP convention because LLMs use tools better than resources for parameterized search. Tag filtering via `--include-tags` / `--exclude-tags` reduces tool surface at mount time. Auto-enriched tool descriptions with response codes + parameter examples → claimed 70-75% token reduction vs naive rendering.

### Code-as-tool (single sandboxed interpreter)

[`baryhuang--mcp-server-aws-resources-python`] — single tool accepts a Python code string; AST validator + import allowlist (boto3, operator, json, datetime, pytz, dateutil, re, time) is the sandboxing mechanism.

### Decorator-driven (user-authored)

[`awslabs--mcp-lambda-handler`] — familiar FastMCP `@mcp.tool()` pattern but reimplemented on top of Lambda request/response shapes rather than `fastmcp`.

## Schema / type strategy

### Pydantic v2 (auto-derived)

- `pydantic>=2.11.1` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- Pydantic via MCP SDK (auto-derived from signatures) — [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`]
- Pydantic v2 with schemas derived from OpenAPI specs via `openapi-spec-validator` + `prance` — [`awslabs--openapi-mcp-server`] (the most extreme "schema is data" design in this bin)

### Hand-authored / minimal

- Hand-authored single-tool schema (Python code string as input) — [`baryhuang--mcp-server-aws-resources-python`]

### Stdlib / unspecified

- No Pydantic dependency listed — likely dataclasses or TypedDict — [`awslabs--mcp-lambda-handler`]

## Async vs sync

### Async throughout

- `httpx` + FastMCP 2 — [`awslabs--openapi-mcp-server`]
- pytest-asyncio + `asyncio_mode = "auto"` — [`awslabs--mcp`]
- Likely async (httpx idiom) — [`blazickjp--arxiv-mcp-server`]

### Sync (boto3 idiom)

- boto3 sync by nature — [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`baryhuang--mcp-server-aws-resources-python`]

### Mixed

- pytest-asyncio suggests async coverage but mixed — [`chroma-core--chroma-mcp`]

## Observability

### `loguru`

- [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--openapi-mcp-server`]

### Standard MCP stderr

- [`chroma-core--chroma-mcp`], [`blazickjp--arxiv-mcp-server`]

### `FASTMCP_LOG_LEVEL` env

- [`awslabs--mcp`]

### CloudWatch + X-Ray (Lambda implicit)

- [`awslabs--mcp-lambda-handler`]

### nREPL JSON-RPC notifications

[`bhauman--clojure-mcp`] — notifications signal tool/resource availability changes; server logs nREPL connection details and tool initialization status during startup.

### Optional Prometheus

[`awslabs--openapi-mcp-server`] — via `[prometheus]` extra.

### CloudTrail audit

[`awslabs--mcp`] — preview aggregated server bundles CloudTrail audit logging.

## Host integrations

### One-click install buttons (URL protocol)

[`awslabs--mcp`] surfaces one-click install URLs for: Kiro, Cursor, VS Code, Cline with Amazon Bedrock, Windsurf, Claude Code. Shifts configuration burden from copy-paste JSON to deep links.

### Claude Desktop JSON

- Most samples document a JSON `mcpServers` snippet: [`awslabs--bedrock-kb-retrieval-mcp-server`] (implicit in monorepo), [`baryhuang--mcp-server-aws-resources-python`] (Docker command + env injection or AWS profile mount), [`blazickjp--arxiv-mcp-server`] (uvx command), [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`] (`claude_desktop_config.json` with shell path)

### Codex plugin

[`blazickjp--arxiv-mcp-server`] — `.codex-plugin/` integration manifest in repo root; first-class Codex plugin shape.

### Claude Code skills (in-repo)

[`blazickjp--arxiv-mcp-server`] — `skills/` directory; explicit Claude Code skill wrapper co-located with the MCP server. Ships integration artifacts for three different host ecosystems in one repo: standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`).

### Smithery

[`baryhuang--mcp-server-aws-resources-python`] — registry entry, install via `@smithery/cli`.

### Multi-REPL (Clojure ecosystem)

[`bhauman--clojure-mcp`] — Shadow-cljs (ClojureScript), Babashka, Basilisp, Scittle environment detection and switching. Multi-REPL support is a Clojure-ecosystem-specific axis.

## Tests

### pytest stack

- pytest + pytest-asyncio + pytest-cov + pytest-mock — [`awslabs--mcp`] (per-server config: `python_files = "test_*.py"`, `python_classes = "Test*"`, `testpaths = ["tests"]`)
- pytest ≥8.3.5, pytest-asyncio ≥0.26.0, pytest-cov ≥4.1.0 — [`chroma-core--chroma-mcp`]
- pytest, `tests/` directory — [`blazickjp--arxiv-mcp-server`]

### Custom marker

[`awslabs--mcp`] — custom `live` marker for API-calling tests.

### Dev extras

[`awslabs--mcp-lambda-handler`] — `pip install -e .[dev]`; framework not extracted.

### Native test framework

[`bhauman--clojure-mcp`] — typical Clojure testing patterns; `test/` directory.

### Not surfaced

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`].

## CI

### GitHub Actions

- Workflows + `tests.yml` with badge — [`blazickjp--arxiv-mcp-server`]
- `.github/workflows/` — [`chroma-core--chroma-mcp`], [`baryhuang--mcp-server-aws-resources-python`]
- `.github/workflows`, `.ruff.toml`, `.pre-commit-config.yaml`, `.secrets.baseline`, OSSF Scorecard, Codecov badge — [`awslabs--mcp`]
- Configured in `.github/` — [`bhauman--clojure-mcp`]

### Per-server in monorepo

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--openapi-mcp-server`] inherit from the parent monorepo's CI.

## Container / packaging artifacts

### Dockerfile

- [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`] (per server), [`baryhuang--mcp-server-aws-resources-python`] (multi-arch), [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`]

### Lambda zip (no Dockerfile)

[`awslabs--mcp-lambda-handler`] — Lambda is the packaging target.

### Devcontainer

[`awslabs--mcp`] — `.devcontainer/` configuration at root for dev workflow.

## Repo layout

### Single package

- `src/<package_name>/` — [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`]
- Single Clojure package with `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, `docs/` — [`bhauman--clojure-mcp`]

### Sub-package in monorepo

- [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--openapi-mcp-server`] all live under `awslabs/mcp/src/<service>/`.

### Monorepo-of-packages

[`awslabs--mcp`] — 40+ servers, central dev tooling at root with per-server pyproject.toml. Classic uv workspace layout (though `[tool.uv.workspace]` not confirmed).

### Multi-host artifact bundle

[`blazickjp--arxiv-mcp-server`] — single repo bundles standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`).

## Build backend / packaging

### hatchling

- [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`chroma-core--chroma-mcp`]

### Not surfaced

- [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`]

### `uv.lock` committed

- [`blazickjp--arxiv-mcp-server`] — present
- Not confirmed — [`awslabs--mcp`], [`chroma-core--chroma-mcp`], others

### Version manager convention

- `uv` — most Python samples
- pip — [`awslabs--mcp-lambda-handler`] (uv not emphasized)

## Entry point / launch

### Console script (PyPI dotted)

[`awslabs--mcp`] — `"awslabs.aws-api-mcp-server" = "awslabs.aws_api_mcp_server.server:main"` — quoted-name script with dot-in-name; valid pyproject syntax but rare.

### Console script (plain)

- `awslabs.bedrock-kb-retrieval-mcp-server` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `awslabs.openapi-mcp-server` (with positional args) — [`awslabs--openapi-mcp-server`]
- `arxiv-mcp-server` — [`blazickjp--arxiv-mcp-server`]
- `chroma-mcp` — [`chroma-core--chroma-mcp`] (`[project.scripts]` → `chroma_mcp:main`)

### Bare script

[`baryhuang--mcp-server-aws-resources-python`] — `src/mcp_server_aws_resources/server.py` or containerized equivalent.

### Library import (no standalone)

[`awslabs--mcp-lambda-handler`] — `def lambda_handler(event, context): return mcp.handle_request(event, context)`. Console script declared but primary usage is library import.

### Tools-installer launch

[`bhauman--clojure-mcp`] — `clojure -Tmcp start` post-install; profiles like `clojure-mcp-light` for lightweight REPL, `:cli-assist` for full.

## Notable structural choices

### Capability probing at startup

[`awslabs--bedrock-kb-retrieval-mcp-server`] — reranking tool only registered when region + IAM perms allow; capability gate at start, rather than failing at tool-call time.

### Lean dependency footprint

- [`awslabs--bedrock-kb-retrieval-mcp-server`] — 4 runtime deps (boto3, loguru, mcp, pydantic); no httpx (boto3 owns network I/O)
- [`awslabs--mcp-lambda-handler`] — 3 deps (python-dateutil, boto3, botocore); pure-stdlib protocol handling, no Pydantic, no mcp-sdk, no fastmcp

### Heavy / "fat" install

[`chroma-core--chroma-mcp`] — bundles three cloud embedding SDKs (openai, cohere, voyageai) in core deps (not extras); fat install, zero-friction provider switching.

### Auto-release sentinel version

[`awslabs--openapi-mcp-server`] — pyproject.toml version was `0.9223372036854775807.9223372036854775807` (int64 max); looks like an automated-release sentinel, not a human-chosen version.

### Tag-driven resource access control

[`awslabs--bedrock-kb-retrieval-mcp-server`] — AWS tags become the access-control boundary for which KBs the server can see; novel solution to "too many resources in the account" without building app-level access control.

### One binary, many runtime modes

[`chroma-core--chroma-mcp`] — single binary supports 4 backing-store modes (ephemeral, persistent, HTTP self-hosted, Chroma Cloud) selected at launch via flags rather than four separate entry points.

### Multi-spec API gateway pattern

[`awslabs--openapi-mcp-server`] — single server fronts many APIs via `--additional-specs`, each with independent auth and HTTP clients; "one gateway to many SaaS APIs".

### Server-framework distinction

[`awslabs--mcp-lambda-handler`] — sub-package in an MCP-server monorepo that is itself not a server but a library for building servers; reveals a structural category the per-server schema does not anticipate. Session management as a pluggable extension point (NoOp/DynamoDB/custom). Infrastructure-dependent auth (API Gateway Authorizer) — auth is architecturally outside the server.

### REPL-driven paradigm

[`bhauman--clojure-mcp`] — REPL-driven development as primary paradigm (nREPL); 50+ tools targeting Clojure ecosystem needs. Configuration via Clojure maps (deps-like pattern). LLM_CODE_STYLE.md for AI assistant prompt guidance — unusual.

### Built-in client-side rate limit

[`blazickjp--arxiv-mcp-server`] — 3-second minimum rate-limit enforcement at the client layer; reflects arXiv's rate-limit guidance.

### Multi-arch Docker

[`baryhuang--mcp-server-aws-resources-python`] — linux/amd64, arm64, arm/v7; broader platform coverage than typical.

### Documentation-heavy repo

[`bhauman--clojure-mcp`] — README.md (30KB), PROJECT_SUMMARY.md (26KB), CONFIG.md (9KB), FAQ.md (8KB), CHANGELOG, BIG_IDEAS, LLM_CODE_STYLE; substantial for a single-package repo.

## Notable Python-specific dependencies

### `prance` + `openapi-spec-validator`

[`awslabs--openapi-mcp-server`] — OpenAPI parsing; non-trivial deps rarely seen in MCP servers. Validation toggle for non-compliant specs.

### `tenacity`

[`awslabs--openapi-mcp-server`] — retry logic on upstream HTTP calls.

### `cachetools`

[`awslabs--openapi-mcp-server`] — in-process caching of spec/responses.

### `uvicorn` despite stdio transport

[`awslabs--openapi-mcp-server`] — suggests optional HTTP mode or internal HTTP client pool.

### `bcrypt`

[`awslabs--openapi-mcp-server`] — runtime dep; likely Basic Auth credential hashing/storage.

### `python-dateutil` only (besides AWS SDK)

[`awslabs--mcp-lambda-handler`] — suggests time-sensitive session token handling.

### `boto3` outside AWS-specific servers

[`awslabs--openapi-mcp-server`] depends on both `fastmcp` and `boto3` (for Cognito auth) — boto3 used beyond pure AWS-API servers.

### Caret-pinned upper bounds

[`awslabs--openapi-mcp-server`] — `,<4`, `,<1` throughout; stricter compatibility stance than typical Python projects.

### Exact-pin SDK

[`chroma-core--chroma-mcp`] — `mcp[cli]==1.6.0` exact pin; unusually tight for a 2025 vendor server.

## Unanticipated axes / observations

### Multi-host artifact bundling in one repo

[`blazickjp--arxiv-mcp-server`] — one MCP server, three host-native plugin wrappers (MCP `src/`, Codex `.codex-plugin/`, Claude Code `skills/`). Each host ecosystem gets dedicated sibling integrations rather than expecting hosts to generically consume the MCP surface.

### Token-cost awareness as first-class concern

[`awslabs--openapi-mcp-server`] — README quantifies token reduction (claimed 70-75%) from auto-enriched tool descriptions.

### Deprecation as a versioning signal

[`awslabs--mcp`] — SSE removal dated and documented in-repo (2025-05-26) rather than only in a changelog.

### Agent SOPs as a first-class shipped artifact

[`awslabs--mcp`] — preview aggregator bundles "pre-built Agent SOPs" alongside tools; not just raw API surface, but opinionated workflows.

### One-click install URL protocol as primary surface

[`awslabs--mcp`] — integration surface that bypasses JSON entirely for supported hosts.

### Spec-driven vs code-driven tool surface

[`awslabs--openapi-mcp-server`] vs the rest of the bin — major design axis. Spec-driven implications: docs drift (spec is source of truth), testing (every spec change is a contract change), LLM behavior (tool descriptions inherit spec quality).

### Code-as-tool as architecture choice

[`baryhuang--mcp-server-aws-resources-python`] — one flexible code-execution tool with AST sandbox versus N hand-enumerated per-API tools.

### Capability-probing at start

[`awslabs--bedrock-kb-retrieval-mcp-server`] — features only registered when env supports them, rather than failing at tool-call time.

### REPL-as-transport (nREPL)

[`bhauman--clojure-mcp`] — unusual for MCP; the JSON-RPC framing flows through an existing REPL connection.

### Agent-augmented tools (server's tools call out to LLMs)

[`bhauman--clojure-mcp`] — agent tools with optional external LLM integration (Anthropic, OpenAI, Google Gemini); the server's tools are themselves LLM-orchestrated.

### Provider-prefixed env var convention

[`chroma-core--chroma-mcp`] — `CHROMA_<PROVIDER>_API_KEY` gives a uniform auth surface across multiple embedding back-ends.

### Tag-based resource scoping

[`awslabs--bedrock-kb-retrieval-mcp-server`] — AWS tags as MCP access-control boundary; alternative to app-level access control.

### Server-framework category

[`awslabs--mcp-lambda-handler`] — "server" vs "server-framework" distinction not anticipated by the per-sample schema.

### Serverless deployment as first-class target

[`awslabs--mcp-lambda-handler`] — cold-start sensitivity, statelessness, external session stores all become design concerns.

### LLM_CODE_STYLE.md for prompt optimization

[`bhauman--clojure-mcp`] — explicit AI-assistant guidance file; unusual.

## Gaps

- Whether the `uvicorn` dep in [`awslabs--openapi-mcp-server`] indicates undocumented HTTP transport
- Test coverage details for [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`]
- How `@mcp.tool()` decorator maps to MCP protocol without `fastmcp` in [`awslabs--mcp-lambda-handler`]
- Whether streaming responses are supported in [`awslabs--mcp-lambda-handler`] given Lambda response-size constraints
- Exact `mcp` SDK version pin in [`blazickjp--arxiv-mcp-server`]
- Contents of `skills/` and `.codex-plugin/` manifest formats in [`blazickjp--arxiv-mcp-server`]
- Whether [`awslabs--mcp`] root pyproject.toml declares `[tool.uv.workspace]`
- Specific Java version constraints (JDK 17+ inferred but not confirmed) in [`bhauman--clojure-mcp`]
- nREPL transport protocol details in [`bhauman--clojure-mcp`]
- Python version floor, test presence, last-commit date for [`baryhuang--mcp-server-aws-resources-python`]
