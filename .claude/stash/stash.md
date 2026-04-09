# Stash

Ideas, future work, and unaddressed observations for this project. A holding area between noticing and doing — entries come in fast, move out when addressed. Managed by the stash MCP server.

- **[ocd-status skill display]** — show available skills with prerequisite install commands in status output
- **[Rule propagation to non-ocd plugins]** — pre-commit hook gutted of rule propagation; rules refactored and the set that needs propagating has changed; redesign which rules propagate and rebuild the hook + guard patterns + tests
- **[Settings vs allowed-tools redundancy]** — evaluate whether project settings.json permission patterns (e.g. mcp__plugin_blueprint_blueprint-research__*) are redundant now that skills declare allowed-tools in frontmatter; allowed-tools applies only during skill execution while settings.json applies globally, so determine which patterns can be removed from settings.json
- **[Cross-MCP orientation]** — once friction/decisions/stash/notes MCPs exist as peers, may need a unified view (workflow rule, orchestrator guide, or per-MCP cross-references in `instructions`) to help the agent disambiguate which MCP to reach for in capture situations; each MCP can self-describe its own scope but the boundaries between peers may not be cleanly self-describable
- **[purpose-map: show unattached files]** — add a function to purpose-map that lists project files not attached to any component; surfaces gaps in coverage so the model grows by what's actually been analyzed rather than by blanket-adding for completeness; would likely cross-reference component_paths with navigator's paths_list
- **[Convention gate hook]** — block Edit/Write until agent reads applicable conventions → [detail](convention-gate-hook.md)
- **[Convention loading on read]** — extend conventions to fire on read with idempotency guard; unlocks moving PFN/SAN out of always-on rules into a SKILL.md convention → [detail](convention-loading-on-read.md)
