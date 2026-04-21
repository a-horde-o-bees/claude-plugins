# Gemini CLI MCP Docs

## Identification
- url: https://geminicli.com/docs/tools/mcp-server/
- type: host integration docs
- author: Google (Gemini CLI team)
- last-updated: active
- authority level: official (for Gemini CLI)

## Scope
Google's Gemini CLI MCP configuration. Config lives in `settings.json` under `mcpServers`, either globally at `~/.gemini/settings.json` or per-project at `.gemini/settings.json`. Supports multiple transports: HTTP (remote URL with custom headers like Bearer tokens), Docker containers running MCP servers, and local stdio binaries. Environment variable expansion in `env` blocks. Environment sanitization — the CLI redacts sensitive env vars from the base environment by default to prevent unintended exposure to third-party MCP servers. Includes CLI subcommands for programmatic server management (complements manual JSON editing).

## Takeaway summary
Gemini CLI's configuration shape is close to Claude Desktop / Cursor / Cline for the `mcpServers` JSON block, so cross-host portability is easy. Two features worth noting: first-class support for Docker as a transport (documented alongside stdio and HTTP) — servers distributed as container images get a direct configuration path. Second, **default env sanitization** — the CLI scrubs sensitive env vars before spawning the server process, which is a good baseline defense against accidental token leakage to untrusted servers. Google Developers Blog and Codelabs have additional content specifically on pairing Gemini CLI with FastMCP.

## Use for
- How do I configure an MCP server in Google's Gemini CLI?
- How do I run an MCP server as a Docker container for Gemini CLI?
- What env-var-scrubbing guarantees does the host give?
- Does Gemini CLI auto-detect servers from other hosts' configs (no — explicit config required)?

## Relationship to other resources
Peer of `claude-code-mcp-docs.md`, `codex-cli-mcp-docs.md`, `warp-mcp-docs.md` among terminal-flavored hosts. The Docker-as-transport emphasis and env sanitization differentiate it.

## Quality notes
Gemini CLI has multiple doc mirrors (`geminicli.com`, `gemini-cli.xyz`, `google-gemini.github.io/gemini-cli`). The first is the primary; the others mirror. Format is stable; config key names unchanged across versions.
