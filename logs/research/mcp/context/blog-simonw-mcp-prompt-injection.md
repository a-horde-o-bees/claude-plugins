# MCP Has Prompt Injection Security Problems (Simon Willison)

## Identification
- url: https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/
- type: blog post
- author: Simon Willison
- last-updated: 2025-04-09
- authority level: community — Simon Willison is a widely-cited practitioner on LLM security

## Scope
Argument that MCP has unresolved prompt-injection vulnerabilities fundamental to the design of connecting LLMs to untrusted tool metadata. Walks three concrete attack patterns: **rug pulls / tool shadowing** (malicious servers redefining tool descriptions post-install or overriding tools from other servers), **tool poisoning** (hidden instructions embedded in tool descriptions — worked example: an `add()` tool with metadata that coerces the LLM into exfiltrating private files), **WhatsApp hijacking** (a fake "fact of the day" tool that redirects outbound messages, using whitespace / base64 to obfuscate data theft from users glancing at the tool description). Treats the spec's "SHOULD" clauses around human-in-the-loop confirmation as practical "MUSTS." Calls out: "no effective mitigation exists yet."

## Takeaway summary
Read this before shipping any MCP server that handles sensitive data or runs in a context with other servers. The threat model is **cross-server interaction**: a single "good" server is relatively safe; two servers installed together, where one is compromised, open tool-shadowing and cross-server data-exfiltration paths that the protocol itself does not prevent. Client and server authors both get actionable guidance: clients must surface tool descriptions prominently and alert on changes; servers should treat all prompt content as potentially hostile and avoid e.g. `os.system()` with unescaped args. Users should curate installed tools and watch for dangerous combinations. This is the canonical "here's why the protocol-layer security story is not enough" reference in the ecosystem.

## Use for
- What are the realistic attack patterns against MCP servers in the wild?
- Why isn't server-side OAuth the whole security story?
- How should a client surface tool descriptions to make injection visible?
- What server-side defensive coding patterns prevent the worst outcomes?

## Relationship to other resources
Complements `mcp-authorization-tutorial.md` (which covers auth but not prompt-injection) and the security-pitfalls section of the spec. Pairs with `blog-elastic-mcp-attack-defense.md` for a fuller threat catalog.

## Quality notes
Simon Willison is an authoritative voice on LLM security; posts are durable references. Specific CVEs may have landed since April 2025, but the structural arguments here remain correct.
