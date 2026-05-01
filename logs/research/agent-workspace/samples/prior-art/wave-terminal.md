# Prior art — Wave Terminal

Modern panel-aware terminal — block system + `wsh` IPC. Markets as "AI-native"; the claim is unverified per interface-mechanism research (docs URL 404s). Useful as a precedent for panel-aware terminal architecture.

## Identity

- **URL:** [waveterm.dev](https://www.waveterm.dev/) + [github.com/wavetermdev/waveterm](https://github.com/wavetermdev/waveterm)
- **License:** Apache-2.0 (research-cited)
- **Stars:** ~20k (research-cited; verify)
- **Status:** Active; Apache-2.0
- **Agent integration:** Marketing claims "AI-native"; documentation page for AI features 404s; **integration mechanics unverified**

## Fit to our goal

**~40% — panel-system + IPC primitives at terminal level.** Useful as a model for "panel-aware terminal" approach if we ever go terminal-multiplexer route. Disqualified as primary interface mechanism per research (terminal content ceiling can't render canvas / PDF / viewer panels).

**Matches:**
- Block / panel system at the terminal level
- IPC between blocks (`wsh`)
- Layout persistence
- Cross-platform terminal substrate
- Active project, large adoption signal

**Differs:**
- Terminal-bound — doesn't satisfy the canvas / PDF / viewer panel requirements in our goal
- "AI-native" claim is unverified
- Not Claude Code-specific
- Apache-2.0 (vs MIT) — license consideration but not blocking

## What to take, what to skip

**Take:** the block system + `wsh` IPC pattern for panel-to-panel communication (worth studying as a model even if our interface is browser); layout-persistence approach; cross-platform considerations.

**Skip:** terminal as the interface (our goal requires canvas / PDF / viewer panels — content ceiling is real per the interface research); the unverified AI-native claim.

## Open questions for deep-dive

- What does Wave's "AI-native" actually mean? The docs URL (`docs.waveterm.dev/features/wave-ai`) returned 404 in research; the homepage uses the term without describing integration mechanics.
- What blocks are supported beyond terminal — does Wave have any non-text panels?
- What's the agent integration shape — direct API calls? MCP? Custom?
- Roadmap issue #2168 ("Wave Agent Mode") — what's its status?
- Production-readiness signals — adoption beyond stars?
- Layout-persistence schema — borrowable?

## Sources

- [waveterm.dev](https://www.waveterm.dev/)
- [github.com/wavetermdev/waveterm](https://github.com/wavetermdev/waveterm)
- Issue #2168 — "Wave Agent Mode" (research-cited)
