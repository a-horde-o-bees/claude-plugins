# Prior art — mcp_excalidraw

Reference implementation of "canvas-as-MCP-introspectable-panel" — 26 MCP tools split between mutation (`create_element`, `align_elements`) and **introspection** (`describe_scene`, `get_canvas_screenshot`, `query_elements`).

## Identity

- **URL:** [github.com/yctimlin/mcp_excalidraw](https://github.com/yctimlin/mcp_excalidraw)
- **License:** Research-cited; verify on read
- **Stack:** Two-process design — canvas web server on `:3000` + MCP server over stdio
- **Status:** v2.0, active; Claude Code skill included

## Fit to our goal

**~30% — single panel type, but the canonical example of agent-introspectable-canvas via MCP.**

**Matches:**
- Panel-state agent introspection via MCP tools (`describe_scene`, `get_canvas_screenshot`, `query_elements`)
- Web server on port + MCP stdio split — useful architecture for a panel
- Canvas as a panel type
- Claude Code-specific skill included

**Differs:**
- Single-purpose (canvas only), not workspace
- No shared state with other panels
- No layout persistence beyond the canvas itself
- Process-per-panel rather than unified workspace

## What to take, what to skip

**Take:** the entire tool design for the canvas panel type — split between mutation and introspection, with specific named operations (`describe_scene`, `get_canvas_screenshot`, `query_elements`, `create_element`, `align_elements`). This is the template for any future "diagram" panel in our workspace.

**Skip:** the single-panel limitation (we want the canvas as one of many panels in a workspace); the per-canvas server-on-port (we want one workspace server hosting many panels).

## Open questions for deep-dive

- How do the web server and MCP server share state — file-based, IPC, shared memory?
- Whether the canvas can persist across sessions
- How Claude-specific is the design — would it work with other agents?
- Performance with large canvases
- The 26-tool surface — which ones earn their keep, which are convenience?
- Is `get_canvas_screenshot` essential, or do `describe_scene` + `query_elements` cover most needs (token-efficiency question)?

## Sources

- [github.com/yctimlin/mcp_excalidraw](https://github.com/yctimlin/mcp_excalidraw)
