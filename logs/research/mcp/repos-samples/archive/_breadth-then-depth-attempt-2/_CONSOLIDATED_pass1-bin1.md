# Sample

Pass-1 Phase-1a partial for bin 1. Functional decomposition of AlwaysSany--deepl-fastmcp-python-server, Azure--azure-mcp, ClickHouse--mcp-clickhouse, DaInfernalCoder--perplexity-mcp, DiversioTeam--clickup-mcp, FuzzingLabs--mcp-security-hub, GLips--Figma-Context-MCP, HenkDz--postgresql-mcp-server, organized by role with implementation paths as sub-sections.

## Server runtime

The language and framework that hosts the MCP protocol loop and dispatches tool calls. Choice of runtime constrains which transports, packaging channels, and host-config shapes are natural.

### Python with FastMCP

Python server built on the FastMCP framework (typically the standalone 2.x package, pinned with caps such as `fastmcp>=2.0.0,<3.0.0`). FastMCP auto-derives tool schemas from typed function signatures, lets the author write nominally-synchronous tool functions while it manages the async transport boundary, and provides a native config file (`fastmcp.json`) alongside pyproject. Authors gravitate to it when they want a low-ceremony binding from "Python function with type hints" to "MCP tool" and don't need to hand-roll JSON-RPC handling. Compatible with all three official transports out of the box, so multi-transport support drops in without runtime changes.

### Python with raw MCP SDK

Python server importing the lower-level `mcp` package directly (e.g., `from mcp.server import Server`) rather than a higher-level wrapper. Authors who pick this layer typically also wrap their own CLI with `click`, validate config with `pydantic-settings`, and use `rich` for non-protocol output — the framework gap is filled with a la carte libraries. Pin discipline varies widely; very loose pins like `mcp>=0.1.0` show up in this branch, indicating less concern about SDK churn than FastMCP-based projects exhibit.

### Python with hand-rolled MCP

Python server with no MCP framework dependency at all — the JSON-RPC stdio loop is implemented per server. Surfaces in monorepos where the MCP layer is thin (e.g., subprocess-wrapping a CLI tool) and the author judged that pulling in FastMCP or the SDK would add more weight than the integration warrants. Packaging concerns get deferred entirely to the container layer; there is no shared pyproject.

### .NET / C#

C# MCP server compiled to a .NET binary. Surfaces in vendor-authored servers where the rest of the org's tooling and developer ecosystem is .NET-centric (Visual Studio, NuGet). Distribution naturally flows to NuGet packages and, secondarily, to Docker images and IDE-extension marketplaces. The runtime choice ties the server to the host platforms where .NET is a first-class citizen.

### Node.js with official TypeScript SDK

TypeScript server built on `@modelcontextprotocol/sdk`, compiled with a bundler such as tsup, and shipped as an npm package with a `bin` entry. Standard modern-TS scaffolding: pnpm, ESLint, Prettier, vitest. The npm bin convention makes `npx -y <package>` a one-liner host-config command, which dominates this branch's distribution stories. Authors who pick this layer get strict typing on tool schemas without a higher-level framework abstracting the SDK.

### Node.js with custom SDK composition

JavaScript/Node server that combines the MCP SDK with vendor-specific SDKs (e.g., the Anthropic Claude Agent SDK) rather than using the MCP SDK alone. The compositional choice shows up when the server is itself an agent-like layer that must call out to LLM APIs while exposing MCP tools, and the second SDK does work the MCP SDK does not.

## Transport

The wire protocol carrying MCP messages between host and server. Constrains the deployment shape (in-process subprocess vs networked service), authentication options (no-auth vs bearer/OAuth), and tenancy model.

### stdio

JSON-RPC over the server process's stdin/stdout, with the host launching the server as a subprocess. Default and most-common path; implies single-tenant (one process, one user), no authentication on the wire (the trust boundary is the process boundary), and host-driven lifecycle. Universal across runtimes — Python, Node, .NET, Docker-containerized servers all converge here. Often the only transport offered by simpler servers, and always the fallback when authors offer multiple.

### HTTP (Streamable / plain)

HTTP-based transport carrying MCP messages, suitable for networked deployments where multiple clients reach a long-running server process. Brings authentication into scope (bearer tokens at minimum) and opens per-request multi-tenancy possibilities. Selected via env var, CLI flag, or by the absence of a `--stdio` flag combined with a `PORT` env. Often paired with stdio in the same binary so one build serves both local-subprocess and remote-server deployments.

