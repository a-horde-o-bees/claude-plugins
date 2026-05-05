# Sample

Mirrors of `https://github.com/anthropics/claude-plugins-official`. Anthropic-managed curated directory mixing in-repo internal plugins (`/plugins`), thin MCP-wrapper external plugins (`/external_plugins`), and SHA-pinned upstream references in the marketplace manifest. 17,422 stars; default branch `main`; last commit 2026-04-20 (`777db5c` — "Add liquid-skills plugin (#1507)"); 145 plugin entries.

## Marketplace manifest layout

### Mixed-provenance composition

Single `.claude-plugin/marketplace.json` at repo root (74,104 bytes, 1,724 lines, 145 plugin entries) hosting in-repo plugin directories under `./plugins/*` (48 string-source entries into `/plugins` or `/external_plugins`), SHA-pinned subdirectories of external repos (`git-subdir` with `sha`), clone-the-whole-repo entries (`url` with no `path` — 72 of these), and a lone `github` shorthand entry (`stagehand`, via `{source: "github", repo: "browserbase/agent-browse"}`). Anthropic-authored content gets full review and code in the repo; partner content is distributed by SHA-pinned reference.

### `$schema` declaration on marketplace.json

Marketplace declares `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"`. No CI step validates against the schema directly; field is editor-assistance only.

### Top-level `metadata` wrapper variants

Flat top-level fields only — `$schema`, `name: "claude-plugins-official"`, `description`, `owner: {name: "Anthropic", email: "support@anthropic.com"}`, `plugins: [...]`. No `metadata` wrapper object.

## Plugin source binding

### `url` clone with `sha` pin

72 of 145 plugin entries use source kind `url` (clone-any-URL form). The `git-subdir` subset (24 entries) carries `sha` fields actively maintained by the `bump-plugin-shas.yml` workflow — only source kind in this manifest with reproducible pinning.

### Relative source pointing to subdirectory

48 entries use string-form relative sources, all starting with `./plugins/<name>` or `./external_plugins/<name>` — relative paths into the repo.

### `git-subdir` into upstream

24 entries use `git-subdir` source kind, each carrying a `sha` field actively maintained by the bump workflow. This is the only source kind in this manifest with reproducible pinning across time.

### `source: github` with explicit coords or `ref` pinning

One entry (`stagehand`) uses the `github` shorthand: `{source: "github", repo: "browserbase/agent-browse"}`. Effectively unused — 1 of 145 entries.

### Skill-carving via shared root + `skills` override

Two entries with `skills` override on the marketplace entry: `netsuite-suitecloud` carves 3 specific skills out of `packages/agent-skills`; `stagehand` declares `./.claude/skills/browser-automation`. Both are `strict: false`, confirming the docs pattern that `strict: false` lets the marketplace entry carve component subsets from an upstream repo.

### `strict` field default

131/145 entries take the implicit-true default (no `strict` key). 14 entries set `strict: false` explicit (all 12 `*-lsp` plugins plus `netsuite-suitecloud` and `stagehand`). No `strict: true` is written explicitly.

## Per-plugin discoverability metadata

### Mixed-by-origin metadata

Different field sets per provenance tier in the same `plugins[]` array — `category` is present on 118/145 entries; `tags` on only 3 entries (all set to `["community-managed"]`); `keywords` on 1 entry (stagehand). 27 entries carry no `category`. Categories used: `automation`, `database`, `deployment`, `design`, `development` (60), `learning`, `location`, `math`, `monitoring`, `productivity` (26), `security`, `testing`. The 27 `category`-less entries degrade the `/plugin > Discover` browsing experience; `tags` (3 entries) and `keywords` (1 entry) are inconsistently adopted across siblings.

## Version coordination

### Marketplace-side pin via source ref

13 entries have a `version` field on the marketplace entry (12 LSP plugins at `1.0.0` plus `stagehand` at `0.1.0`); the rest rely on `plugin.json`. Among internal plugins where both could be set, only `ralph-loop`, `code-simplifier`, `claude-code-setup`, `claude-md-management`, and `learning-output-style` carry `version: "1.0.0"` in `plugin.json`; most internal `plugin.json` files omit `version` entirely. For external entries (`url` and `git-subdir`), upstream `plugin.json` versions are not surfaced — the source-side `sha` (where present) is the version contract; consumer pinning surface is the source ref.

