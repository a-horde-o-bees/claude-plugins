# Prior art — OpenCove

Spatial development workspace built on an infinite 2D canvas — agents, terminals, tasks, and notes coordinated on one canvas rather than buried in tabs and chat threads. **Single highest-fidelity match found in the research wave.**

## Identity

- **URL:** [github.com/DeadWaveWave/opencove](https://github.com/DeadWaveWave/opencove)
- **License:** MIT (verified)
- **Stack:** Electron + React + TypeScript; xyflow for canvas; xterm.js + node-pty for terminals; Vitest + Playwright tests
- **Status:** Alpha (v0.2.0 April 27 2026, 414 commits, 16 contributors, 51 releases) — verified via direct fetch
- **Agent integration:** Designed for Claude Code and Codex specifically; model-agnostic at the terminal layer; recommends global install of either

## Fit to our goal

**~85%.** The closest existing approximation found.

**Matches:**
- Configurable layout of mixed panel types (terminals, notes, tasks, agents)
- Layout persistence via "space archives"
- Headless mode for browser access — significant for our self-host-on-WSL story
- Self-host (Electron locally + headless server option)
- Claude Code as a primary integration target
- Spatial canvas treats panels as first-class objects (freely positioned)

**Differs:**
- Infinite 2D canvas vs tiled layout — design vocabulary difference. The user prefers tiled (primarily 2-panel left/right)
- No documented CRDT-peer agent pattern — agents run inside terminals, not as Yjs peers with shared cursors and edit operations
- Layout state stored but not surfaced as introspectable graph (no `panels_showing(id)` analog)
- Alpha quality — risk profile is real

## What to take, what to skip

**Take:** the space-archive layout-persistence pattern; xterm.js + node-pty terminal-panel implementation; xyflow canvas substrate (alternative to react-mosaic if we ever go canvas); Claude Code + Codex integration shape.

**Skip / replace:** Electron wrapper (we'd want browser-only); terminal-as-agent-channel (replace with CRDT-peer per Electric pattern); freeform canvas (replace with tiles per user preference).

## Open questions for deep-dive

- How is layout configurability surfaced — free positioning only, or is there a snap-to-grid / tile-mode option?
- What's the space-archive serialization schema?
- How does the headless mode work — is it a server emitting state changes that a browser client consumes?
- How are agents wired to terminals — direct stdin/stdout, or through an MCP layer?
- What's the failure profile of the alpha — what bugs are open?
- Multi-repo / cross-project workflow support (matches the user's WSL multi-repo case)?

## Sources

- [github.com/DeadWaveWave/opencove](https://github.com/DeadWaveWave/opencove) — verified MIT, alpha v0.2.0 April 2026, 51 releases
