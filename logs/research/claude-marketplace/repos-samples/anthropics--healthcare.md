# Sample

Mirrors of `https://github.com/anthropics/healthcare`. Anthropic-owned marketplace of "Skills for healthcare workflows including clinical trials, prior authorization review, and FHIR API development." 203 stars; default branch `main`; last commit 2026-01-16 (sha `c382e94`, merge of PR #31); 7 plugins.

## Marketplace manifest layout

### Multi-plugin owned-aggregator marketplace

Single `.claude-plugin/marketplace.json` at repo root. Top-level `name: "healthcare"` (matches the repo name). 7 plugins — three skill-carving plugins use `source: "./"` (repo root); four MCP plugins use `source: "./<plugin-dir>"` (`./cms-coverage`, `./npi-registry`, `./pubmed`, `./icd10-codes`). No `$schema` field.

### Top-level `metadata` wrapper variants

`metadata.{description, version}` wrapper — `metadata.version: "1.0.0"`, `metadata.description: "Skills for healthcare workflows …"`. No top-level `description`. `metadata.pluginRoot` absent. `owner.{name, email}` declared (`Anthropic`, `support@anthropic.com`) but no `owner.url`. The marketplace-level `version: 1.0.0` covers the whole catalog and is the only machine-readable version for the three skill-carving plugins (which have no `plugin.json`).

## Plugin source binding

### Skill-carving via shared root + `skills` override

Three plugins (`clinical-trial-protocol`, `prior-auth-review`, `fhir-developer`) declare `source: "./"`, `strict: false`, and carve out a single skill directory via the marketplace-entry `skills` array (e.g., `"skills": ["./clinical-trial-protocol-skill"]`). Each carve maps 1:1 plugin-to-skill while sharing the repo root as their `source`, avoiding per-plugin `.claude-plugin/plugin.json` files. Skill-carving plugins intentionally have no `plugin.json`; an installer cannot read a plugin-level version — relies on the containing marketplace's `metadata.version` (single coarse version covering all three carved plugins simultaneously).

### Relative source pointing to subdirectory

Four MCP plugins use `source: "./<plugin-dir>"` (e.g., `./cms-coverage`) with their own `plugin.json` housing `mcpServers`. These take the implicit-true `strict` default.

### `strict` field default

`strict: false` explicit on exactly the three skill-carving plugins. Absent on the four MCP-only plugins (implicit `strict: true`).

## Per-plugin discoverability metadata

### Category + tags pair

Every plugin (all 7) declares `category: "healthcare"` and a 3–5-element `tags` array (e.g., `["fhir","hl7","api","interoperability","smart-on-fhir"]`). No `keywords`. Uniform across all entries.

## Version coordination

### No plugin-level version

The three skill-carving plugins have no `plugin.json` at all — only the marketplace entry and `SKILL.md`. There is no per-plugin version concept; the only versionable artifact is the marketplace tag. The marketplace-entry `version` field is also absent on all entries.

### Single source of truth (`plugin.json` only)

For the four MCP plugins, `plugin.json` is authoritative and each declares `"version": "1.0.0"`.

## Channel distribution

### No pinning surface

No channel split. Single `v1.0.0` tag plus absence of `CHANGELOG.md` mean consumers tracking `main` versus the tag cannot easily diff intervening skill changes.

## Tag and release lifecycle

### Single lifetime tag with drift

Single annotated tag `v1.0.0` at sha `f778439` exists on `main`'s linear history (published 2026-01-09), yet `main` has continued to advance (latest commit 2026-01-16, a week after the release). No subsequent tag cut for those merges, so `main` drifts from the only released version with no user-visible channel to opt in to.

## Plugin-component registration

### Marketplace-entry-only definition (no `plugin.json`)

The three skill-carving plugins have no `.claude-plugin/plugin.json`; the marketplace entry's `skills` array (combined with `strict: false`) is the entire definition. Each owns only a single skill — the carving could be replaced by per-plugin `plugin.json` files inside each skill directory, but choosing carving instead centralizes plugin metadata in `marketplace.json` at the cost of not having a place to record per-plugin version history.

### Inline `mcpServers` definition in `plugin.json`

The four MCP plugins use inline `mcpServers` config objects in `plugin.json` (no external `.mcp.json`). Each `mcpServers` entry uses `"type": "http"` with a hosted URL. No process spawn, no command, no env vars.

## Component composition

### Skills (universal)

3 skill directories (`clinical-trial-protocol-skill/`, `prior-auth-review-skill/`, `fhir-developer-skill/`), each with `SKILL.md` plus `references/`, some with `scripts/` and `assets/`.

### MCP servers

Four MCP plugins (three authored by deepsense.ai, one by Anthropic) declared via inline `mcpServers` blocks in their `plugin.json` files (no sibling `.mcp.json`). Each uses `"type": "http"` with a hosted URL.

### Composition shapes

Hybrid marketplace: skill-carving plugins + MCP-only plugins in one manifest. Three skill plugins with `source: "./"` + `skills` override coexist with four MCP-only plugins with `source: "./<dir>"` + their own `plugin.json` housing `mcpServers`. Two structurally different plugin shapes share one `marketplace.json`.

## Server runtime (MCP)

### Remote HTTP MCP

The four MCP plugins use `"type": "http"` with a hosted URL. No local process, no command, no env vars beyond auth. Three authored by deepsense.ai; one by Anthropic.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directories in any plugin, no CLI wrappers. Python scripts live under each skill's `scripts/` and are called by the skill itself, not exposed as user-runnable CLIs.

## Dependency installation

### No managed install — pure shell/markdown

Skill plugins ship Python scripts as user-side prerequisites with no managed install. `clinical-trial-protocol-skill` README "Requirements" calls for "Python with scipy and numpy" and ships `scripts/sample_size_calculator.py`. No `requirements.txt`, no `pyproject.toml`, no hook-driven install. The README delegates to "Python with scipy and numpy" as a user-side prerequisite — a user without those packages will hit a runtime `ImportError` inside the skill with no corrective guidance. Other skills have no runtime deps. MCP plugins are remote HTTP MCP servers with no client-side install.

## User configuration and authentication

### No user-supplied config

No `userConfig` declared on any plugin. The skills are content-driven and the MCP servers are remote HTTP endpoints with no user-supplied credentials surfaced at install time.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks. No hooks of any kind in any plugin.

## Session context loading

### No session-context loading

No SessionStart hook, no UserPromptSubmit hook, no `hookSpecificOutput.additionalContext` observed. No SessionStart matcher applies.

## Live monitoring

### `monitors.json` absent

No `monitors.json` in any plugin.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `plugin.json` declares the schema-level `dependencies` field. The only tag (`v1.0.0`) covers the whole marketplace, not an individual plugin — the `{plugin-name}--v{version}` cross-plugin pinning mechanism is not exercised.

## Testing

### No tests

No test directory, no test files anywhere in the tree.

## CI workflow shape

### CI workflows present but no tests

4 workflows in `.github/workflows/`: `claude-code-review.yml`, `claude-skill-review.yml`, `claude.yml`, `release.yml`. Three of four install Claude Code plugins from sibling Anthropic marketplaces and run agent-driven review (no pytest, no linting, no validators). `claude-code-review.yml` triggers on `pull_request: [opened, synchronize, ready_for_review, reopened]` and installs `code-review@claude-code-plugins` from `https://github.com/anthropics/claude-code.git` to run `/code-review:code-review`. `claude-skill-review.yml` triggers on the same PR events plus `workflow_call` (reusable) with `CLAUDE_CODE_OAUTH_TOKEN` secret; detects changed `SKILL.md`-containing directories via `git diff --name-only origin/${{ github.base_ref }}...HEAD` (after `fetch-depth: 0` checkout) and runs one job per affected skill via dynamic matrix (`matrix.skill: fromJson(needs.detect-skills.outputs.skills)`) computed from `find . -name SKILL.md`, installing `example-skills@anthropic-agent-skills` from `https://github.com/anthropics/skills.git` and invoking skill-creator to comment on the PR. `release.yml` triggers on `push: tags: ['v*']`. `claude.yml` is a general `@claude` responder using `anthropics/claude-code-action@v1`. The `claude-skill-review.yml` declares `workflow_call` with required `CLAUDE_CODE_OAUTH_TOKEN` secret, implying it is callable from other workflows, but no caller exists in this repo — possibly reused by sibling Anthropic repos.

### `@claude` mention responder

`claude.yml` triggers on `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review` events, gated on `@claude` mention. Uses `anthropics/claude-code-action@v1` to turn the repo into an agent-addressable surface for ad-hoc questions and patches.

### Action-pinning conventions

Tag-pinned (`actions/checkout@v4`, `anthropics/claude-code-action@v1`, `softprops/action-gh-release@v1`). No SHA pinning. No caching declared.

## Marketplace validation

### No validation

No `validate.yml`, no pre-commit hook, no `claude plugin validate` invocation in CI. No frontmatter validation, no hooks.json validation. Marketplace.json has no structural validation gate — invalid JSON or a reference to a deleted skill directory would only surface at install time. The two review workflows are semantic reviewers (Claude-in-the-loop), not schema validators.

### LLM-driven PR review

`claude-code-review.yml` and `claude-skill-review.yml` install plugins from sibling Anthropic marketplaces (`anthropics/claude-code.git`, `anthropics/skills.git`) and let Claude comment on PR contents — including frontmatter and manifest changes. Not deterministic; LLM inspection rather than schema enforcement. The dynamic matrix over `find . -name SKILL.md` runs one review job per affected skill so the workflow auto-adjusts to new skills without edits.

## Release automation

### Skill-zip build via filesystem glob

`release.yml` triggered by `push: tags: ['v*']`. Iterates every directory matching `*-skill/`, zips its contents into `<skill_name>-<GITHUB_REF_NAME>.zip`, and attaches all such zips to a draft GitHub release. Uses `softprops/action-gh-release@v1` with `draft: true`, `prerelease: false`, `generate_release_notes: true`. No CHANGELOG.md in the repo. The packaging pattern `for skill_dir in *-skill/` depends on directory naming convention — the three current skill directories end in `-skill` (`clinical-trial-protocol-skill`, `prior-auth-review-skill`, `fhir-developer-skill`) and all three are released as zips. The four MCP plugin directories (`cms-coverage`, `npi-registry`, `pubmed`, `icd10-codes`) do not match `*-skill/` and are silently excluded from release artifacts; consumers must install from source via the marketplace flow. No version-vs-`plugin.json` cross-check: an MCP plugin's `plugin.json` `version` field could drift from the tag without the workflow objecting. No tag-sanity gates — no verify-tag-on-main, no version-vs-tag assertion, no regex check.

### Auto-generated release notes from commits

`release.yml` uses `generate_release_notes: true` on `softprops/action-gh-release@v1` to delegate to GitHub's built-in commit-based note generator. No `CHANGELOG.md` in repo.

## Documentation surface

### README only

Repo-root `README.md` (~50 lines). The README states "Skills are provided under Anthropic's terms of service." No `CHANGELOG.md`, no `architecture.md` at root or per plugin, no `CLAUDE.md`.

### Per-plugin README mixed coverage

Per-plugin READMEs uneven: `clinical-trial-protocol-skill/README.md` and `prior-auth-review-skill/README.md` exist; `fhir-developer-skill/` has no README (SKILL.md only). None of the four MCP plugins has a README. Skills without any README rely entirely on SKILL.md frontmatter description for discoverability.

## License declaration

### License only in README prose

LICENSE absent as a file (no `LICENSE`, no SPDX identifier). README prose: "Skills are provided under Anthropic's terms of service." GitHub's license detection returns null. The README prose is not machine-readable. Repo `license` field is null per GitHub API.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, or `PULL_REQUEST_TEMPLATE.md`.
