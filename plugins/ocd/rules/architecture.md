# Rules Architecture

How the rules system delivers always-on agent guidance.

## Auto-Loading Mechanism

Claude Code automatically loads all markdown files in `.claude/rules/` into agent context at session start. This is a Claude Code platform feature — no plugin code is involved in the loading itself. The plugin's contribution is deploying rule files to this directory.

Files are loaded as system context visible to the agent throughout the session. The agent follows them as operating instructions.

## Governance Registration

Although rules auto-load through Claude Code's built-in mechanism, they are also registered in the navigator's governance database with `auto_loaded = 1`. This registration enables:

- **`governance_match`** — can include rules when `include_rules=True` (used during governance evaluation). By default, rules are excluded from `governance_match` results since they're already in context.
- **`governance_order`** — rules participate in topological ordering. Since rules are foundational (other governance entries build on them via `governed_by`), they appear at level 0.
- **`governance_unclassified`** — rules with `matches: "*"` provide universal coverage, so files matching rules aren't flagged as unclassified.

## Pattern Semantics

Rules typically use `matches: "*"` — they apply universally regardless of which file is being worked on. This reflects their nature as behavioral guidance rather than file-specific content standards.

Specific patterns on rules are permitted but uncommon. A rule with `matches: "*.py"` would only fire when Python files are the target, which is usually a convention's job. The distinction: rules with specific patterns still auto-load (the agent always sees them), but the pattern communicates scope of applicability.

## Template and Deployment

Same mechanism as conventions:

- **Templates** — `plugins/ocd/rules/` in the plugin source
- **Deployed copies** — `.claude/rules/` in the user's project

Edit deployed copies. The `sync-templates.py` script propagates deployed → template changes before commits. `/ocd-init` deploys templates to the project.

## Design Principles Structure

The design principles rule (`ocd-design-principles.md`) is the root of the governance dependency chain. It uses a specific structural convention:

- Each principle is a section with a heading, purpose statement, and bullets
- Bullets use two forms: **declarative** (general guidance) and **trigger** (gate-action format for case-specific situations)
- The file carries a recurrence heuristic — recurring failures signal missing principles

This structure is documented in the governance-md.md convention, which applies to all governance files.
