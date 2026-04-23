# TypeScript SDK README

## Identification
- url: https://github.com/modelcontextprotocol/typescript-sdk
- type: SDK docs
- author: Model Context Protocol project (Anthropic-maintained)
- last-updated: active; README notes v2 is pre-alpha with v1.x recommended for production until Q1 2026
- authority level: official

## Scope
The official TypeScript/JavaScript SDK. Runs on Node.js, Bun, and Deno. Covers both `@modelcontextprotocol/server` and `@modelcontextprotocol/client` packages, Streamable HTTP + stdio transports, Express / Hono / Node-HTTP middleware adapters, OAuth helpers, and a Standard-Schema-based validation story that lets you plug in Zod v4, Valibot, or ArkType without the SDK privileging one. README funnels detail to `docs/server.md`, `docs/client.md`, and the `examples/` tree (tools, resources, prompts, auth).

## Takeaway summary
Use v1.x for anything you ship this year; v2 is pre-alpha until Q1 2026. Tool/prompt input schemas go through Standard Schema, so pick your validator (Zod if you want the widely-known option, Valibot for smaller bundles, ArkType for TS-native types) and the SDK consumes whichever. Transports ship in-box (Streamable HTTP for production remotes, stdio for local); the middleware packages handle mounting an MCP server inside an existing Express / Hono / Node-HTTP app. Auth helpers cover both server-side (verifying tokens) and client-side (OAuth flows) paths.

## Use for
- What's the current supported TS SDK major and when does v2 become recommended?
- How do I mount an MCP server inside an existing Express or Hono app?
- Which validator should I use for tool inputs?
- What's the client-side OAuth flow shape in Node?
- Does it run on Deno / Bun?

## Relationship to other resources
TypeScript counterpart to `python-sdk-readme.md`. Both consume the same spec. The `examples/` tree in this repo is a peer to the `modelcontextprotocol/servers` monorepo but TS-focused.

## Quality notes
README is light on code; depth lives in `docs/server.md`, `docs/client.md`, and the examples. Note the v1 vs v2 distinction — readers landing in Q1-2026 may see the guidance flip.
