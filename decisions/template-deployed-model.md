# Template/Deployed Model

## Context

Plugin rules and conventions are authored in the plugin source tree but consumed from project directories (`.claude/rules/`, `.claude/ocd/conventions/`). Agents editing files need to know which copy is the source of truth to avoid edits being overwritten on next init.

## Options Considered

**No distinction** — single copy of each file. Disqualified: plugins need to deploy files to project directories for Claude Code to discover them, so two copies are inherent to the deployment model.

**Path-based convention** — document in CLAUDE.md that `plugins/` paths are sources and `.claude/` paths are deployed. Disqualified: agents frequently edit the wrong copy because the rule requires remembering path semantics; no in-file signal when reading a deployed copy.

**Comment header with source path** — deployed files include `<!-- Source: plugins/.../file.md -->`. Disqualified: hardcoded paths break across installation contexts (local dev vs marketplace vs user customization).

**Frontmatter type field** — `type: template` on source files, `type: deployed` on deployed copies. Init script replaces the value during deployment by modifying only the frontmatter block.

## Decision

Frontmatter `type: template` / `type: deployed`. Init scripts (`init.py`, `_init.py`) copy template to destination, then `stamp_deployed()` replaces the type value within the frontmatter block only. Comparison logic applies the stamp in memory before comparing bytes to determine Current/Outdated/Replaced status.

## Consequences

- Enables: agents see which copy they are editing when they read the file; works regardless of installation context; no path coupling between template and deployed copies
- Constrains: every rule and convention markdown file must have frontmatter; init scripts must handle the stamp replacement correctly; `stamp_deployed()` is duplicated in two init scripts
- Trade-off: the stamp replacement uses string replacement scoped to frontmatter block to avoid accidentally replacing matching strings deeper in the file
