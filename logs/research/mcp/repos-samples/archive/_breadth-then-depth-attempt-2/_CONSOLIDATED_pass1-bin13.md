# Sample

Pass-1 Phase-1a partial for bin 13. Functional decomposition of twolven--mcp-server-puppeteer-py, upstash--context7, utensils--mcp-nixos, v-3--discordmcp, viant--mcp, voska--hass-mcp, zilliztech--mcp-server-milvus, and zongmin-yu--semantic-scholar-fastmcp-mcp-server, organized by role with implementation paths as sub-sections.

## Server runtime

The language and runtime that hosts the MCP server process. Determines which SDK is available, what packaging conventions apply downstream, and whether the deliverable is a script, compiled binary, or interpreted package.

### Python

Python interpreter as host. Pairs naturally with PyPI distribution and uv/uvx invocation; supports stdio servers as plain `__main__` modules and HTTP servers as ASGI apps. Version floor is a meaningful axis on its own — observed floors range from 3.8 (legacy `setup.py`-era projects) through 3.10 (the common modern baseline) up to 3.11 and 3.13 (aggressive floors that gain newer typing/syntax features at the cost of locking out older deployments).

### Node.js / TypeScript

JavaScript runtime as host, typically with TypeScript at author-time and a `build/` JS output as the launched artifact. Pairs naturally with npm/npx distribution and a `node build/index.js` entry point. Node version floors observed include `16.x+` for older projects; modern monorepo setups use pnpm workspaces and changesets for coordinated releases without an explicit version floor surfacing.

### Go

Compiled-binary host. Pairs naturally with `go get` consumption as a library and standalone-binary distribution for end users; no per-process runtime install is required of consumers of the binary. Used here as an SDK/framework target rather than a single application — the Go entry exposes both server-embedding (functional-options API) and a standalone bridge binary so consumers can either embed the library or run a packaged executable.

## MCP framework / SDK

The library that handles JSON-RPC framing, capability negotiation, and tool/resource registration. Determines schema strategy, async style, and how much of the protocol the author writes by hand.

### FastMCP

Higher-level Python framework that auto-derives JSON schemas from Python type hints and handles transport selection. Two major lines exist: an older 1.x style imported as `from mcp.server.fastmcp import FastMCP` (bundled with the `mcp[cli]` extra), and a newer 2.x line imported as `from fastmcp import FastMCP` published as a separate `fastmcp` package. Newer 2.x versions have lower-bound pins like `fastmcp >= 2.14.1`. Pairs naturally with Pydantic for schema generation and with `httpx`/async tool functions. Often used alongside `click` for CLI argument parsing even though FastMCP ships its own launcher.

### Raw MCP SDK (Python)

Lower-level `mcp` package without the FastMCP convenience layer. Authors hand-author tool schemas. Surfaces both as the modern `mcp[cli]>=1.4.1` (still a relatively old pin compared to the latest releases) and as legacy pre-1.0 `mcp-server>=0.1.0` referenced in `setup.py`-era projects. Suited to projects that need fine control over schema shape or need to predate FastMCP availability.

### MCP TypeScript SDK

Official TypeScript SDK published by Anthropic. Used by Node-based servers; pairs naturally with discord.js, Puppeteer, or any other Node ecosystem dependency the server needs. Schema definition is hand-authored in TypeScript.

### Custom Go MCP SDK

