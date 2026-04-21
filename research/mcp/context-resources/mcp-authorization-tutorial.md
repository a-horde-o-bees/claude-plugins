# MCP Authorization Tutorial

## Identification
- url: https://modelcontextprotocol.io/docs/tutorials/security/authorization
- type: spec / official docs site (tutorial)
- author: Model Context Protocol project
- last-updated: active (current with spec 2025-11-25)
- authority level: official

## Scope
End-to-end OAuth 2.1 authorization tutorial for MCP servers. Covers the full handshake: initial `401 Unauthorized` + `WWW-Authenticate: Bearer` with `resource_metadata` pointer, Protected Resource Metadata discovery (RFC 9728), Authorization Server Metadata discovery (RFC 8414 or OIDC Discovery), pre-registration vs Dynamic Client Registration (RFC 7591), the user authorization flow with PKCE, and bearer-token-authenticated requests. Worked example wires a Keycloak container to a minimal server shown in TypeScript, Python (FastMCP), and C#. Concludes with a security pitfalls list: short-lived tokens, audience validation (RFC 8707 resource indicators), HTTPS-only in production, least-privilege scopes, no credentials in logs, `Mcp-Session-Id` hardening, etc.

## Takeaway summary
For remote (HTTP) MCP servers, OAuth 2.1 is the protocol-prescribed auth path. Stdio servers can use env-based credentials — OAuth is specifically for HTTP transports where the server is remote. The canonical server-side pattern: return 401 with `WWW-Authenticate: Bearer realm="mcp", resource_metadata="https://.../.well-known/oauth-protected-resource"`, serve the PRM JSON with `authorization_servers` and `scopes_supported`, validate bearer tokens on requests (introspection or local JWT validation), and reject when the `aud` claim doesn't match your resource URL. Critical implementation notes buried in the pitfalls section: never write token validation by hand (use tested libraries), always enforce audience (`aud`) matching to block token-passthrough attacks, `Mcp-Session-Id` is untrusted input and must not gate authorization, DCR may need gating in enterprise settings. The related-standards block at the bottom is the single best index for the RFCs an implementer needs: OAuth 2.1 draft, RFC 8414, RFC 7591, RFC 9728, RFC 8707.

## Use for
- How should I structure auth for a remote (HTTP) MCP server?
- What exactly goes in the `WWW-Authenticate` challenge and the PRM document?
- Which RFCs apply (OAuth 2.1, RFC 8414, RFC 7591, RFC 9728, RFC 8707)?
- What does a complete working example look like in TS / Python / C#?
- What are the most common auth pitfalls and their fixes?

## Relationship to other resources
The hands-on companion to the normative `/specification/latest/basic/authorization` section in `mcp-specification.md`. TypeScript and Python worked examples extend what's in the respective SDK READMEs.

## Quality notes
Current and high-fidelity. The Keycloak recipe is development-only; production would swap in a vetted auth server and use resource-indicator-bound audiences (RFC 8707) rather than hardcoded ones. The example token-verifier classes in Python and TS are good copy-starting-points but should be adapted for your choice of introspection vs local JWT validation.
