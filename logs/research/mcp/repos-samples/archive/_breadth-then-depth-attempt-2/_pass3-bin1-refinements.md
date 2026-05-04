# Pass 3 Refinements — Bin 1

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

- **Azure archived-with-successor convention still unresolved.** Azure--azure-mcp.md continues to carry facts about the *successor* `microsoft/mcp` (host integrations, `Repository layout > Umbrella consolidation` description) rather than the archived original. Pass 2 raised this; Pass 3 inherited the same shape. No structural-tree decision yet on how to mark "this evidence describes the successor, not the sampled entity." Reconciler may want a convention (sample-level frontmatter tag, separate sample for the successor, or a note in the consolidated about how umbrella-consolidation samples should resolve).

- **DaInfernalCoder transport selection mechanism still not surfaced.** The README does not document a transport-selection mechanism; HTTP transport is inferred from Anthropic Agent SDK usage. Listed under `Transport > Streamable HTTP` without a `Selection mechanism` sub-path. Pass 2 flagged this; the gap persists because the underlying repo evidence is genuinely thin, not because of a tree mismatch.

- **FuzzingLabs hand-rolled-per-server pattern is unusual.** 38 separate hand-rolled MCP implementations rather than one shared framework, all absorbed into `Server runtime > Python with hand-rolled MCP`. The fit is reasonable but loses a real signal — the "monorepo of independent hand-rolls" pattern is structurally different from a single hand-rolled server. Reconciler may consider whether `Repository layout > Monorepo of independent servers` already captures this axis sufficiently (it does, in this sample's case), or whether the runtime path should split.
