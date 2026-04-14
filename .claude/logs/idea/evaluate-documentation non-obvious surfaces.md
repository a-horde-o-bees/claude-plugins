# evaluate-documentation non-obvious surfaces

## Purpose

Documentation isn't confined to README.md / architecture.md / CLAUDE.md / SKILL.md. It also lives in:

- CLI help text (e.g. `plugins/ocd/skills/navigator/__main__.py:556` describes the scan command's behavior and drifted stale after the rules/conventions table separation — it still says "governance table")
- Module docstrings (the file-level `"""..."""` blocks that serve as purpose statements)
- MCP tool descriptions and `instructions=` blocks on FastMCP servers
- Frontmatter `description:` fields on skills, rules, and conventions
- Inline header purpose statements in rule/convention files

The evaluate-documentation skill, currently being redesigned from the ground up, should treat these as first-class documentation surfaces. A refactor that touches schema or behavior can leave help text, docstrings, and tool descriptions behind — the skill should catch that drift the same way it catches drift in the canonical documents.

## Documentation Currency

The skill also owns currency enforcement — the `Before modifying a system: check for its architecture reference` / `After significant structural changes: update` triggers previously in `system-documentation.md`. That rule now describes the design only (what a system is, what documents it needs, what goes where). Active rectification belongs in the skill where it can audit drift and prompt updates.

## Concrete Drift Instance

Surfaced during purpose-map session 2026-04-10: rules/conventions table separation left stale "governance table" references in `__main__.py:556`, `plugins/ocd/rules/architecture.md:13`, and `plugins/ocd/conventions/architecture.md:18,32`. The two architecture.md files are caught by the current model; the __main__.py help text is not.