### No plugin-level version

`session-report/` plugin directory has no `.claude-plugin/plugin.json` (confirmed by direct API fetches of both `plugins/session-report/.claude-plugin/plugin.json` and `plugins/session-report/.claude-plugin/`, both 404); ships only `LICENSE` and `skills/`. The 12 LSP plugin directories also have no `.claude-plugin/plugin.json` — for those the marketplace entry is `strict: false` with full `lspServers` config (the intended "entry-is-entire-definition" shape). Marketplace-entry `version` and `plugin.json` `version` can disagree, with no validation to align them.

## Channel distribution

### No pinning surface

Single `marketplace.json` on `main` is the only distribution. No tags, no release branches (0 tags, 0 releases observed via `gh api`). Consumers have no pinning mechanism — `/plugin install X@claude-plugins-official` fetches from `main` tip. For `git-subdir` sources this is partially mitigated by the SHA pins the bump workflow maintains (so upstream plugin code is reproducible once pinned), but the marketplace manifest itself has no channel.

### SHA pinning per external entry

For external `git-subdir`-sourced plugins, the `sha` field on each entry acts as a per-plugin pin — the marketplace itself tracks HEAD but each external plugin is frozen at the SHA the maintainer chose. Effectively a per-entry channel pin without a global stable/latest split.

## Tag and release lifecycle

### No tags at all

Repo has zero tags. "Release" means whatever `main` currently holds; rolling back requires checking out a specific commit. No CHANGELOG.md, no GitHub releases. Active branches are all PR feature branches (e.g., `add-liquid-skills`, `add-plugin/aikido`, ≥30 visible in first page).

## Plugin-component registration

### Default convention discovery

Every internal `plugin.json` examined (12 samples) declares only `name`, `description`, `author`, and occasionally `version`. No plugin uses explicit `skills`, `commands`, `agents`, `hooks`, `mcpServers`, or `lspServers` path arrays in `plugin.json`. All component wiring relies on default-discovery conventions (`commands/*.md`, `agents/*.md`, `skills/*/SKILL.md`, `hooks/hooks.json`, `.mcp.json`).

### Marketplace-entry-only definition (no `plugin.json`)

Two shapes both used here. `session-report/` ships no `plugin.json` — its marketplace entry is strict-default and the directory holds only `LICENSE` and `skills/` (likely silent-load-failure). 12 LSP plugin directories (clangd-lsp, pyright-lsp, etc.) also ship no `plugin.json` — for those the marketplace entry is `strict: false` with a full `lspServers: {...}` block carrying the entire plugin definition; the plugin directory holds only `README.md` + `LICENSE`.

## Component composition

### Skills (universal)

Skills ship across many internal plugins — skill-creator, plugin-dev, frontend-design, mcp-server-dev, and others.

### Commands

Commands present in plugins like commit-commands, code-review, ralph-loop, example-plugin.

### Agents

Agents ship in plugins like feature-dev, code-simplifier, pr-review-toolkit, plugin-dev, hookify.

### Hooks

Hooks present in 5 plugins: hookify, ralph-loop, security-guidance, explanatory-output-style, learning-output-style.

### MCP servers

`example-plugin` carries `.mcp.json` with `{example-server: {type: http, url: ...}}`; all 15 external plugins ship a `.mcp.json` at plugin root.

### Composition shapes

LSP-server-only "hollow" plugin shape applies to all 12 `*-lsp` plugin directories. Output-style emulation via SessionStart `additionalContext` is used by `explanatory-output-style` and `learning-output-style` (no `output-styles/` directory exists; the docs feature is rebuilt as a SessionStart hook emitting the entire instruction blob).

## Skill authoring conventions

### Standard frontmatter

Skills ship with the standard frontmatter set; no plugin in this repo uses non-standard frontmatter fields like `disable-model-invocation` or `context: fork`.

## Agent declaration conventions

### Standard fields plus model / color

Observed on `feature-dev/agents/code-architect.md`: `name`, `description`, `tools`, `model`, `color`. Example values: `model: sonnet`, `color: green`, `tools: Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch, KillShell, BashOutput`.

### Plain tool-name list

Agents declare `tools:` as plain comma-separated names (`Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch, KillShell, BashOutput`) rather than permission-rule syntax like `Bash(uv run *)`. No tool uses the permission-pattern form in the sample examined.