### SSE (Server-Sent Events)

HTTP-based long-lived stream from server to client, used as the streaming transport for remote MCP servers. Co-resides with HTTP and stdio in multi-transport binaries; selected via the same env var or CLI mechanism as the other non-stdio options. Implies the same auth and tenancy considerations as plain HTTP.

### Selection mechanism

Across the corpus, authors pick one of three selection conventions:

- CLI flag (`--transport stdio|sse|http`, or `--stdio` boolean) — explicit, scriptable, surfaces in `--help`
- Environment variable (`*_MCP_SERVER_TRANSPORT=stdio|http|sse`) — natural in container/Docker contexts where launching code already passes env
- Implicit (default to stdio; opt into HTTP by setting `PORT`) — minimal surface for the common case

## Distribution channel

How end users and host configs obtain a runnable server. Constrains the install command shown in host config and the friction of getting started.

### PyPI

Python packages published to PyPI under a stable name, installable via `pip install <name>` or — more commonly in this corpus — via `uv run --with <name>` or `uvx <name>` for ephemeral environments. Optional extras can swap in alternative engines (e.g., `[chdb]` for an embedded analytics path). Host-config command is typically `uv run` with on-demand install plus a pinned Python version, removing the user's responsibility to manage a venv.

### npm / npx

Node packages published to the npm registry, run via `npx -y <package>` directly from host config. This is the lowest-friction path for Node servers — a single host-config line with no install step. On Windows the same command is wrapped as `cmd /c npx ...` to navigate shell quoting. Bin entries in `package.json` make the package itself the executable.

### Install-from-git via uvx

Python server distributed without any registry publication — users install via `uvx --from git+https://github.com/<owner>/<repo> <command>`. The git URL becomes the effective package index; updates require pulling fresh, and there is no version range to pin. Surfaces when authors want zero registry-publication overhead, or treat the project as internal/team-scoped without a marketing release.

### NuGet

.NET packages on NuGet for C# servers, slotting into the .NET ecosystem's standard package manager. Often co-distributed with IDE-extension marketplace publications (Visual Studio Marketplace, IntelliJ Marketplace, Eclipse Marketplace) so the server reaches users through their IDE's native install flow.

### Docker image

Container image distributed via a registry (Docker Hub or unspecified org registries) and launched with `docker run` from host config. Self-contained — runtime, dependencies, and any wrapped CLI tools are baked in. Surfaces both as the primary distribution channel (when the server wraps platform-specific binaries that would be painful to install per-host) and as a secondary channel alongside PyPI/npm for users who prefer container isolation.

### Smithery registry

Discovery-and-distribution registry specific to the MCP ecosystem, integrated via `npx -y @smithery/cli install <owner>/<repo>` or via a `smithery.yaml` manifest in the repo. Adds the server to a searchable index of MCP servers; effectively a curation layer on top of npm/git. Optional, additive — the server typically also publishes to npm or PyPI directly.

### Source clone

`git clone` followed by `uv sync`, `npm install`, or equivalent. Always implicitly available; documented explicitly when the project lacks a registry presence or for development workflows. Does not show up in host-config commands.

## Entry point and launch shape

The exact command host configs run to start the server. Determined by distribution channel and runtime, but with author-level shape choices.

### Bare script with CLI args

A single Python script (e.g., `main.py`) at repo root, invoked as `uv run python main.py [args]`. No console-script entry point installed; all CLI flag parsing happens inside the script. Middle ground between "script with no args" and "console script with click" — gives the author transport-selection and host/port flags without committing to a packaging surface.

### Console script via pyproject

`[project.scripts]` entry in pyproject defining a stable command name (e.g., `mcp-clickhouse`) that resolves to a module function. Host config invokes the name directly (`uv run --with <pkg> <name>`) or uses `python3 -m <package>.main` as an alternative. Standard packaging approach for Python servers that publish to PyPI.

### `__main__.py` module entry

Python module defining `__main__.py`, with the console script pointing at `<package>.__main__:main`. Functionally equivalent to a `server:main` console script but visible at the package level — invocable as `python -m <package>` in addition to the named console script. Common when the same binary doubles as a management CLI (subcommands like `set-api-key`, `check-config`, `test-connection`) on top of the MCP server protocol.

### npm bin entry

`bin` field in `package.json` pointing at the built CLI, executed via `npx -y <package> [args]`. Universal among Node servers; the Windows variant wraps in `cmd /c`.

### Docker entrypoint

