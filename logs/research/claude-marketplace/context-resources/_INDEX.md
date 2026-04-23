# Marketplace Context Resources — Research Index

Authoritative sources consumed by per-repo research agents. Each file answers specific schema / prescription questions so agents don't need to re-fetch docs during inspection.

## How to use

- Agents reference these files when determining whether a repo's choice is docs-prescribed (★), docs-valid (☆), or docs-silent.
- When a repo's implementation contradicts docs, cite the specific prescription from the relevant context file.
- All four context files were fetched on 2026-04-20; regenerate if docs change materially.

## Contents

- [docs-plugins-reference.md](docs-plugins-reference.md) — complete plugin.json schema, component locations, hook events, environment variables, plugin caching, CLI commands. Includes the docs-worked-example for dependency installation (`diff -q` + `rm` retry pattern — silent, no systemMessage).
- [docs-plugin-marketplaces.md](docs-plugin-marketplaces.md) — marketplace.json schema, plugin source types (relative/github/url/git-subdir/npm), strict mode, channel distribution (★ two-marketplace pattern), reserved names blocklist, enterprise managed-settings.
- [docs-hooks.md](docs-hooks.md) — hook events, handler types (command/http/prompt/agent), JSON output schema (`continue`, `suppressOutput`, `systemMessage`, `decision`, `hookSpecificOutput.additionalContext`), exit code semantics, matcher patterns.
- [docs-plugin-dependencies.md](docs-plugin-dependencies.md) — plugin-to-plugin dependency schema, semver ranges, `{plugin-name}--v{version}` tag convention, conflict error codes. v2.1.110+ requirement.

## Authority cross-reference

**Most authoritative for each question:**

- Plugin.json schema / component defaults → `docs-plugins-reference.md`
- Marketplace.json schema / plugin sources → `docs-plugin-marketplaces.md`
- Hook JSON output / exit codes → `docs-hooks.md`
- Plugin-to-plugin dependencies → `docs-plugin-dependencies.md`
- Dependency install pattern (worked example) → `docs-plugins-reference.md` (the `diff -q` + `rm` pattern)
- userConfig sensitive handling / keychain quota → `docs-plugins-reference.md`
- Reserved marketplace names → `docs-plugin-marketplaces.md`
- Version authority (relative vs non-relative sources) → `docs-plugin-marketplaces.md`
- Channel distribution (two-marketplace stable/latest) → `docs-plugin-marketplaces.md`
- Agent frontmatter constraints → `docs-plugins-reference.md`
- Monitor version floor (v2.1.105+) → `docs-plugins-reference.md`
- Plugin dependency version floor (v2.1.110+) → `docs-plugin-dependencies.md`

## Gaps disclosed

- Claude Code changelog not captured as a separate resource. Version-floor info is scattered through the four docs pages above.
- `docs-discover-plugins` (installation flow) not captured — consumer-side, not authoring-side. Referenced in the marketplaces docs but not critical for pattern research.
- `docs-plugins` (tutorials / create plugins) not captured separately — supersets covered by plugins-reference.
- `docs-skills`, `docs-sub-agents`, `docs-mcp`, `docs-settings` — relevant for skill/agent/MCP specifics but each is its own discipline. If research surfaces skill-specific questions (schema, discovery), fetch then.
