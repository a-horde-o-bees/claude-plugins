# Rules Architecture

How the rules system delivers always-on agent guidance.

## Auto-Loading Mechanism

Claude Code automatically loads all markdown files under `.claude/rules/` recursively into agent context at session start. This is a Claude Code platform feature — no plugin code is involved in the loading itself. The plugin's contribution is deploying rule files to `.claude/rules/<plugin>/` subfolders.

Files are loaded as system context visible to the agent throughout the session. The agent follows them as operating instructions.

## Governance Registration

Although rules auto-load through Claude Code's built-in mechanism, they are also registered in the governance server's `rules` table by path. Registration enables:

- **`governance_match`** — can include all registered rules when `include_rules=True` (used during governance evaluation). By default, rules are excluded from `governance_match` results since they're already in agent context.
- **`governance_unclassified`** — rule files are excluded from the unclassified report so they aren't flagged as missing convention coverage.

The `rules` table stores only the entry path and git_hash. Rules have no pattern columns because they apply universally — they are agent guidance, not file-type standards.

## Pattern Semantics

Rules carry `includes: "*"` frontmatter for consistency with the governance file format, but the pattern is not stored or evaluated — Claude Code auto-loads every rule file regardless, and `governance_match` with `include_rules=True` returns whole-rule inclusion rather than per-pattern matching. File-type scoping is a convention concern, not a rule concern; guidance that should apply only to specific file types belongs in a convention.

## Template and Deployment

Same mechanism as conventions:

- **Templates** — `plugins/ocd/rules/` in the plugin source (flat, no subfolder)
- **Deployed copies** — `.claude/rules/ocd/` in the user's project (per-plugin subfolder)

Edit deployed copies. The `sync-templates.py` script propagates deployed → template changes before commits. `/init` deploys templates to the project.

## Design Principles Structure

The design principles rule (`design-principles.md`) is the root of the governance dependency chain. It uses a specific structural convention:

- Each principle is a section with a heading, purpose statement, and bullets
- Bullets use two forms: **declarative** (general guidance) and **trigger** (gate-action format for case-specific situations)
- The file carries a recurrence heuristic — recurring failures signal missing principles

This structure is documented in the governance-md.md convention, which applies to all governance files.
