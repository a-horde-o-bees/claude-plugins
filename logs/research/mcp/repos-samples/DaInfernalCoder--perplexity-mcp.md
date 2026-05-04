# Sample

Mirrors of `https://github.com/DaInfernalCoder/perplexity-mcp`. Perplexity search MCP server — exposes `search`, `reason`, `deep_research` tools with auto-complexity routing to Sonar Pro / Sonar Reasoning / Sonar Deep Research. 289 stars, MIT, default branch `main`, last commit November 1, 2025 ("Reasoning and Chat History"). Hackathon-winning design (1st @ Cline Hackathon).

## Server runtime

### Node.js with custom SDK composition

JavaScript (94.7%) Node.js server combining the MCP SDK with the Anthropic Claude Agent SDK rather than using the MCP SDK alone. The compositional choice surfaces because the server is itself an agent-like layer that calls out to Perplexity Sonar models while exposing MCP tools.

## Transport

### Streamable HTTP

HTTP transport inferred from Anthropic Agent SDK usage; selection mechanism not explicitly documented in extract.

## Capability surface

### Auto-routing across backends

Single logical tool (`search`) dispatches internally to one of multiple backend models (Sonar Pro / Sonar Reasoning / Sonar Deep Research) based on a complexity heuristic. Override parameter (`force_model`) lets the LLM bypass the heuristic when needed. Tools: `search` (Sonar Pro), `reason` (Sonar Reasoning Pro), `deep_research` (Sonar Deep Research).

## Configuration delivery

### Environment variables

`PERPLEXITY_API_KEY` from environment.

### CLI flags

`--api-key`, `--cwd` parameter for `.env` path.

### Dotenv file

`.env` file loaded at startup. Resolution priority: CLI arg > env var > `.env` file.

## Authentication

### Static API key / token via env var

Perplexity API key (`PERPLEXITY_API_KEY`) supplied via CLI arg, environment variable, or `.env` file.

## Multi-tenancy

### Single-user / single-tenant per process

Per-request context; assumes single-agent invocation.

## Distribution channel

### npm via npx / bunx

Published to npm; recommended install is `npx -y perplexity-mcp`. Source clone with `npm install` is the alternative.

### Smithery registry

Smithery registry integration — `smithery.yaml` present in repo. Discovery/distribution via Smithery's MCP-aware catalog.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx -y perplexity-mcp` is the canonical launch idiom; no separate launcher scripts.

## Container artifacts

### Multi-stage Dockerfile

Dockerfile present (multi-stage Node.js 18-Alpine).

## Repository layout

### Single-package source (language-conventional)

Single-package; dirs include `src/`, `examples/`, `memory-bank/`, `.roo/`; config files include `package.json`, `tsconfig.json`, `smithery.yaml`, `Dockerfile`.

## Documentation surface

### README as the canonical surface

README emphasizes npx invocation simplicity; sample configuration in README. Host integrations referenced in generic MCP-config terms; specifics not detailed.
