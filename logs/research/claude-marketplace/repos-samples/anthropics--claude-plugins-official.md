# anthropics/claude-plugins-official

## Identification

- **URL**: https://github.com/anthropics/claude-plugins-official
- **Stars**: 17,422
- **Last commit date**: 2026-04-20 (commit `777db5c` — "Add liquid-skills plugin (#1507)")
- **Default branch**: `main`
- **License**: not declared at repo level (GitHub API `license: null`); each plugin directory ships its own `LICENSE` file (the Apache-2.0 body, 11,358 bytes identical across internal plugins) — README explicitly says "Please see each linked plugin for the relevant LICENSE file"
- **Sample origin**: primary (Anthropic-owned aggregator marketplace)
- **One-line purpose**: "A curated directory of high-quality plugins for Claude Code." — Anthropic-managed directory mixing in-repo internal plugins (`/plugins`), thin MCP-wrapper external plugins (`/external_plugins`), and SHA-pinned upstream references in the marketplace manifest.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (74,104 bytes, 1,724 lines, 145 plugin entries)
- **Marketplace-level metadata**: top-level fields — `$schema`, `name: "claude-plugins-official"`, `description`, `owner: {name: "Anthropic", email: "support@anthropic.com"}`, `plugins: [...]`. No `metadata` wrapper object.
- **`metadata.pluginRoot`**: absent (no `metadata` object at all; plugin entries use per-entry `source` paths like `./plugins/<name>`)
- **Per-plugin discoverability**: `category` present on 118/145 entries; `tags` on only 3 entries (all set to `["community-managed"]`); `keywords` on 1 entry (stagehand). 27 entries carry no `category`. Categories used: `automation`, `database`, `deployment`, `design`, `development` (60), `learning`, `location`, `math`, `monitoring`, `productivity` (26), `security`, `testing`.
- **`$schema`**: present — `https://anthropic.com/claude-code/marketplace.schema.json`
- **Reserved-name collision**: no (`claude-plugins-official` is not a reserved name per `docs-plugin-marketplaces.md`)
- **Pitfalls observed**: 27 of 145 entries omit `category`, which degrades the `/plugin > Discover` browsing experience. The `tags` field (3 entries) and `keywords` field (1 entry) are inconsistently adopted; the docs reference `keywords` and `tags` as optional plugin-level fields but there's no project-wide convention about which to use.

## 2. Plugin source binding

- **Source format(s) observed** (per-entry `source` in marketplace.json): `url` 72, `string` (relative path) 48, `git-subdir` 24, `github` 1. No `npm` sources. The 48 string sources all start with `./plugins/<name>` or `./external_plugins/<name>` — relative paths into the repo.
- **`strict` field**: default-implicit `true` on 131/145 entries; `strict: false` explicit on 14 entries (all 12 `*-lsp` plugins plus `netsuite-suitecloud` and `stagehand`). No `strict: true` written explicitly.
- **`skills` override on marketplace entry**: present on 2 entries (`netsuite-suitecloud` carves 3 specific skills out of `packages/agent-skills`; `stagehand` declares `./.claude/skills/browser-automation`). Both are `strict: false`, confirming the docs pattern that `strict: false` lets the marketplace entry carve component subsets from an upstream repo.
- **Version authority**: divided. 13 entries have a `version` field on the marketplace entry (all 12 LSP plugins at `1.0.0` plus `stagehand` at `0.1.0`); the rest rely on `plugin.json`. Among internal plugins where both could be set, only `ralph-loop`, `code-simplifier`, `claude-code-setup`, `claude-md-management`, and `learning-output-style` carry `version: "1.0.0"` in `plugin.json`. Most internal `plugin.json` files omit `version` entirely. Drift risk is real: marketplace-entry `version` and `plugin.json` `version` can disagree, and nothing validates them against each other.
- **Pitfalls observed**: Source kind `url` (72 entries) uses `url` as the value of `source.source` — per `docs-plugin-marketplaces.md` this is the generic clone-any-URL form; `github` appears only once (`stagehand`, via `{source: "github", repo: "browserbase/agent-browse"}`), so the `github` shorthand is effectively unused. The `git-subdir` entries carry a `sha` field that is actively maintained by the `bump-plugin-shas.yml` workflow (see §14) — this is the only source kind with reproducible pinning.

