# Prior art — Jupyter AI + Jupyter Collaboration

JupyterLab + Yjs-based real-time collaboration (jupyter-collaboration) + AI-as-cell-participant (jupyter-ai). Combined, **the closest existing example of "agent participates in CRDT-shared document with mixed cell types"** for our design.

## Identity

- **URLs:**
    - [github.com/jupyterlab/jupyter-collaboration](https://github.com/jupyterlab/jupyter-collaboration) — v4.3.0 March 2026, Yjs-based via `jupyter_ydoc`
    - [github.com/jupyterlab/jupyter-ai](https://github.com/jupyterlab/jupyter-ai) — v3.0.0, 4.2k stars
- **License:** BSD-3-Clause (Jupyter standard)
- **Status:** jupyter-collaboration mature; jupyter-ai under incubation but actively developed
- **Agent integration:** Built-in Jupyter MCP server; agents "read and write files, run terminal commands, and interact with notebooks"; permission system gates writes; **Claude is explicitly supported** alongside other models

## Fit to our goal

**~75% — closest model of "AI as peer in collaborative document with mixed cell types" we'll find.** Different document model (notebook cells in one document) but same architectural pattern.

**Matches:**
- Yjs-based shared state between humans and AI
- Cells as typed content units with stable IDs (markdown / code / output / raw)
- Mixed content types in one document
- AI-as-peer-participant via MCP — not chat-with-AI-on-the-side
- Real-time collab supports multiple humans + AI
- Claude supported
- File-as-source-of-truth (notebook .ipynb)

**Differs:**
- Notebook structure (one document, ordered cells), not panel-tile structure
- Cells live in one document rather than separate panels
- Domain bias toward computational notebooks; less natural fit for diagrams + viewers + general docs

## What to take, what to skip

**Take:** the entire architectural pattern is borrowable —
- Yjs + `jupyter_ydoc`-style document model for shared state
- Built-in MCP server pattern for agent-as-peer
- Permission system for agent writes
- Kernel-execution decoupled from display (input cells vs output cells; matches our bidirectional / read-only viewer split)
- Cell-stable-ID model

**Validate before adopting:** the content-triplication problem flagged in the sync-mechanism research wave — Jupyter RTC layers CRDT on filesystem on memory and can diverge. Need to understand mitigation before borrowing.

## Open questions for deep-dive

- jupyter-ai's specific MCP server tool surface — what's exposed to the agent?
- How are cell IDs generated and persisted across sessions?
- How does the kernel-execution boundary map to "agent writes a code cell, gets output cell back"?
- What bugs surface from the content-triplication issue in production?
- How does the permission system work — per-action, per-tool, granular?
- Standalone use of `jupyter_ydoc` outside a notebook context?

## Sources

- [github.com/jupyterlab/jupyter-collaboration](https://github.com/jupyterlab/jupyter-collaboration) — verified v4.3.0 March 2026
- [github.com/jupyterlab/jupyter-ai](https://github.com/jupyterlab/jupyter-ai) — verified 4.2k stars, v3.0.0
