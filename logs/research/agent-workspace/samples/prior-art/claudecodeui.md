# Prior art — claudecodeui (CloudCLI)

Browser-served UI wrapping Claude Code with file explorer + git explorer + terminal + chat + MCP management panels. Mobile/web-friendly. Built for remote-from-phone use.

## Identity

- **URL:** [github.com/siteboon/claudecodeui](https://github.com/siteboon/claudecodeui)
- **License:** AGPL-3.0 — **flagged**: meaningful consideration for any derivative
- **Status:** v1.30.0 April 2026, active
- **Stack:** Browser-served on a port
- **Agent integration:** Wraps Claude Code natively; reads same `~/.claude` config as the CLI

## Fit to our goal

**~65% — browser-served, port-based, multi-panel around Claude Code.** Real and active. But panels are passive (one-way), and AGPL license is a meaningful consideration for any derivative.

**Matches:**
- Browser delivery on a port ✓
- Mobile-friendly layout
- Multi-panel layout
- Claude Code-native (reads the same config as the CLI)
- MCP management panel exposed
- Self-host

**Differs:**
- Panels are one-way — no agent introspection of panel state
- AGPL-3.0 license may complicate any derivative or fork that combines with non-AGPL code
- No CRDT layer
- Built primarily for remote-from-phone use case, not multi-panel-on-laptop

## What to take, what to skip

**Take:** the MCP management panel pattern (where the user can see and configure MCP servers); mobile-responsive layout decisions; remote-access architecture; Claude Code config-reading approach.

**Validate before adopting:** AGPL implications. If the project's recommended path forks or composes with this, the AGPL contagion question must be answered.

## Open questions for deep-dive

- Panel architecture — custom vs library? What's the layout system?
- Session lifecycle — how does it handle Claude Code session management?
- Remote-access auth model — what protects the port?
- AGPL compatibility with our project's MIT direction — would forking + extending trigger AGPL obligations on the workspace as a whole?
- Specific terminal-panel implementation
- Specific git-panel implementation

## Sources

- [github.com/siteboon/claudecodeui](https://github.com/siteboon/claudecodeui) — v1.30.0 April 2026, AGPL-3.0