## 3. Channel distribution

- **Channel mechanism**: no split. A single `marketplace.json` on `main` is the only distribution. No tags, no release branches (0 tags, 0 releases observed via `gh api`).
- **Channel-pinning artifacts**: absent. No `stable-tools` / `latest-tools` style dual-marketplace. Users installing this marketplace always get whatever is on `main`.
- **Pitfalls observed**: Consumers have no pinning mechanism — `/plugin install X@claude-plugins-official` fetches from `main` tip. For `git-subdir` sources this is partially mitigated by the SHA pins the bump workflow maintains (so *upstream* plugin code is reproducible once pinned), but the marketplace manifest itself has no channel.

## 4. Version control and release cadence

- **Default branch name**: `main`
- **Tag placement**: none (0 tags)
- **Release branching**: none — flat `main`-only model. Active branches are all PR feature branches like `add-liquid-skills`, `add-plugin/aikido` (≥30 visible in first page).
- **Pre-release suffixes**: none observed (no tags at all)
- **Dev-counter scheme**: absent
- **Pre-commit version bump**: no
- **Pitfalls observed**: Zero release infrastructure — no CHANGELOG, no tags, no GitHub releases. All state lives on `main`. For a first-party marketplace of this scale (145 plugins), the lack of any release pinning mechanism is notable.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — every internal `plugin.json` examined (12 samples) declares only `name`, `description`, `author`, and occasionally `version`. No plugin uses explicit `skills`, `commands`, `agents`, `hooks`, `mcpServers`, or `lspServers` path arrays in `plugin.json`. All component wiring relies on the default-discovery conventions (`commands/*.md`, `agents/*.md`, `skills/*/SKILL.md`, `hooks/hooks.json`, `.mcp.json`). The only registrations that *do* use explicit config objects live on the marketplace entry, not in plugin.json: `lspServers: {...}` on the 12 LSP plugins and `skills: [...]` on 2 plugins.
- **Components observed** (across all internal + external plugins):
    - skills — yes (skill-creator, plugin-dev, frontend-design, mcp-server-dev, etc.)
    - commands — yes (commit-commands, code-review, ralph-loop, example-plugin)
    - agents — yes (feature-dev, code-simplifier, pr-review-toolkit, plugin-dev, hookify)
    - hooks — yes, 5 plugins (hookify, ralph-loop, security-guidance, explanatory-output-style, learning-output-style)
    - .mcp.json — yes (example-plugin with `{example-server: {type: http, url: ...}}`; all 15 external plugins carry a `.mcp.json` at plugin root)
    - .lsp.json — no (LSP servers declared only in marketplace entry's `lspServers` field, not via `.lsp.json`)
    - monitors — no (no `monitors.json` observed anywhere)
    - bin — no (no `bin/` directory on any internal or external plugin)
    - output-styles — indirect. Two plugins named `explanatory-output-style` and `learning-output-style` emulate the unshipped output-style feature via `SessionStart` hooks that emit `hookSpecificOutput.additionalContext`. No `output-styles/` directory.
- **Agent frontmatter fields used**: observed on `feature-dev/agents/code-architect.md`: `name`, `description`, `tools`, `model`, `color`. Example: `model: sonnet`, `color: green`, `tools: Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch, KillShell, BashOutput`.
- **Agent tools syntax**: plain tool names separated by commas — not permission-rule syntax like `Bash(uv run *)`. No tool uses the permission-pattern form in the sample examined.
- **Pitfalls observed**: `session-report/` contains no `.claude-plugin/plugin.json` at all — the marketplace entry for it is strict-default and the plugin directory ships only `LICENSE` and `skills/`. Per `docs-plugins-reference.md`, `plugin.json` is required (at minimum with a `name` field) for a plugin to load under strict mode, so either this plugin relies on an undocumented tolerance in the loader or it fails to load cleanly. Either way, it breaks the pattern followed by every other internal plugin. The 12 LSP plugin directories (clangd-lsp, pyright-lsp, etc.) also have no `.claude-plugin/plugin.json` — for those the marketplace entry is `strict: false` with full `lspServers` config, which is the intended "entry-is-entire-definition" shape.

## 6. Dependency installation

- **Applicable**: no — no plugin in this repo installs Python/Node/etc. packages at session start. The marketplace is content-only (skills, commands, agents, hooks, MCP wrappers). External-plugin MCP servers that are runtime-fetched (`npx @playwright/mcp@latest`, `uvx --from git+... serena`) do their own install ad-hoc via the MCP launcher, not via a plugin-install hook.
- **Dep manifest format**: none
- **Install location**: not applicable
- **Install script location**: not applicable
- **Change detection**: not applicable
- **Retry-next-session invariant**: not applicable
- **Failure signaling**: not applicable
- **Runtime variant**: ad-hoc runtime fetch via MCP command strings only. `playwright` uses `command: npx, args: [@playwright/mcp@latest]`; `serena` uses `command: uvx, args: [--from, git+https://github.com/oraios/serena, serena, start-mcp-server]`; `terraform` uses `command: docker, args: [run, ..., hashicorp/terraform-mcp-server:0.4.0]`. These are not plugin-managed installs; they are launcher commands the MCP runtime invokes each session.
- **Alternative approaches**: `npx`/`uvx` ad-hoc (on the external MCP plugins, as above)
- **Version-mismatch handling**: none
- **Pitfalls observed**: There is no `SessionStart` dep-install convention here to mirror what `docs-plugins-reference.md` describes as the worked example pattern. The repo's hooks are all content-injection (explanatory/learning SessionStart) or rule-evaluation (hookify, security-guidance PreToolUse), not dependency management.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — no `bin/` directory exists in any internal or external plugin. Confirmed by iterating all 34 internal plugin directories and all 15 external plugin directories.
- **`bin/` files**: none
- **Shebang convention**: not applicable (hook scripts do use shebangs — `#!/usr/bin/env bash` and `#!/usr/bin/env python3` — but these are invoked via `command: bash "${CLAUDE_PLUGIN_ROOT}/...` or `python3 ${CLAUDE_PLUGIN_ROOT}/...` from `hooks.json`, not as bin entrypoints)
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` is used in every `hooks.json` observed (hookify, ralph-loop, security-guidance, explanatory-output-style, learning-output-style) — always as `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py` or `bash "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.sh"`
- **Venv handling (Python)**: not applicable (no managed venv; hooks just call `python3` from the user PATH)
- **Platform support**: not applicable
- **Permissions**: not applicable
- **SessionStart relationship**: not applicable
- **Pitfalls observed**: Hookify's Python hooks import from `core.*` and `utils.*` inside the plugin by adding `CLAUDE_PLUGIN_ROOT` to `sys.path` at the top of each hook script — a pattern that works but relies on `CLAUDE_PLUGIN_ROOT` being set, with a fallback that silently suppresses `ImportError` and emits `systemMessage` via JSON before `sys.exit(0)`.

## 8. User configuration

- **`userConfig` present**: no (0 matches searching marketplace.json for `userConfig`; no `plugin.json` examined declares it)
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable to `${user_config.*}` / `CLAUDE_PLUGIN_OPTION_*` — but external MCP plugins do use `${ENV_VAR}` substitution directly, bypassing `userConfig`. Examples: `external_plugins/github/.mcp.json` uses `Authorization: "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"`; `external_plugins/terraform/.mcp.json` passes `TFE_TOKEN=${TFE_TOKEN}` via `docker run -e`. These env vars are expected to exist in the user's shell environment, not declared by the plugin.
- **Pitfalls observed**: By relying on bare `${ENV}` substitution instead of `userConfig`, the external plugins provide no discoverable schema — a user installing `github` has to read `.mcp.json` (or `README.md`) to learn that `GITHUB_PERSONAL_ACCESS_TOKEN` must be set. `userConfig` with `sensitive: true` would surface this as a configurable field with secret handling, but the convention in this repo is to skip it.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 2 plugins.
    - `hookify/hooks/hooks.json` — PreToolUse with no matcher (fires on all tools); runs `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse.py`, timeout 10s. Purpose: evaluates user-defined rules from `.claude/hookify.*.local.md` files.
    - `security-guidance/hooks/hooks.json` — PreToolUse with `matcher: "Edit|Write|MultiEdit"`, runs `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/security_reminder_hook.py` (no timeout declared). Purpose: warns about security issues in file edits.
- **PostToolUse hooks**: 1 plugin. `hookify/hooks/hooks.json` — PostToolUse with no matcher, `posttooluse.py`, timeout 10s.
- **PermissionRequest/PermissionDenied hooks**: absent across all inspected hooks.json files.
- **Output convention**: stdout JSON (`{"systemMessage": "..."}`). Hookify scripts `json.dumps(result)` to stdout, including error paths. Ralph-loop's Stop hook emits JSON via `jq -n` with `{decision: "block", reason: $prompt, systemMessage: $msg}` for its in-session prompt re-injection.
- **Failure posture**: fail-open, uniformly. Every hookify hook wraps `main()` in `try/except` and exits 0 regardless, with comments like `# ALWAYS exit 0 - never block operations due to hook errors`. Ralph-loop's stop-hook also exits 0 on every error path, printing to stderr but never blocking. Security-guidance is the only one without visible top-level error wrapping (the script body was not fetched but the hook registration has no timeout — if it hangs, Claude Code waits).
- **Top-level try/catch wrapping**: observed on all hookify hooks (`pretooluse.py`, `posttooluse.py`, `stop.py`, `userpromptsubmit.py`); each also wraps the initial import in its own try/except that emits a `systemMessage` on ImportError.
- **Pitfalls observed**: Ralph-loop's Stop hook uses `decision: "block"` with the prior prompt as the `reason` to implement an in-session re-run loop — a non-obvious use of the Stop hook's block protocol to implement long-running agentic loops. Timeouts are inconsistent: hookify declares 10s, ralph-loop and security-guidance declare none.

## 10. Session context loading

- **SessionStart used for context**: yes — 2 plugins (`explanatory-output-style`, `learning-output-style`) use `SessionStart` to inject a large instruction blob via `hookSpecificOutput.additionalContext`. These emulate the deprecated "explanatory" and "learning" Claude Code output styles.
- **UserPromptSubmit for context**: hookify registers a `userpromptsubmit.py` hook, but its purpose is rule evaluation (user-defined rules from `.local.md`), not context injection.
- **`hookSpecificOutput.additionalContext` observed**: yes — verbatim in both `explanatory-output-style/hooks-handlers/session-start.sh` and `learning-output-style/hooks-handlers/session-start.sh`. The shell script is a here-doc that prints the JSON to stdout and exits 0.
- **SessionStart matcher**: none declared on either plugin — fires on all SessionStart sub-events (`startup|clear|compact`), per docs default.
- **Pitfalls observed**: The `hooks-handlers/` directory name is a local convention for these two plugins (distinct from `hooks/` which holds `hooks.json`). The convention separates the registration (`hooks/hooks.json`) from the handler scripts (`hooks-handlers/*.sh`) — unusual layout vs. the more common "hooks.json alongside its scripts in hooks/" pattern used by hookify and ralph-loop.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: No monitors anywhere in the repo; the documented monitor feature is unused by this first-party marketplace.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no (0 matches in any plugin.json examined; 0 in marketplace.json entries)
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: no — not applicable since no tags exist in this repo at all (plus the marketplace is single-manifest, so the per-plugin tag pattern from `docs-plugin-dependencies.md` doesn't fit this layout)
- **Pitfalls observed**: Given the LSP "umbrella" concept (12 LSP plugins that each wrap one language server), a `dependencies` chain would be a natural fit (e.g., one user-installs `typescript-lsp` which depends on a shared base). Instead each LSP plugin is independent and flat.

## 13. Testing and CI

- **Test framework**: none (no `tests/` directory at repo root; no per-plugin `tests/` observed; `pytest.ini` / `pyproject.toml` absent at root)
- **Tests location**: not applicable
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: yes (4 workflow files in `.github/workflows/`)
- **CI file(s)**: `bump-plugin-shas.yml`, `close-external-prs.yml`, `validate-frontmatter.yml`, `validate-marketplace.yml`
- **CI triggers**:
    - `validate-marketplace.yml` — `pull_request` scoped to `paths: ['.claude-plugin/marketplace.json']`
    - `validate-frontmatter.yml` — `pull_request` scoped to `paths: ['**/agents/*.md', '**/skills/*/SKILL.md', '**/commands/*.md']`
    - `bump-plugin-shas.yml` — `schedule: cron '23 7 * * 1'` (Monday 07:23 UTC) and `workflow_dispatch` with `plugin`, `max_bumps` (default 20), `dry_run` (default true) inputs
    - `close-external-prs.yml` — `pull_request_target: [opened]`, gated on `vars.DISABLE_EXTERNAL_PR_CHECK != 'true'`
- **CI does**: (a) marketplace JSON validation + alphabetical-sort check via bun+TS, (b) frontmatter validation across agents/skills/commands via bun+TS with custom YAML pre-quoting of glob special chars, (c) weekly SHA bump PR for outdated `git-subdir` pins, (d) auto-close PRs from non-Anthropic-members pointing them to the submission form. No tests, no linting.
- **Matrix**: none (all jobs run `ubuntu-latest`, no matrix)
- **Action pinning**: tag-based. `actions/checkout@v4`, `oven-sh/setup-bun@v2`, `actions/create-github-app-token@v1`, `actions/github-script@v7`. No SHA pinning.
- **Caching**: none (no `actions/cache`; `setup-bun` handles its own install but with no explicit cache key)
- **Test runner invocation**: not applicable (validators run directly: `bun .github/scripts/validate-marketplace.ts` and `bun .github/scripts/check-marketplace-sorted.ts`)
- **Pitfalls observed**: Zero test coverage of plugin content — frontmatter is checked structurally (name + description present on agents/commands; description OR `when_to_use` on skills) but there is no runtime test that a skill loads, a command parses, or a hook runs without error. The bump workflow uses a GitHub App token (`app-id: 2812036`) rather than `GITHUB_TOKEN` because org policy forbids `GITHUB_TOKEN` from creating PRs — this secret sharing across `-internal` and `-official` is called out in the workflow comment.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable (no release process). The closest analogue is `bump-plugin-shas.yml` which opens an automated PR to refresh `git-subdir` SHA pins — this is dependency-refresh automation, not release automation. Mechanism: Python `discover_bumps.py` script queries GitHub for the latest commit on each pinned ref (respecting `path` scope for subdirs), sorts by oldest-pinned-first ("prevents starvation under the cap"), applies up to `--max 20` bumps, then a bot-signed PR is opened with label `sha-bump`.
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable (no CHANGELOG.md in repo)
- **Pitfalls observed**: The bump workflow has a concurrency group `bump-plugin-shas` with `cancel-in-progress: false`, and a first step that `gh pr list --label sha-bump --state open --jq 'length'` to skip if an open PR already exists — so at most one open bump PR can accumulate at a time. The workflow pushes with `--force-with-lease` onto a date-stamped branch `auto/bump-shas-$(date +%Y%m%d)`.

## 15. Marketplace validation

- **Validation workflow present**: yes (`validate-marketplace.yml`, `validate-frontmatter.yml`)
- **Validator**: bun + plain TS (no zod). `validate-marketplace.ts` is ~65 lines: parses JSON, checks object shape, verifies `plugins` is an array, iterates requiring `name`/`description`/`source` per entry, tracks duplicates in a `Set`. `check-marketplace-sorted.ts` enforces case-insensitive alphabetical order on `plugins[].name` with a `--fix` flag that rewrites the file in place. `validate-frontmatter.ts` uses the `yaml` package with a pre-processing pass (`quoteSpecialValues`) that quotes unquoted values containing `{}[]*&#!|>%@\``  so glob patterns like `**/*.{ts,tsx}` parse, then per-type validation: agents require `name`+`description`, commands require `description`, skills require `description` or `when_to_use`. Nested `skills/<name>/agents/` etc. are explicitly excluded (treated as skill content, not plugin components).
- **Trigger**: `pull_request` only, path-scoped — each validator runs only when its relevant files change
- **Frontmatter validation**: yes (agents, skills/SKILL.md, commands)
- **Hooks.json validation**: no (no schema validation of `hooks.json`)
- **Pitfalls observed**: `validate-marketplace.ts` doesn't validate the shape of `source` (doesn't check that `source` is either a string or an object with a valid `source` discriminator); it only checks that the field is truthy. So a malformed `{source: {typo: "github"}}` object would pass. The validator also doesn't check that the referenced path (for relative sources) exists in the repo. The alphabetical-sort check is strict and automated — every new PR that adds a plugin must place it in the correct sorted position or CI fails with a `--fix` suggestion.

## 16. Documentation

- **`README.md` at repo root**: present — ~50 lines (1,881 bytes equivalent short-form). Covers structure (`/plugins` vs `/external_plugins`), install command, contribution split (Anthropic-internal vs submission-form external), plugin structure skeleton, and a pointer to official docs.
- **`README.md` per plugin**: present on all 34 internal plugins checked; also present on external plugins where carried (but external plugin directories generally hold only `.claude-plugin/plugin.json` + `.mcp.json` — e.g., `asana/`, `github/`, `playwright/` show no README at that level). Mixed — internal plugins always ship a README; thin external MCP wrappers usually do not.
- **`CHANGELOG.md`**: absent (0 matches)
- **`architecture.md`**: absent (0 matches)
- **`CLAUDE.md`**: absent (0 matches)
- **Community health files**: none observed at root (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`; the README's "Contributing" section serves in place of CONTRIBUTING.md). GitHub repo custom properties indicate L2/L3 repo protection enabled but no files surface in `.github/`.
- **LICENSE**: absent at repo root; each plugin carries its own `LICENSE` file (Apache-2.0 boilerplate, identical 11,358 bytes across internal plugins). GitHub API `license: null`.
- **Badges / status indicators**: absent (README has no badges, no CI-status shields)
- **Pitfalls observed**: The pattern "LICENSE per plugin, none at root" is explicit per README's "Please see each linked plugin for the relevant LICENSE file." External plugins often omit LICENSE entirely — these inherit by reference from the upstream repo they wrap. The lack of a repo-level LICENSE causes GitHub to report `license: null` even though Apache-2.0 files are present throughout.

## 17. Novel axes

- **Strict-false as "config carrier for hollow plugin directories"**: 12 of the 14 `strict: false` entries (all `*-lsp` plugins) use the marketplace entry to carry the *entire* plugin definition — the plugin directory itself holds only `README.md` + `LICENSE`, no `plugin.json`, no `skills/`, no `commands/`. The marketplace entry's `lspServers` block is literally the whole plugin. This is a deliberate structural choice: one umbrella `-lsp` plugin per language with LSP config declared centrally in marketplace.json, installable as its own unit but with no separately-versioned plugin body. This goes beyond the docs-described "carving skills" use case for `strict: false`.
- **Hybrid internal/external distribution model**: a single marketplace.json mixes (a) in-repo plugin directories under `./plugins/*` (48 string-source entries into `/plugins` or `/external_plugins`), (b) SHA-pinned subdirectories of external repos (`git-subdir` with `sha`), (c) clone-the-whole-repo entries (`url` with no `path` — 72 of these), and (d) a lone `github` shorthand. The Anthropic-authored content gets full review + code in the repo; partner content is distributed by SHA-pinned reference. Both surface uniformly through `/plugin install X@claude-plugins-official`.
- **SHA-drift remediation via scheduled bot PR**: the `bump-plugin-shas.yml` + `discover_bumps.py` pair implements a specific contract — "oldest-pinned first" fairness (`-age_days` sort), single-PR-at-a-time concurrency (label-based check), and a cap of 20 bumps per run. Failures to fetch (404, 422 "No commit found for SHA" on force-pushed refs) are categorized as "dead" without blocking other bumps. This is a reusable recipe for keeping a pinned-source marketplace fresh at predictable cadence.
- **External-PR bouncer as organizational policy**: `close-external-prs.yml` runs on `pull_request_target: [opened]`, checks author's collaborator permission level via `repos.getCollaboratorPermissionLevel`, and auto-closes + comments on any PR from a non-admin/non-write user, redirecting to a submission form. Explicitly disableable via `vars.DISABLE_EXTERNAL_PR_CHECK`. This is organizational access control implemented as a workflow rather than as repo branch-protection rules.
- **Output-style emulation via SessionStart `additionalContext`**: `explanatory-output-style` and `learning-output-style` rebuild the unshipped "output style" feature as plugins by emitting the entire instruction blob through `hookSpecificOutput.additionalContext` on SessionStart. Essentially, plugins as one-shot system-prompt modifiers. The plugin directory is just a wrapper around a single bash here-doc. Demonstrates that the hooks API can subsume a missing first-class feature.
- **Stop-hook prompt re-injection loop (ralph-loop)**: uses `decision: "block"` with `reason: <previous-prompt-text>` to re-feed the same prompt into the agent on each Stop, implementing a self-referential work loop with iteration counters stored in `.claude/ralph-loop.local.md` (markdown with YAML frontmatter), session isolation via `CLAUDE_CODE_SESSION_ID`, and a `<promise>TAG</promise>` escape protocol. Non-obvious use of the hook API as a control-flow primitive.
- **Alphabetical-sort enforcement in CI**: `check-marketplace-sorted.ts` runs on every PR that touches `marketplace.json` and fails with a `--fix` command hint if the 145-entry `plugins` array isn't in case-insensitive alphabetical order. Treats the manifest like a sorted registry and uses CI rather than pre-commit hook to enforce it.
- **Frontmatter pre-quoter for glob patterns**: `validate-frontmatter.ts`'s `quoteSpecialValues` function pre-processes frontmatter text to quote unquoted values containing YAML special chars so that glob patterns like `**/*.{ts,tsx}` parse without authors having to hand-quote them. Small convenience that shifts the burden from author to tooling.

## 18. Gaps

- Did not fetch every plugin's `README.md` body — statements about which plugins ship README files rely on directory listings only; a README could be present with unusual casing or naming.
- Did not examine `security-guidance/hooks/security_reminder_hook.py` source — failure-posture claim (no top-level try/except wrapping) is inferred from the absence of `timeout` in its hooks.json registration and from it being the only one in this sample I didn't open, not from the script body itself. Would resolve by fetching that single file.
- Did not enumerate every internal plugin's skill list — for the skill-enabled plugins only `skill-creator` was opened in depth; claims about other skill-shipping plugins (plugin-dev, mcp-server-dev, frontend-design, playground, etc.) rely on directory structure and marketplace entry metadata.
- GitHub Code Search API returned 404/auth errors for cross-repo queries, so the `userConfig` / `architecture.md` / `CHANGELOG.md` absence claims rely on raw-file fetches of specific paths plus directory listings, not on an exhaustive content-search. A missing file in a non-standard location could be overlooked. Would resolve by a full recursive tree API call at the repo root.
- Did not inspect the 72 `url`-source partner plugins' upstream repos — no claim is made about what those plugins actually ship, only about how they are referenced in this marketplace's manifest.
- None remaining — session-report's lack of `plugin.json` was confirmed by direct API fetches (both `plugins/session-report/.claude-plugin/plugin.json` and `plugins/session-report/.claude-plugin/` return 404).
