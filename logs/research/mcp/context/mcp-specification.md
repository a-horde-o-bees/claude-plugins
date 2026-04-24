# MCP Specification

## Identification
- url: https://modelcontextprotocol.io/specification/latest
- type: spec
- author: Model Context Protocol project (Anthropic-led, open governance)
- last-updated: 2025-11-25 (schema revision slug in spec URL)
- authority level: official

## Scope
The authoritative protocol specification for MCP. Defines the base JSON-RPC 2.0 wire format, stateful connection lifecycle, capability negotiation between hosts/clients/servers, and the feature surfaces on each side (server: resources, prompts, tools; client: sampling, roots, elicitation). Normative RFC 2119 language ("MUST", "SHOULD", "MAY") — this is the document you quote when a design question turns on what the protocol requires vs. recommends vs. permits. Links to the machine-readable `schema.ts` in the `modelcontextprotocol/specification` repo.

## Takeaway summary
MCP is a JSON-RPC 2.0 protocol with explicit capability negotiation. A server author must decide which of the three server feature groups (resources, prompts, tools) to offer, and must handle the additional utilities the spec prescribes (progress, cancellation, logging, error reporting, configuration). The spec is explicit that security is not enforced at the protocol layer — implementers MUST build consent, authorization, and sampling-approval flows into the host. Tool descriptions and annotations from untrusted servers are untrusted input. This is the normative reference; everything else in the ecosystem (SDKs, hosts, frameworks) is a conforming implementation.

## Use for
- What messages must a server handle to be spec-compliant?
- Which feature groups are optional vs. required?
- What does capability negotiation look like on the wire?
- What are the MUST/SHOULD/MAY expectations for security, consent, and sampling?
- What utilities (progress, cancellation, logging) does the protocol define?
- What is the current revision slug and where is the machine-readable schema?

## Relationship to other resources
Canonical source-of-truth. Every SDK README, framework guide, and host integration doc is a projection of this spec. When SDK docs and the spec disagree, the spec wins — or the SDK is behind. The TypeScript schema linked from the spec is the single source for message shapes.

## Quality notes
Dense and normative — optimize for lookup, not linear reading. Version-slugged URL means older revisions remain addressable; always confirm you're reading `/specification/latest` or the revision your target SDK implements.