## Server runtime (MCP)

### Runtime-fetched server via `npx -y`

`playwright` external plugin uses `command: npx, args: [@playwright/mcp@latest]`.

### Pinned PyPI wheel via `uvx`

`serena` external plugin uses `command: uvx, args: [--from, git+https://github.com/oraios/serena, serena, start-mcp-server]`.

### Docker-launched MCP server

`terraform` external plugin uses `command: docker, args: [run, ..., hashicorp/terraform-mcp-server:0.4.0]` (pinned tag).

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory exists in any internal or external plugin (confirmed by iterating all 34 internal plugin directories and all 15 external plugin directories). Hook scripts use shebangs (`#!/usr/bin/env bash`, `#!/usr/bin/env python3`) but are invoked from `hooks.json` via `command: bash "${CLAUDE_PLUGIN_ROOT}/...` or `python3 ${CLAUDE_PLUGIN_ROOT}/...`, not as bin entrypoints. Hookify's Python hooks import from `core.*` and `utils.*` inside the plugin by adding `CLAUDE_PLUGIN_ROOT` to `sys.path` at the top of each hook script.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Every `hooks.json` observed uses `${CLAUDE_PLUGIN_ROOT}` — always as `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py` or `bash "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.sh"` (hookify, ralph-loop, security-guidance, explanatory-output-style, learning-output-style).

## Dependency installation

### Delegated to PyPI runner (`uvx`)

External-plugin MCP servers use ad-hoc runtime fetch via the MCP launcher rather than plugin-managed install. `serena` is fetched via `uvx --from git+https://github.com/oraios/serena, serena, start-mcp-server`.

### No managed install — pure shell/markdown

Marketplace is content-only (skills, commands, agents, hooks, MCP wrappers); no plugin installs Python/Node packages at session start. External-plugin MCP servers that are runtime-fetched (`npx @playwright/mcp@latest`, `uvx --from git+... serena`) do their own install ad-hoc via the MCP launcher, not via a plugin-install hook.

## User configuration and authentication

### No userConfig, env-var only

External plugins use bare `${ENV}` substitution directly, bypassing `userConfig`. `external_plugins/github/.mcp.json` uses `Authorization: "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"`; `external_plugins/terraform/.mcp.json` passes `TFE_TOKEN=${TFE_TOKEN}` via `docker run -e`. These env vars are expected to exist in the user's shell environment, not declared by the plugin. A user installing `github` has to read `.mcp.json` (or `README.md`) to learn that `GITHUB_PERSONAL_ACCESS_TOKEN` must be set.

## Session context loading

### `additionalContext` payload at SessionStart

`explanatory-output-style/hooks-handlers/session-start.sh` and `learning-output-style/hooks-handlers/session-start.sh` are bash scripts using a here-doc that prints JSON to stdout with `hookSpecificOutput.additionalContext` carrying the entire instruction blob. Used to emulate the deprecated "explanatory" and "learning" Claude Code output styles. SessionStart matcher absent on either plugin — fires on all sub-events. The `hooks-handlers/` directory name is a local convention for these two plugins (distinct from `hooks/` which holds `hooks.json`); separates the registration (`hooks/hooks.json`) from the handler scripts.

## SessionStart matcher scope

### Empty matcher (all sub-events)

`explanatory-output-style` and `learning-output-style` SessionStart hooks declare no matcher, firing on all sub-events (`startup|clear|compact`).

## Tool-use enforcement

### Hook-only enforcement (frontmatter is documentation)

Two plugins register PreToolUse hooks. `hookify/hooks/hooks.json` runs PreToolUse with no matcher (fires on all tools); runs `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse.py`, timeout 10s; evaluates user-defined rules from `.claude/hookify.*.local.md` files. `security-guidance/hooks/hooks.json` runs PreToolUse with `matcher: "Edit|Write|MultiEdit"`, runs `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/security_reminder_hook.py` (no timeout declared); warns about security issues in file edits. Hookify also registers a PostToolUse with no matcher, `posttooluse.py`, timeout 10s. PermissionRequest/PermissionDenied hooks are absent across all inspected hooks.json files.

## Hook output contract

### `systemMessage` for human-readable summaries

Hookify scripts `json.dumps(result)` to stdout, emitting `{"systemMessage": "..."}` JSON on every code path including error paths. Used for completion-event reports.

