# Pass 3 Refinements — Bin 8

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

(none)

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Pass 2 Go-modules build path now applied.** Both Go SDK samples (`mark3labs--mcp-go.md`, `metoro-io--mcp-golang.md`) previously had no `Build and packaging` section because the Go-modules path didn't exist in the consolidated when Pass 2 ran. Pass 2's refinement was accepted into consolidated as `Build and packaging > Go modules (\`go.mod\` / \`go.sum\`)` — Pass 3 has now added this section to both samples with the `go.mod` module-path / Go-version-constraint facts that were previously orphaned. No further refinement needed; this resolves the Pass 2 structural-concern entry.

- **`microsoft--playwright-mcp.md` cross-corpus phrasing removed.** The `Capability gating via tool subsets at install time` description previously said "Author explicitly noted this as a different gating axis than the \`--toolsets\`/\`--read-only\` model used elsewhere." The "elsewhere" reference is cross-corpus phrasing that compares the sample to other entities. Rewritten to frame the contrast within the entity itself: "The author explicitly frames this as a different gating axis than \`--toolsets\` / \`--read-only\` style flags." Cross-sample comparison removed; the per-sample claim about the author's framing is preserved.

- **`metoro-io--mcp-golang.md` Go version constraint not surfaced.** The README and captured repo evidence does not surface a specific Go version constraint (unlike mark3labs's Go 1.25.5+ floor). The `Build and packaging > Go modules` section notes this absence rather than fabricating a constraint. Reconciler may want a stylistic note that "version constraint not surfaced" is a valid description shape rather than a gap to fill.

- **`metoro-io--mcp-golang.md` HTTPS-with-custom-auth experimental status.** Pass 2 already flagged this as in-progress / partial-coverage under `Authentication > Application-delegated (SDK provides nothing)` and `Transport > Custom or experimental transports`. Pass 3 confirms placement is stable; no new refinement.

- **`microsoft--playwright-mcp.md` test stack still underspecified.** Pass 2 noted the test framework wasn't extracted; placed under `Test stack > No tests / not surfaced`. Pass 3 inherits this placement — no additional evidence available.

- **`marlonluo2018--pandas-mcp-server.md` PyPI publication still unverified.** Pass 2 hedged the placement under both `Source clone with editable install` (definite) and `PyPI via uvx (zero-install runner)` (hinted). Pass 3 leaves the dual placement as-is — the README hint is real evidence even if publication isn't verified.

- **`modelcontextprotocol--servers.md` MCP Roots dual placement.** Pass 2 surfaced that Filesystem's MCP Roots support fits both `Capability surface > MCP Roots participation` (capability) and `Configuration delivery > Host-supplied protocol-level config (MCP Roots)` (config delivery). Pass 3 confirms both placements remain — they describe the same underlying mechanism from two angles, and both roles are legitimate vantages.