Hand-built Go implementation of the MCP protocol on top of JSON-RPC 2.0. Exposes a functional-options API (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`, `WithRootRedirect`) for configuring servers, separate `client.go`/`server.go` packages, and an out-of-process bridge binary. Includes built-in OAuth2/OIDC support (a feature that most Python/TypeScript SDKs delegate to the host).

## Transport

The wire protocol the host uses to communicate with the server. Each transport choice constrains the deployment shape and the multi-tenancy story.

### stdio

JSON-RPC over the launched process's stdin/stdout. Implicit when the server is launched as a child process by a desktop host (Claude Desktop, Cursor); the host pipes JSON in and reads JSON out. Single-process / single-user by construction — the host owns the lifetime of the server. Constrains stdout: any unprotected log writes corrupt the JSON-RPC stream. The most common transport across the sample set; default in most servers and the only transport in the simplest ones. Works equally well when the server is wrapped in a Docker container that runs the stdio server inside (`docker run -i`).

### SSE (Server-Sent Events)

HTTP-based transport using Server-Sent Events for server→client messaging. Suited to long-running shared deployments where multiple clients connect to one server; requires HTTP-mode infrastructure (host, port, URI paths). Often configured alongside stdio as an alternative mode the user can select.

### Streamable HTTP

Newer HTTP transport that supports request/response streaming without SSE's connection-lifetime constraints. Configurable via functional options or env vars. Often paired with stateless-mode flags so the same HTTP endpoint can be deployed behind a load balancer for shared multi-user use.

### In-process HTTP bridge alongside stdio

A custom HTTP server bound to a fixed port (e.g., 8000) running inside the same process as the stdio MCP server, exposing equivalent functionality to non-MCP clients. Distinct from "pick a transport" — both protocols serve simultaneously. Toggled via env var (e.g., `*_ENABLE_HTTP_BRIDGE`). Suited to projects that want to be consumable by both MCP-aware agents and arbitrary HTTP clients without duplicating business logic. Often implies a custom bridge implementation rather than the SDK's built-in HTTP transport.

## Transport selection mechanism

How the user or host tells the server which transport to use. Distinct from the transports themselves — it's the configuration affordance.

### Environment variables

Transport choice driven by env vars at process start (e.g., `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP`). Convenient for container deployments where env is the natural injection point.

### CLI flags

Transport selected by command-line argument when launching the entry point. Often paired with multiple JSON config snippets in the README — one per mode — that show users how to wire the host to each transport.

### Functional options (in-code configuration)

Caller assembles the server with composable option functions (`WithStreamableURI()`, `WithSSEURI()`, `WithSSEMessageURI()`) before starting it. Suited to library/SDK projects where the consumer is another program rather than an end user invoking from a host config.

### Separate entry points per transport

Each transport mode is a distinct entry function or binary (e.g., `stdioSrv.ListenAndServe()` vs `srv.HTTP(...).ListenAndServe()`). Forces an explicit choice at code-level rather than runtime configuration.

### Implicit (default only)

Server only supports one transport (typically stdio); no selection mechanism needed. Common in single-purpose servers built for a desktop host.

## Distribution channel

How the artifact reaches end users. Frequently combined — a single project may publish to PyPI, Docker Hub, and a declarative package manager all at once.

### PyPI / pip

Standard Python package index distribution. Consumers run `pip install <pkg>` and invoke the installed console script. Pairs naturally with pyproject.toml + hatchling builds and uv-based lockfiles. Often combined with uvx as the recommended consumer-facing one-liner.

### uvx (PyPI via uv)

`uvx <pkg>` runs the latest version in an ephemeral environment without a global install. Common pattern in modern host-config snippets — the JSON snippet uses `"command": "uvx"` with the package name, and the user never has to manage a venv. Works against any PyPI-published package.

### Source clone + `uv run`

Server is launched from a checked-out source tree via `uv run src/<package>/server.py ...`. Unusual for vendor-official servers; signals either a development-leaning posture or that the project hasn't fully embraced PyPI distribution. Forces consumers to clone the repository before they can run the server.

### Source-only clone (no published package)

Distribution is `git clone` plus build/install instructions. No npm or PyPI publication. Limits reach to users willing to clone but keeps repo simple and avoids registry/account ceremony. Surfaces in both Node projects (`npm install && npm run build`, then `node build/index.js`) and Python projects (`pip install -r requirements.txt`).

### npm / npx

Node Package Registry distribution. `npx <pkg>` runs a CLI without a global install; often used for one-shot setup commands (e.g., an OAuth-bootstrap script) as well as for the long-running server itself.

### Docker image

Server packaged as a container image published to a registry (Docker Hub, ghcr.io). Consumers pull and run with `docker run -i --rm -e <ENV>... <image>`. The host config uses `"command": "docker"` with the image and env passthrough as args. Suited to environments where Docker is already part of the operator's mental model (e.g., Home Assistant deployments). Often paired with PyPI/uvx as a secondary install method.

### docker-compose

Compose file shipped in the repo to orchestrate the server alongside its dependencies. Suited to projects bundling multiple services (e.g., a server plus a database it needs).

### Nix flake (`nix run github:...`)

Nix-native install via flake reference; consumers run `nix run github:<owner>/<repo>` without registry intermediation. Reproducible by Nix's content-addressed store. Often paired with a `nix develop` shell for contributors.

### Declarative NixOS / Home Manager module via nixpkgs

Server packaged as a first-class nixpkgs entry; users add a config block to their NixOS or Home Manager config. Rare among MCP servers — gives the project a system-config-managed install path for declarative-systems users.

### Go module (`go get`)

Library/SDK consumed by other Go programs via `go get github.com/<owner>/<repo>`. Distribution is the source-as-Go-module model; no published binaries needed for the library use case.

### Standalone bridge binary

Pre-built executable that wraps the library so non-Go programs can use it without embedding. Distributed alongside the Go-module library for the same project. Suited to allowing Python/Node/etc. tools to consume an MCP server backed by the library without needing a Go toolchain.

### Hosted HTTP MCP endpoint

Server runs on infrastructure the project operates; consumers point their host at a stable URL (e.g., `https://mcp.context7.com/mcp`) instead of running anything locally. Pairs naturally with OAuth or API-key auth.

### Smithery registry

Listing in a third-party MCP server registry (Smithery) that distributes config rather than artifacts. Complementary to source/PyPI/Docker — the registry surfaces the project to discovery, the underlying install still happens via one of the other channels.

### `.claude-plugin/marketplace.json`

Marketplace metadata file shipped in-repo so the project surfaces in Claude's plugin marketplace. Distinct from a full `plugin.json` plugin wrapper — the marketplace file alone enables discovery without installing the project as a Claude plugin.

## Entry point / launch shape

What the user actually runs (or what the host invokes) to start the server. Frequently determined by distribution choice but worth tracking separately because the same package can be launched in multiple shapes.

### Console script

`[project.scripts]` (Python) or `bin` field (Node) declares a named executable that wraps the package's main function. Host config uses the bare command name (e.g., `"command": "hass-mcp"`). Pairs with PyPI/npm distribution.

### `uvx <package>`

Host config uses `"command": "uvx"` and passes the package name as an arg; the package is fetched and run on demand. Common host-config shape for modern Python servers.

### `npx <package>`

Node analog of uvx — `"command": "npx"` with the package name fetches and runs without global install. Also used for one-shot bootstrap commands like OAuth setup wizards.

### `docker run -i --rm`

Host config uses `"command": "docker"` and passes `run -i --rm -e <ENV> <image>` as args. The MCP transport is stdio inside the container, with the `-i` flag wiring host stdin/stdout to the container.

### Single-file script (`python <file>.py`)

Server lives in one `.py` file at the repo root; host config invokes `"command": "python"` with the file path as an arg. Bare `python` on system PATH is fragile (depends on which interpreter is first found). Common in legacy setup.py-era projects and minimal experimental servers.

### Built JS file (`node build/index.js`)

TypeScript projects compile to a JS output directory and host config invokes Node against the built file. Requires the consumer to have run `npm install && npm run build` first.

### Source-tree `uv run`

`"command": "uv"` with `run src/<package>/server.py ...` as args. Launches against a checked-out source path rather than an installed package. Unusual but documented in some projects' canonical configs.

### Library embedding (no entry point)

The project is consumed as a library/SDK; the consumer writes their own `main` and embeds the server. Used by Go SDK projects that expose `srv.HTTP(...)` and `stdioSrv.ListenAndServe()` for callers to invoke.

### Standalone bridge binary

Pre-compiled executable that wraps the library so non-language-native consumers can launch a working server without writing any code.

## Configuration delivery

How runtime configuration (auth tokens, backend URLs, transport tuning) reaches the server process.

### Environment variables

Runtime config injected via env (`HA_TOKEN`, `DISCORD_TOKEN`, `MILVUS_URI`, `SEMANTIC_SCHOLAR_API_KEY`, etc.). Universal default — every transport/distribution combination supports it. Pairs cleanly with Docker (`-e VAR`), uvx (env inheritance), and host-config JSON (which has explicit `env` blocks).

### `.env` file

Dotenv-style file consumed at startup. May take precedence over CLI args or env vars (one observed project explicitly inverts the common ordering, treating `.env` as the highest-priority source) — biases toward reproducible host-config-driven deployments at the cost of overriding a CLI invocation.

### CLI arguments

Args parsed from the launch command (often via `click` in Python projects, even when the framework provides its own launcher). Useful when env-based config feels heavy or when one process needs to host multiple variants. Frequently combined with env vars where each acts as a fallback for the other.

### Functional options at construction

In library/SDK projects, the consumer passes option functions when building the server (`WithStreamableURI(...)`). No external config — choices are baked into the consuming program's source.

### Host-config JSON

The host (Claude Desktop, Cursor) writes a JSON snippet that names the command, its args, and its env block. This is the visible configuration surface for end users; the server itself reads only env/CLI/.env, but the host's JSON is what the README documents.

### OAuth setup wizard

A one-shot interactive command (e.g., `npx ctx7 setup`) walks the user through OAuth and writes the resulting credentials into the host's config file. Removes manual JSON editing for users; constrains the project to ship a setup helper alongside the server.

## Authentication

How the server authenticates against its backend or its callers.

### None (public backend)

Server talks to a public API or runs entirely locally; no credentials. Suited to read-only public-data servers (browser automation against the open web, public package indexes).

### Long-lived token via env var

User generates a token in the upstream system's UI (e.g., Home Assistant long-lived access token, Discord bot token) and injects it via env. Single-tenant — one token per process. Common in self-hosted-backend integrations where the user already manages the upstream system.

### API key (optional, for higher rate limits)

Server works without credentials but accepts an API key (`SEMANTIC_SCHOLAR_API_KEY`, `CONTEXT7_API_KEY`) to lift rate limits or unlock additional features. Lowers friction for first use; rewards users who register.

### OAuth setup-wizard flow

Setup helper (e.g., `npx ctx7 setup`) runs the OAuth dance and persists the resulting token. Per-user identity rather than per-process. Pairs naturally with hosted HTTP MCP endpoints where the credential is sent on each request.

### OAuth2 / OIDC bearer tokens

Server-side enforcement of OAuth2/OIDC. Two modes observed: global resource protection (any request requires a valid bearer token) and fine-grained per-tool/resource control (still flagged experimental). Client-side counterpart includes automatic token acquisition on a 401 response — the client discovers the protected resource metadata, acquires tokens, and retries — bringing tool-style HTTP libraries closer to OAuth-aware browsers.

### Bot identity (third-party platform)

Auth against a chat or social platform via that platform's bot model — Discord bot tokens, etc. The bot's permissions (which servers it's invited to, what scopes it has) define the reachable surface; users grant the bot access through the platform's normal invite flow rather than configuring the MCP server directly.

## Multi-tenancy model

Whether one running server can serve one user or many. Closely linked to transport — stdio implies single-tenant, HTTP modes can support multi-tenant with the right design.

### Single-user, single-process

One server process per user. Stdio transport implies this by construction (the host owns the process). The most common mode by far.

### Bot-scoped

One bot identity per process; the bot's platform memberships define the reachable tenants. Multiple users may interact with the same bot, but the server's identity is fixed.

### Per-user OAuth token

Each user has their own OAuth credential; the server uses the credential on the user's behalf. Pairs naturally with hosted HTTP endpoints serving many users.

### Per-request bearer token

Each HTTP request carries its own token; the server identifies the tenant from the token. Suited to multi-user shared deployments behind a load balancer.

### Stateless HTTP for shared deployment

Server flag (e.g., `*_STATELESS_HTTP`) disables per-connection state so the server can sit behind a load balancer with multiple instances handling requests interchangeably. Multi-user-capable when paired with per-request auth.

## Capability surface

What the server actually exposes — tools, resources, prompts. Worth tracking the count and shape because it bears on token efficiency and on what the server is for.

### Minimal (1–5 tools)

Deliberately small surface. Suited to focused servers (a single domain action like "send Discord message" or "navigate browser") or to projects that consciously trade breadth for token economy. Discord MCP and Puppeteer-py both sit here.

### Moderate (10–20 tools)

Functional groupings of related actions (e.g., 16 tools split across paper search, citation analysis, author info, recommendation; ~15 tools for vector DB CRUD plus search variants). Often documented with explicit grouping headers in the README.

### Unified broad-tool surface

Two tools that each accept a wide query parameter (one observed: `nix()` taking a unified query at ~1,030 tokens of schema, plus `nix_versions()`). Deliberate token-efficiency strategy: fewer tools means smaller capability advertisement to the host, even though each tool covers a broad surface area.

### Server protocol features beyond tools

The MCP spec includes resources, prompts, sampling, roots, logging, progress reporting, request cancellation, subscriptions, and elicitation. Most servers in this bin expose only tools; SDK-style projects (Go) expose the broader surface so library consumers can build any protocol shape they need.

## Host integration

How the project documents getting itself wired into specific hosts.

### Claude Desktop JSON snippet

The dominant pattern: README embeds a JSON `mcpServers` entry showing exactly what to paste into `claude_desktop_config.json`. Distinguishes by transport (stdio vs SSE often have separate snippets) and by distribution (Docker, uvx, npx, etc. each get their own snippet shape).

### Cursor JSON snippet

Equivalent JSON snippet for Cursor's config file. Often shipped alongside the Claude Desktop snippet; sometimes accompanied by a `.cursor/` directory with project-level config.

### Multi-host catalog (30+ agents)

README documents support for 30+ different agent platforms with per-agent config snippets. Implies the server is generic enough that it doesn't depend on host-specific features.

### MCP Inspector

`npx @modelcontextprotocol/inspector <command>` for manual testing. Documented as the recommended way to verify the server before wiring it into a host.

### Claude Code

Native support for the `/mcp` flow or the `claude mcp add` command. Often documented as one of several supported hosts rather than the primary target.

### NixOS / Home Manager module

Declarative config entry (an attribute set added to `configuration.nix` or `home.nix`) handles install + activation in one place. Rare among MCP servers; tied to the Nix distribution channel.

### No host integration documentation

SDK-style or library projects skip host-specific docs because the consumer is another program, not a host. Examples and library docs replace host snippets.

## Plugin wrapper

Whether the project ships Claude-plugin-system metadata in addition to (or instead of) being a plain MCP server.

### `.claude-plugin/marketplace.json` only

Marketplace discovery metadata without a full plugin.json. Lets the project surface in Claude's marketplace UI without becoming a full installable plugin — a discovery hook on top of the existing MCP-server distribution.

### None

No `.claude-plugin/` directory; the project is consumed only via host MCP configs and not through the plugin system. Most servers in this bin sit here.

## Test stack

Testing approach and framework.

### pytest

Standard Python test framework. Pairs with FastMCP / raw mcp servers; fixture style varies and is not always surfaced in READMEs. Sometimes gated behind a `[dev]` optional extra so end users don't pull test deps.

### Go stdlib testing

Standard `testing` package; test files live alongside source as `client.go`/`server.go` patterns. Common to all Go projects.

### npm test (monorepo workspace)

`npm run test` invoked across pnpm workspaces in monorepos; specific framework not always surfaced.

### MCP Inspector (manual)

Not a unit/integration test, but an authoring-time interactive verification step the README documents (`npx @modelcontextprotocol/inspector <launch-command>`). Often the only documented testing approach for minimal projects.

### None

No test framework documented or visible in repo root. Common in single-file experimental servers and in projects whose maintainer relies on manual host testing instead.

## CI

Continuous integration setup.

### GitHub Actions

`.github/workflows/` directory with workflows (often not detailed in READMEs beyond a badge). Runs lint, format, and test scripts; sometimes paired with a CodeRabbit-style PR review bot.

### None

No `.github/workflows/` surfaced. Common in single-file or experimental projects.

## Containerization / deployment artifacts

Container or system-level packaging that ships alongside the server source.

### Dockerfile + image registry

Dockerfile in repo + image published to Docker Hub or ghcr.io. Doubles as a distribution channel (consumers `docker pull`) and a deployment artifact (operators run the image directly). Often paired with `docker run -i` host configs.

### docker-compose

`docker-compose.yml` orchestrating the server with related services (e.g., a database). Suited to dev setup and to deployments needing multiple coordinated containers.

### Nix flake / NixOS module

`flake.nix` for `nix develop` and `nix run` workflows; declarative module exposed via nixpkgs for system-level installation. Doubles as distribution (consumers `nix run`) and dev environment (`nix develop` provides a reproducible shell).

### None

No container or system-packaging artifacts; consumers handle install via PyPI/npm/source.

## Repo layout

How the source tree is organized.

### Single-file script

One `.py` or `.ts` file at repo root plus a manifest (`requirements.txt` / `package.json`). Suited to minimal experimental servers; reflects a "demonstration" rather than "long-lived project" posture.

### Single-package

Conventional Python `src/<package>/` or Node `src/` layout with one published package. The dominant shape in this bin.

### Monorepo with pnpm workspaces and changesets

Multiple packages under `/packages` coordinated by pnpm-workspace.yaml; changesets handles version bumps and changelog generation across packages. Often accompanies projects that ship a server, a CLI, and additional tooling as separate but coordinated artifacts. Expanded layout includes `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n` directories alongside `/packages`.

### Library with subdirectories

Go library layout: root-level `client.go`/`server.go`/`doc.go` plus subdirectories for `/bridge`, `/client`, `/server`, `/internal`, `/docs`, `/example`. Suited to SDK-style projects where the surface is multiple consumable packages.

## Python build system

Build backend choice and lockfile convention for Python projects. (Bin includes both legacy and modern shapes.)

### pyproject.toml + hatchling

Modern PEP 517 build backend. Pairs with `[project.scripts]` console-script declarations and `requires-python` floors. Often combined with a committed `uv.lock` for reproducibility and with optional `[dev]` extras for test-only deps.

### Legacy `setup.py` + `requirements.txt`

Pre-PEP-517 packaging. No `pyproject.toml`. Console scripts declared in setup.py's `entry_points`, but README invocation may diverge from the declared script (a sign the package was never installed/tested as a console script). Reflects an older project that hasn't migrated.

### Lockfile committed (`uv.lock`)

Project commits its uv-managed lockfile so contributors and CI install the same resolved versions. Modern convention; not universal.

### `.python-version` file

Project pins the local interpreter version via pyenv-style file. Often combined with uv to enforce the floor.

## Notable cross-cutting axes

Patterns observed in this bin that don't fit cleanly under a single role.

### Public-vs-private architectural split

Project's MCP client/wrapper code is open-source while the backend (parsing, crawling, query-resolution engines) is private and run as a hosted service. The OSS repo is consumable but doesn't reveal the full implementation. Pairs naturally with the hosted-HTTP-endpoint distribution and OAuth/API-key auth.

### Token-efficiency-driven capability design

Deliberate compression of the tool surface to a small number of broad tools (e.g., one unified query tool) on the rationale that schema text counts against the host's token budget. A design pressure that affects capability surface, schema strategy, and even backend indexing.

### Setup-wizard CLI as bootstrap

A one-shot npx/uvx command that bootstraps OAuth, writes host config, and registers credentials before the user touches any JSON. Reduces install friction at the cost of shipping an additional CLI artifact alongside the server.

### Source-tree-only invocation as canonical

Some vendor-official servers document `uv run src/<package>/server.py ...` as the primary launch even though the package is also published. Constrains consumers to clone the repo and biases the project toward developer-mode use.
