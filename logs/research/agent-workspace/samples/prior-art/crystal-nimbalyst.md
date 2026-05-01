# Prior art — Crystal / Nimbalyst

Multi-worktree Claude Code orchestration UI — terminal + chat + diff + editor + logs panels around concurrent Claude Code sessions. Renamed from Crystal to Nimbalyst Feb 2026; both names still in use.

## Identity

- **URL:** [github.com/stravu/crystal](https://github.com/stravu/crystal) (renamed Nimbalyst)
- **License:** Research-stated active; verify on read
- **Stack:** Electron desktop app
- **Status:** Renamed Feb 2026; both names valid; multi-worktree session orchestration
- **Agent integration:** Drives Claude Code CLI directly across multiple worktrees

## Fit to our goal

**~60% — multi-panel Claude Code orchestration.** Strong precedent for "panels around Claude Code" but Electron desktop only and panels are one-way (Claude emits, panels render).

**Matches:**
- Multi-panel layout for Claude Code
- Multi-worktree support — relevant to the user's multi-repo workflow
- Claude Code-specific integration
- Self-host (Electron locally)

**Differs:**
- Electron desktop, not browser-served
- Panels are one-way — no agent introspection of panel state
- Recent name change suggests strategy churn — the orchestration-layer category is volatile (per the existing-implementations research, Roo Code shutting down, Goose moving orgs, Vibe Kanban sunsetting)
- No CRDT layer for shared state

## What to take, what to skip

**Take:** the multi-worktree pattern for parallel session management; per-panel display roles (terminal / diff / editor / logs); SetupTasks / Dashboard UX patterns; multi-Claude-Code orchestration insights.

**Skip / replace:** one-way panel design (replace with bidirectional via CRDT-peer or MCP-tool surface); Electron desktop wrapper (replace with browser-served).

## Open questions for deep-dive

- Why the Crystal → Nimbalyst rename? What's different in Nimbalyst version?
- How is multi-worktree state managed? Cross-worktree communication?
- Is there a programmatic API the workspace could borrow from, or is it strictly UI?
- What was the design intent that drove the multi-worktree pattern?
- Has there been public discussion of the rename / strategy shift that informs the volatility risk?

## Sources

- [github.com/stravu/crystal](https://github.com/stravu/crystal)
- DeepWiki: [Crystal architecture](https://deepwiki.com/stravu/crystal/2-architecture) (research-cited)
