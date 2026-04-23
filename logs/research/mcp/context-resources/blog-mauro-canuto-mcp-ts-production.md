# Building MCP Servers the Right Way — Production-Ready Guide in TypeScript (Mauro Canuto)

## Identification
- url: https://maurocanuto.medium.com/building-mcp-servers-the-right-way-a-production-ready-guide-in-typescript-8ceb9eae9c7f
- type: blog post
- author: Mauro Canuto (CTO, hisy — healthcare data)
- last-updated: active
- authority level: community

## Scope
TypeScript-focused production guide. Covers monorepo architecture (Turborepo) for managing multiple MCP servers, type definition with Zod, handler functions, tool registration, and three concrete lessons from practice: TypeScript/ESM import issues (resolved with `tsdown`), mandatory `structuredContent` field requirements the author hit in production, and STDIO logging constraints. References a GitHub repo for the implementation. Testing, deployment, and security are called out as follow-up topics (not covered in this post).

## Takeaway summary
Value is in the three specific pain-points — not generic "design your tools well" advice, but artifacts from actually shipping. The TS/ESM import issue bites every TypeScript MCP server that compiles to ESM and gets imported from a CJS host; `tsdown` is one mitigation path. The `structuredContent` field clarification matters for any server returning rich tool output — omission produces subtle bugs clients handle inconsistently. The STDIO-logging constraint echoes the canonical "no stdout" rule, worth re-hearing with a TS-specific example. Skim for the lessons-learned, skip the architecture section (Turborepo monorepo is the author's preference, not a spec requirement).

## Use for
- Which TypeScript/ESM import pitfalls hit production MCP servers?
- When is `structuredContent` mandatory?
- How does the "no stdout in stdio" rule manifest in TypeScript?

## Relationship to other resources
Complements the TS SDK README with field-report depth. Overlaps with the best-practices synthesis articles but more concrete on TS-specific gotchas.

## Quality notes
Legitimate technical content, not SEO filler. Author disclosed connection to hisy (healthcare product) — the post is light on that promo. Promised follow-ups on testing/deployment/security may or may not have been published.
