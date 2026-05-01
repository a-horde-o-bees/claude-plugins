# Prior art — Marimo

Reactive Python notebook with explicit agent-as-cell-participant via ACP (Agent Client Protocol). **One of the gold-standard precedents for AI integration in cell-based workspaces** alongside jupyter-ai.

## Identity

- **URL:** [marimo.io](https://marimo.io/) + [github.com/marimo-team/marimo](https://github.com/marimo-team/marimo)
- **License:** Apache-2.0 (research-stated)
- **Status:** Actively developed; AI integration shipped with ACP-based tool surface
- **Agent integration:** ACP (Agent Client Protocol) — tool surface mirrors user editing operations at the cell level; Claude support

## Fit to our goal

**~65%.** Different domain (Python notebooks vs general-purpose workspace) but the cell-level agent pattern is exactly transferable.

**Matches:**
- Agent-as-cell-participant (not chat-with-AI-on-the-side)
- ACP-based tool surface — agent operations mirror user editing semantics
- Reactive execution model — output auto-derives from inputs
- Claude support
- File-as-source-of-truth
- Open-source, self-host

**Differs:**
- Python-only — narrower content-type scope
- Notebook structure, not panel-tile workspace
- Single-language reactive model — doesn't generalize to mixed content types directly

## What to take, what to skip

**Take:** the ACP-based agent surface design (tool calls mirror user editing operations); the reactive execution model (worth studying for any panel that should re-render when input changes — e.g., a query-result panel that re-runs on data change); cell-as-stable-unit pattern.

**Skip:** Python-only assumption; notebook-document structure.

## Open questions for deep-dive

- Stable cell IDs — research flagged issue #3177 not yet shipped. What's the current state?
- ACP specification maturity — is it a well-defined protocol or still informal?
- Reactive boundaries — how does Marimo handle agent edits that would trigger reactive cascades? Are agent edits batched?
- How would this lift to non-Python content (markdown, diagrams, tables)?
- Performance under concurrent agent + human edits in the reactive model?
- Comparison with jupyter-ai's MCP-based tool surface — same pattern, different protocol?

## Sources

- [marimo.io](https://marimo.io/)
- [github.com/marimo-team/marimo](https://github.com/marimo-team/marimo)
- ACP — Agent Client Protocol (Marimo's agent integration layer)
