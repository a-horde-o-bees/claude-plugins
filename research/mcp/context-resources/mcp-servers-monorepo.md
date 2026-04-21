# modelcontextprotocol/servers Monorepo

## Identification
- url: https://github.com/modelcontextprotocol/servers
- type: SDK docs / reference implementations
- author: Model Context Protocol project (steering group)
- last-updated: active; some servers archived to a separate repo over time
- authority level: official

## Scope
The official reference-server monorepo. Seven active reference servers: `everything` (test server with prompts, resources, tools), `fetch`, `filesystem`, `git`, `memory`, `sequentialthinking`, `time`. Multi-language — TypeScript and Python implementations side by side, showing the same conceptual server realized in different SDKs. Distribution via npm (`npx`) and PyPI (`uvx`/`pip`). Includes configuration snippets for wiring servers into Claude Desktop and other hosts.

## Takeaway summary
These are **reference implementations**, not production templates — the README is explicit about that. They are the most useful source for answering "what does a plausible server look like in this language / for this capability?" Read `src/everything` first; it exercises every feature surface (prompts, resources, tools, logging, sampling) in one server and is the closest thing to a canonical pattern-demonstration. `src/fetch` and `src/filesystem` show how to design access controls for sensitive capabilities. Each server's README includes the exact Claude Desktop config snippet.

## Use for
- What does a minimal-but-complete MCP server look like in language X?
- How do I handle access controls for a filesystem / git / shell tool?
- How do I wire a reference server into Claude Desktop for local testing?
- What does the `everything` server demonstrate that my server should too (prompts + resources + tools together)?

## Relationship to other resources
The peer of `../repos/` in this research tree but captured here because the monorepo itself is a documentation resource (pattern demonstration) as much as a set of servers. Linked from `modelcontextprotocol-io-home.md` and every SDK README.

## Quality notes
The "reference, not production" caveat matters — the servers are small, sometimes missing error-handling or auth patterns that a production server must have. Use as a structural template, not a security template.
