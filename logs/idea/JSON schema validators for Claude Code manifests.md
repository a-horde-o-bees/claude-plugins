---
log-role: queue
---

# JSON schema validators for Claude Code manifests

## Purpose

Validate `plugin.json`, `.claude-plugin/marketplace.json`, `hooks.json`, and `settings.json` against documented Claude Code shapes before runtime errors surface them. Today these files have no programmatic validation — typos in field names, missing required keys, or wrong value types become silent failures or cryptic runtime errors discovered only when Claude Code itself rejects the input.

## Approach

Author or import JSON Schemas matching Claude Code's plugin reference (https://code.claude.com/docs/en/plugins-reference). Add a `/ocd:check json-schema` dimension that walks the project's tracked JSON files, dispatches each to its applicable schema by path glob, and reports validation failures in the same `Violation` shape used by other check dimensions. Same allowlist mechanism, same exit-code behavior, same report integration.

## Out of scope

- Validating `paths.csv` content (different format, project-specific fields)
- Validating per-skill frontmatter shape (markdown-side concern, partially covered by the SKILL.md convention; could grow into its own `frontmatter-schema` dimension later)

## Dependencies

- `jsonschema` Python package — add to plugin's `pyproject.toml`
- Authoritative schemas — Claude Code documents the shapes; either hand-author or fetch if upstream publishes machine-readable schemas