### `decision: "block"` for gating

Ralph-loop's Stop hook emits JSON via `jq -n` with `{decision: "block", reason: $prompt, systemMessage: $msg}` for in-session prompt re-injection — refusing the Stop event so the prompt re-feeds into the agent.

## Hook failure posture

### Fail-open posture with explicit comment contract

Every hookify hook wraps `main()` in `try/except` and exits 0 regardless, with comments like `# ALWAYS exit 0 - never block operations due to hook errors`. Top-level try/catch wrapping observed on all hookify hooks (`pretooluse.py`, `posttooluse.py`, `stop.py`, `userpromptsubmit.py`); each also wraps the initial import in its own try/except that emits a `systemMessage` on ImportError. Ralph-loop's stop-hook also exits 0 on every error path, printing to stderr but never blocking. Security-guidance is the only one without visible top-level error wrapping (the script body was not fetched but the hook registration has no timeout — if it hangs, Claude Code waits).

## Hook timeout and async philosophy

### Differentiated per-hook timeouts

Hookify declares 10s timeouts on PreToolUse and PostToolUse; ralph-loop and security-guidance declare none. Inconsistent across plugins.

## State persistence

### Plugin-local `.local.md` with YAML frontmatter

Ralph-loop's Stop hook uses `decision: "block"` with `reason: <previous-prompt-text>` to re-feed the same prompt into the agent on each Stop, implementing a self-referential work loop. Iteration counters stored in `.claude/ralph-loop.local.md` (markdown body with YAML frontmatter); session isolation via `CLAUDE_CODE_SESSION_ID`; a `<promise>TAG</promise>` escape protocol for breaking out of the loop.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `plugin.json` declares the schema-level `dependencies` field. The 12 LSP plugins are independent and flat — given the LSP "umbrella" concept, a `dependencies` chain would be a natural fit (e.g., one user-installs `typescript-lsp` which depends on a shared base) but is unused.

## Testing

### No tests

No `tests/` directory at repo root; no per-plugin `tests/` observed; `pytest.ini` / `pyproject.toml` absent at root. Quality control is review-time on PRs.

## CI workflow shape

### Multi-workflow split by trigger and concern

4 workflow files in `.github/workflows/`: `bump-plugin-shas.yml`, `close-external-prs.yml`, `validate-frontmatter.yml`, `validate-marketplace.yml`. Triggers split per concern: `validate-marketplace.yml` on `pull_request` scoped to `paths: ['.claude-plugin/marketplace.json']`; `validate-frontmatter.yml` on `pull_request` scoped to `paths: ['**/agents/*.md', '**/skills/*/SKILL.md', '**/commands/*.md']`; `bump-plugin-shas.yml` on `schedule: cron '23 7 * * 1'` (Monday 07:23 UTC) and `workflow_dispatch` with `plugin`, `max_bumps` (default 20), `dry_run` (default true) inputs; `close-external-prs.yml` on `pull_request_target: [opened]`, gated on `vars.DISABLE_EXTERNAL_PR_CHECK != 'true'`.

### Single PR-gatekeeper workflow

`close-external-prs.yml` triggers on `pull_request_target: [opened]`, gated on `vars.DISABLE_EXTERNAL_PR_CHECK != 'true'`. Uses `actions/github-script` to check the PR author's collaborator permission level via `repos.getCollaboratorPermissionLevel`; auto-closes and comments on any PR from a non-admin/non-write user, redirecting to a submission form. Org-wide submission gating implemented as a workflow rather than as repo branch-protection rules.

### Action-pinning conventions

All actions tag-based: `actions/checkout@v4`, `oven-sh/setup-bun@v2`, `actions/create-github-app-token@v1`, `actions/github-script@v7`. No SHA pinning. No `actions/cache`; `setup-bun` handles its own install with no explicit cache key. Matrix is none — all jobs run `ubuntu-latest`.

## Marketplace validation

### Schema-and-shape validators in TS

`validate-marketplace.yml` runs `bun .github/scripts/validate-marketplace.ts` and `bun .github/scripts/check-marketplace-sorted.ts`. `validate-marketplace.ts` is ~65 lines: parses JSON, checks object shape, verifies `plugins` is an array, iterates requiring `name`/`description`/`source` per entry, tracks duplicates in a `Set`. Plain TS, no zod. Validates field presence, not shape — `source` must be truthy but its discriminator isn't checked (a malformed `{source: {typo: "github"}}` object would pass). Validator also doesn't check that the referenced path (for relative sources) exists in the repo.