`docker run` with image name and any volume mounts and env vars; the container's ENTRYPOINT runs the server. The entire command is what host config calls, so host-side complexity grows with mount and env requirements.

## Configuration delivery

How the server learns its operational settings (credentials, connection info, feature flags). Determines what users have to set up before launching.

### Environment variables

Required and optional settings read from the process environment. The dominant pattern; works uniformly across runtimes and is well-supported by host MCP-config JSON schemas (which typically have an `env` field). Surfaces with vendor-specific naming conventions like `<TOOL>_API_KEY`, `<TOOL>_HOST`, `<TOOL>_MCP_SERVER_TRANSPORT`. Fine-grained behavior toggles (write-access, drop-table, auth-disabled-for-dev) ride on the same channel.

### CLI flags

Settings passed as command-line arguments at launch (`--api-key`, `--connection-string`, `--transport`, `--port`). Coexists with env vars; resolution priority typically CLI > env > file when multiple sources collide. Authors use flags when they want the host-config snippet to be self-documenting at a glance or when the value is intrinsically per-launch (transport choice, port).

### Dotenv file

`.env` file in the project directory, loaded at startup. Mostly a developer-convenience layer over env vars; the production path is still environment variables. Resolution lands at the bottom of the priority chain (CLI > env > .env).

### Persistent OS-native config

