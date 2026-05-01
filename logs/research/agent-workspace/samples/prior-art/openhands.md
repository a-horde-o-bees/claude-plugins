# Prior art — OpenHands

Self-host agent IDE with VS Code Web IDE + persistent Chromium browser + VNC desktop + terminal — multi-panel browser delivery, agent-introspectable surfaces, model-agnostic. **Most mature self-host agent IDE.**

## Identity

- **URL:** [github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
- **License:** MIT
- **Stack:** REST + WebSocket server, runs locally or in container; agent SDK; LiteLLM for model abstraction
- **Status:** Most mature self-host agent IDE; Software Agent SDK paper Nov 2025; active
- **Agent integration:** Model-agnostic via LiteLLM — Anthropic explicitly supported

## Fit to our goal

**~70% — full agent IDE pattern, but the agent's chat surface is OpenHands' own, not Claude Code's CLI.** Architectural orientation differs.

**Matches:**
- Self-host on a port (REST + WebSocket); local or containerized
- Multi-panel browser delivery (VS Code Web + Chromium + VNC + terminal)
- Each panel exposed to the agent as an MCP-like tool surface — agent reads tool results from each surface
- Layout configurable; shared workspace state (event-sourced)
- Anthropic Claude supported

**Differs:**
- Own chat UI (replaces Claude Code's CLI rather than embedding it)
- Event-sourced state model rather than CRDT
- Opinionated full-stack agent harness rather than composable workspace
- Higher operational footprint (Chromium + VNC + ...) than our minimum

## What to take, what to skip

**Take:** the substrate-as-MCP-tools pattern (browser, terminal, file editor each exposed as agent-callable tools); event-sourced workspace history pattern; permission/approval model for agent actions; SDK architecture for cleaner agent integration.

**Skip / replace:** OpenHands' own chat UI (we want Claude Code as the chat surface); the heavyweight per-environment containers (we want WSL-native).

## Open questions for deep-dive

- Could OpenHands be reframed to embed an external agent (Claude Code) rather than driving its own chat UI? Plugin point?
- What's the layout configurability beyond the defaults?
- Multi-repo / cross-project support model?
- How does the cwd / project boundary work — does it carry over between sessions?
- What's the resource cost of running the full stack (browser + VNC + terminal) locally?
- Specific lessons from the SDK paper (Nov 2025) on agent-IDE architecture?

## Sources

- [github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
- [Software Agent SDK paper (arXiv 2511.03690)](https://arxiv.org/html/2511.03690v1)
- [docs.openhands.dev](https://docs.openhands.dev/sdk/guides/agent-browser-use)