### Frontmatter validation by grep

`validate-frontmatter.yml` runs `validate-frontmatter.ts` using the `yaml` package with a pre-processing pass (`quoteSpecialValues`) that quotes unquoted values containing `{}[]*&#!|>%@\`` so glob patterns like `**/*.{ts,tsx}` parse. Per-type validation: agents require `name`+`description`, commands require `description`, skills require `description` or `when_to_use`. Nested `skills/<name>/agents/` etc. are explicitly excluded (treated as skill content, not plugin components). PR-only triggers, path-scoped so each validator fires only on relevant changes.

### Alphabetical-sort enforcement

`check-marketplace-sorted.ts` enforces case-insensitive alphabetical order on `plugins[].name` with a `--fix` flag that rewrites the file in place. Runs on every PR that touches `marketplace.json`. Treats the manifest like a sorted registry; CI rather than pre-commit hook is the enforcement point. New PRs adding a plugin must place it in the correct sorted position or CI fails with a `--fix` suggestion.

## Source-pin maintenance

### Scheduled bot-PR with fairness ordering

`bump-plugin-shas.yml` workflow runs on cron (Monday 07:23 UTC) and `workflow_dispatch`. Python `discover_bumps.py` script queries GitHub for the latest commit on each pinned ref (respecting `path` scope for subdirs), sorts by oldest-pinned-first ("prevents starvation under the cap"), applies up to `--max 20` bumps per run (configurable via `max_bumps` input, default 20), then a bot-signed PR is opened with label `sha-bump`. Concurrency group `bump-plugin-shas` with `cancel-in-progress: false`. First step does `gh pr list --label sha-bump --state open --jq 'length'` to skip if an open PR already exists — at most one open bump PR can accumulate at a time. Pushes with `--force-with-lease` onto a date-stamped branch `auto/bump-shas-$(date +%Y%m%d)`. Failures to fetch (404, 422 "No commit found for SHA" on force-pushed refs) are categorized as "dead" without blocking other bumps. Uses a GitHub App token (`app-id: 2812036`) rather than `GITHUB_TOKEN` because org policy forbids `GITHUB_TOKEN` from creating PRs.

## Release automation

### No release automation / manual

No `release.yml`, no release process. No CHANGELOG.md in repo. No tag-sanity gates, no release-creation mechanism, no draft releases, no CHANGELOG parsing. The closest analogue is `bump-plugin-shas.yml`, which is dependency-refresh automation, not release automation.

## Documentation surface

### README only

Repo `README.md` is ~50 lines (1,881 bytes equivalent short-form). Covers structure (`/plugins` vs `/external_plugins`), install command, contribution split (Anthropic-internal vs submission-form external), plugin structure skeleton, and a pointer to official docs.

### Per-plugin README mixed coverage

Per-plugin README present on all 34 internal plugins checked; also present on external plugins where carried (but external plugin directories generally hold only `.claude-plugin/plugin.json` + `.mcp.json` — e.g., `asana/`, `github/`, `playwright/` show no README at that level). Internal plugins always ship a README; thin external MCP wrappers usually do not.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` (0 matches), no `architecture.md` (0 matches), no `CLAUDE.md` (0 matches).

## License declaration

### No repo-root LICENSE; per-skill LICENSE only

LICENSE absent at repo root; each plugin carries its own `LICENSE` file (Apache-2.0 boilerplate, identical 11,358 bytes across internal plugins). README explicitly says "Please see each linked plugin for the relevant LICENSE file." External plugins often omit LICENSE entirely (these inherit by reference from the upstream repo they wrap). GitHub API `license: null`.

## Community health files

### Anti-contribution with auto-close gatekeeper

`close-external-prs.yml` workflow on `pull_request_target: [opened]` checks the PR author's collaborator permission level via the GitHub API and auto-closes any PR from non-admin/non-write users with a comment redirecting to a submission form. Disableable via `vars.DISABLE_EXTERNAL_PR_CHECK` repo variable. README's "Contributing" section serves in place of CONTRIBUTING.md; no `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` at root. GitHub repo custom properties indicate L2/L3 repo protection enabled.