Settings stored in a platform-appropriate config directory via `platformdirs` (`~/.config/<app>/` on Linux, `%APPDATA%\<app>\` on Windows, etc.), written by a management subcommand of the same binary (`set-api-key`, etc.). Survives across launches without per-host env-var setup. Unusual in this corpus — most MCP servers leave persistence to the host's MCP config JSON and read only from env at runtime.

### Per-tool enablement file

JSON or similar file (`tools.json`) referenced by env var (`POSTGRES_TOOLS_CONFIG`) that toggles individual tools on/off. Used to reduce the LLM-visible tool surface without forking the server. Sits orthogonal to credential config — same server, different tool subset per deployment.

### Framework-native config file

Config file consumed by the server framework itself, not by application code (`fastmcp.json` for FastMCP). Carries framework-level settings (transport defaults, runtime options) that don't belong in env vars or CLI. Coexists with the application's env-var surface.

## Authentication

How the server authenticates inbound calls (when applicable) and how it authenticates outward to its backing service.

### Service API key

Static API key for the backing service (DeepL, Perplexity, Figma, ClickUp, etc.), supplied via env var, CLI flag, or persistent config. Single credential, single tenant; the server holds it and uses it for every backed call. The dominant pattern for SaaS-API-wrapping servers. Some servers add a credential-resolution priority chain (CLI > env > file) so multiple sources can coexist.

### Database connection string

Username/password embedded in a `postgres://user:pass@host:port/db`-style URL. Supplied via env var or CLI flag. Authentication is whatever the database speaks; the MCP server is just a relay.

### Bearer token over HTTP/SSE

Bearer token required when the transport is HTTP or SSE; absent on stdio (where process boundary is the trust boundary). Token typically generated out-of-band (`uuidgen`, `openssl rand`) and passed via env var to the server. Dev-mode override flag (`*_AUTH_DISABLED=true`) lets authors run unauthenticated locally without code changes.

### Per-tool varied

In monorepos that ship many independent servers (one per wrapped tool), authentication varies per server — some need API keys (vulnerability databases), others need none (local CLI wrappers). The container env injection mechanism is uniform; the credentials inside it are tool-specific.

### Cloud-platform credential chain

For cloud-platform servers (Azure, AWS), authentication delegates to the platform's standard credential-discovery chain (DefaultAzureCredential or equivalent), which walks env vars, instance metadata, managed identity, and developer-CLI credentials in order. The server itself doesn't define an auth mechanism — it inherits the platform's.

## Multi-tenancy

Whether and how a single server instance can serve multiple users or workspaces.

### Single-tenant per process

One server process serves one user/workspace; switching users means relaunching with different credentials. The default for stdio servers (process boundary equals trust boundary) and for most SaaS-API-wrapping servers (one API key, one identity). No code complexity; matches the host-launches-subprocess model perfectly.

### Per-request via middleware

HTTP-mode server allows per-request connection overrides through middleware-managed context state — incoming request can carry connection settings that override the process defaults for the duration of that call. Closest the corpus comes to true multi-tenancy. Requires HTTP transport (stdio has no per-request channel for this) and a middleware extension point.

### Single connection per server instance

Database servers that hold one connection (per the supplied connection string) for the process lifetime. Effectively single-tenant; the workaround for multiple connections is multiple server instances.

## Capability surface

What the server exposes to the LLM — tools, resources, prompts, etc.

### Tools-only surface

Server exposes one or more tools and nothing else (no resources, prompts, sampling, roots). Dominant pattern. Tool counts vary widely — small handfuls (3-7) for narrowly-scoped servers like translation or search, mid-twenties for task-management or DB servers, into the dozens for kitchen-sink integrations.

### Tool consolidation as design pressure

Authors actively reduce tool counts (one repo went from 46 atomic tools to 17 meta-tools) as a deliberate response to LLM discovery and parameter-validation pressure — too many narrow tools confuse model selection; broader meta-tools with more parameters work better. Surfaces as an explicit narrative choice, not just an emergent count.

### Auto-routing across backends

Single logical tool (`search`) dispatches internally to one of multiple backend models (Sonar Pro / Sonar Reasoning / Sonar Deep Research) based on a complexity heuristic. The LLM picks "what to do," the server picks "which engine." Inverts the conventional surface where each backend gets its own tool name. Override parameter (`force_model`) lets the LLM bypass the heuristic when needed.

### Monorepo of micro-servers

Instead of one server with many tools, ship many servers each exposing a narrow toolset for one concern. Each server is its own container, its own MCP entry in the host's config. Composability moves from the tool layer to the deployment layer — users pick which servers to run, not which tools to enable.

### Self-reflective analytics tool

Tool exposes aggregated observations of the server's own past calls (`analyze_usage_patterns`, `get_translation_history`) back to the LLM. Implies local persistence of call history (not typical of the otherwise-stateless MCP server pattern) and surfaces the server's own behavior as a queryable resource.

### Progressive trust gating

Destructive operations (writes, drops) gated behind separate boolean env vars rather than a single read-only toggle (`*_ALLOW_WRITE_ACCESS` plus a separate `*_ALLOW_DROP`). Two-step opt-in for destructive surface; finer-grained than the binary read-only knob common elsewhere.

## Repository layout

How the codebase is organized across packages and deployment artifacts.

### Single-package

One package, one entry point — `src/`, `tests/`, manifest at root. Default for servers that wrap one upstream service. Same shape across Python, TypeScript, and other runtimes.

### Monorepo of independent servers

Many subdirectories, each a standalone MCP server with its own Dockerfile, scripts, and tests. A `Dockerfile.template` at the root acts as scaffolding for adding new servers. The repo as a whole is the contribution surface; individual servers are the deployment units.

### Umbrella consolidation

Originally per-service repos collapsed into a single org-level monorepo with `/servers/<name>/` subdirectories and `/core/` shared libraries. The consolidation pattern surfaces with a transitional period — original repos are archived with redirect notices to the umbrella, sometimes with a multi-month gap between code-freeze and formal repo archival as the redirect stabilizes.

## Container and packaging artifacts

Container-related files in the repo and what role each plays.

### Dockerfile as deployment artifact

`Dockerfile` (sometimes multi-stage) producing the runtime image used in production. Bakes in the language runtime, dependencies, and the server entry point. Universal across runtimes. Multi-stage builds (e.g., Node 18-Alpine final stage) trim runtime image size.

### Docker Compose for local dev

`docker-compose.yml` orchestrating the server alongside its backing services for local development (e.g., spinning up a database the server connects to). Distinct role from the production Dockerfile — Compose owns the dev-loop experience, the Dockerfile owns the runtime artifact.

### Docker Compose for multi-server orchestration

In monorepo-of-servers layouts, Compose orchestrates many MCP server containers together so users can bring up the full security or domain toolchain at once.

### Dockerfile.template as scaffold

A template Dockerfile parameterized for "new tool added to the monorepo" — enforces the security baseline (non-root, capability-drop, read-only mounts, resource limits) and base-image conventions across all per-tool servers. Contribution-surface artifact, not a runtime artifact.

### Hardened-by-default container posture

Dockerfile baseline includes non-root user, dropped Linux capabilities, read-only filesystem mounts, resource limits. Surfaces in security-focused projects where the wrapped CLI tools are themselves attack surface; uncommon in general-purpose MCP servers.

## Test stack

How the project verifies correctness, and what infrastructure tests depend on.

### pytest with async extras

`pytest` plus `pytest-asyncio` (and optionally `pytest-cov`) for Python projects. Standard configuration; tests under `tests/`. Test density varies widely with no clear correlation to project popularity — small-star projects sometimes carry dozens of tests.

### Docker Compose for integration test infra

`test-services/` directory with a Docker Compose file spinning up real backing services (databases, etc.) for integration tests, alongside unit tests in the same `tests/` tree. Lets pytest exercise real protocol-level behavior without mocking the upstream service.

### vitest

TypeScript projects use vitest as the test runner, configured via the project's normal TS tooling. Standard modern-TS choice.

### Tests not surfaced

Many samples don't surface test details in their README — presence of a `tests/` directory or pytest.ini is sometimes the only signal. The absence of test discussion in documentation is itself a corpus-level signal: testing is rarely a marketed feature for MCP servers.

## CI

Automated workflows triggered on commits or releases.

### GitHub Actions present

`.github/workflows/` directory with one or more workflow files. Universal where any CI is present; specific triggers and jobs vary and often aren't extracted into READMEs.

### Build + test + supply-chain scan

CI pipeline that builds the artifact (Docker image, npm/PyPI package), runs tests, and runs supply-chain scanning (e.g., Trivy for container vulnerabilities). The scan step is treated as a build gate rather than a separate concern; surfaces in security-focused projects.

## Host integrations documented

Which host applications the README walks through configuring.

### Claude Desktop

JSON `mcpServers` config snippet shown in README. Most common documented host. Snippet usually shows the launch command (`npx -y <pkg>`, `uv run ...`, `docker run ...`) plus the env-var block.

### Claude Code

Project-level `.mcp.json` file with per-server entries. Less commonly documented than Claude Desktop but appears in monorepo layouts where many servers ship together.

### Cursor

JSON config snippets specific to Cursor's MCP integration. Featured prominently in design-tool-integration servers and as a co-equal target in dev-oriented servers.

### Visual Studio family

Visual Studio 2022, VS Code, VS Code Insiders, IntelliJ IDEA, Eclipse — surfaces in vendor-authored servers (.NET ecosystem) where the host integration ships as an IDE extension via the platform's marketplace.

### Generic MCP-compatible

Stdio-launch instructions framed for any compliant MCP host without naming specifics. Default fallback when authors don't want to enumerate hosts.

## Developer ergonomics

In-repo tooling that supports development of the server itself (not its consumers).

### Setup subcommands on the MCP binary

The same console script that runs the MCP server protocol also exposes management subcommands (`set-api-key`, `check-config`, `test-connection`) for credential setup and connectivity verification. Doubles the binary as a config CLI; uses `rich` and `click` for the human-facing output. Pattern echoes `kubectl config`-style CLIs.

### MCP framework dev config

`fastmcp.json` for FastMCP-based projects gives the framework first-class dev configuration in the repo, separate from pyproject. Lets `fastmcp` dev tooling discover the server without arg passing.

### Sample example middleware

`example_middleware.py` or equivalent demonstrating how to extend the server via a configured middleware module. Acts as both documentation and a test of the middleware extension point.

### Health-check scripts

Per-container health-check scripts in monorepo-of-servers layouts so Docker can verify each server is responsive. Tied to container deployment patterns.

### Linter and formatter conventions

Standard runtime-appropriate tooling (ruff for Python, ESLint+Prettier for TypeScript, mypy for typed Python projects), git hooks via lefthook or similar. Signals an opinionated dev environment that consumers contributing back should expect to match.

## Extension points

Mechanisms the server exposes for users to modify behavior without forking.

### Middleware module slot

Env var (`MCP_MIDDLEWARE_MODULE`) names a Python module that intercepts FastMCP protocol events (tool calls, resource reads, prompts, listings) and can mutate context state (e.g., per-request connection overrides) or implement cross-cutting concerns (logging, tracing, performance measurement). The closest thing in the corpus to a true plugin architecture for an MCP server.

### Per-tool enablement

JSON config file toggles individual tools without code changes. Lets deployers shrink the LLM-visible surface for safety or focus, and lets the same server image serve multiple deployment profiles.

## Documentation surface

How the project communicates what it is and how to use it.

### README as the canonical surface

Single README.md carrying purpose, install, config, host integration, and tool inventory. Universal. Length and depth vary widely.

### README plus docs directory

Supplementary `docs/` directory for longer-form material (architecture, per-tool deep dives) referenced from README. Surfaces in larger or more mature projects.

### Archival redirect README

When a repo is superseded, the README is replaced by an archival notice pointing at the successor. Two-stage archival is a recurring shape — README declares archival on one date, the GitHub repo flag flips months later as the redirect's stability gets confirmed.
