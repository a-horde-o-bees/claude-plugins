# docs-plugin-marketplaces

**URL**: https://code.claude.com/docs/en/plugin-marketplaces
**Type**: Official Claude Code documentation
**Authority**: Official — authoritative for marketplace.json schema, plugin source types, channel distribution, and managed-marketplace restrictions.

## Scope

Complete documentation for creating and hosting plugin marketplaces: the marketplace.json schema, all plugin source types (relative, github, url, git-subdir, npm), strict mode, channel distribution (two-marketplace stable/latest pattern), reserved names, CLI commands (`plugin marketplace add/list/remove/update`), and enterprise managed-marketplace restrictions.

## Key prescriptions

### marketplace.json schema

- **Required top-level fields**: `name` (kebab-case), `owner` (object with `name`, optional `email`), `plugins` (array).
- **Optional metadata wrapper**: `metadata.description`, `metadata.version`, `metadata.pluginRoot` (prepends base dir to relative plugin paths).
- **Reserved marketplace names** (blocklist): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`. Also names impersonating official ones.

### Plugin entries

- **Required per-plugin**: `name`, `source`.
- **Optional**: `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`, `category`, `tags`, `strict`, plus all component path fields (`skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`).

### Plugin source types

- `"./path"` — relative string (must start with `./`; resolved from marketplace root; requires git-based marketplace distribution — URL-based won't work).
- `{ source: "github", repo: "owner/repo", ref?, sha? }` — GitHub source.
- `{ source: "url", url: "...", ref?, sha? }` — Any git URL.
- `{ source: "git-subdir", url, path, ref?, sha? }` — Sparse clone of subdirectory.
- `{ source: "npm", package, version?, registry? }` — npm package.

### Strict mode

- `strict: true` (default) — plugin.json is authoritative; marketplace entry supplements.
- `strict: false` — marketplace entry is entire definition; plugin.json must not declare conflicting components (else fails to load). Used for carving out different skill selections per marketplace entry.

### Channel distribution

- **Prescribed pattern for stable/dev channels**: two separate marketplaces with different `name` values, each pinning the same plugin repo to a different `ref` (or SHA). Worked example in docs: `stable-tools` + `latest-tools`, each pointing at same `code-formatter` repo at different refs.
- **Version floor requirement**: the plugin's `plugin.json` must declare a different `version` at each pinned ref — if both refs have the same manifest version, Claude Code treats them as identical and skips the update.

### Version authority (coupled with source type)

- **Relative-path plugins**: set version in marketplace entry.
- **All other plugin sources (github/url/git-subdir/npm)**: set version in plugin.json.
- **Never both**: plugin manifest wins silently; mismatches silently drift.

### Enterprise controls

- `extraKnownMarketplaces` in managed settings — auto-register marketplaces; prompts users to install.
- `strictKnownMarketplaces` in managed settings — allowlist of permitted marketplace sources (exact-match by default; regex via `hostPattern` or `pathPattern`).
- `enabledPlugins` — pre-enable plugins in managed settings.

### Validation CLI

- `claude plugin validate .` — validates marketplace.json, plugin.json, skill/agent/command frontmatter, hooks.json.
- `/plugin validate .` — equivalent interactive form.

### Container seeding

- `CLAUDE_CODE_PLUGIN_SEED_DIR` — read-only pre-populated plugin cache for container images.
- Seed directory mirrors `~/.claude/plugins` structure; auto-updates disabled for seed marketplaces.
- Colon/semicolon-separated paths for multiple seed layers.
- `CLAUDE_CODE_PLUGIN_CACHE_DIR` — build-time override that installs directly into seed path.

### Environment variables

- `GITHUB_TOKEN` / `GH_TOKEN` — private GitHub marketplace auth (background auto-update can't use credential helpers).
- `GITLAB_TOKEN` / `GL_TOKEN` — GitLab.
- `BITBUCKET_TOKEN` — Bitbucket.
- `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` — preserve stale cache on git pull failure (for offline environments).
- `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` — override default 120s git timeout.

## Use for

- Verifying marketplace.json fields against the schema.
- Distinguishing plugin sources (github vs url vs git-subdir vs npm) and their required/optional fields.
- Resolving version-authority questions (relative vs non-relative sources).
- Identifying reserved names that would block publishing.
- Channel distribution: docs prescribe two-marketplace pattern for stable/latest.
- Enterprise-facing consumers: `strictKnownMarketplaces`, `extraKnownMarketplaces`, seed directories.
