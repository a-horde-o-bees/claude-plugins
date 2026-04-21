# IgorGanapolsky/ThumbGate

## Identification

- **URL**: https://github.com/IgorGanapolsky/ThumbGate
- **Stars**: 16
- **Last commit date**: 2026-04-21 (pushed_at, UTC)
- **Default branch**: main
- **License**: MIT (SPDX: MIT, root `LICENSE`)
- **Sample origin**: primary (community)
- **One-line purpose**: "Self-improving agent governance: thumbs-up/down → Pre-Action Gates that block repeat AI mistakes" — an npm-published MCP server that captures feedback, distills lessons, and injects PreToolUse prevention rules; the `.claude-plugin/` manifest wraps the same published npm package as a Claude plugin.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root; co-located with `plugin.json`, a plugin-level `README.md`, and an mcpb `bundle/` subdirectory (`icon.png`, `icon.svg`, `server/index.js`).
- **Marketplace-level metadata**: no `metadata` wrapper. Top-level `name`, `version`, `owner` {`name`, `email`}, `plugins[]`. No top-level `description`.
- **`metadata.pluginRoot`**: absent (pluginRoot not declared anywhere; source binding is `npm`, so no local root applies).
- **Per-plugin discoverability**: single-plugin marketplace (`thumbgate`). Entry carries `category: "developer-tools"`, `tags: [pre-action-gates, ai-agent-safety, mcp, memory, workflow-hardening]`, `keywords: [claude-desktop, desktop-extension, pre-action-gates, ai-agent-safety, mcp, memory, workflow-hardening]`, plus a nested `metadata` dict that duplicates `author`, `homepage`, `license`, `keywords`, `category`. All three plus nested `metadata` present — redundant, but present.
- **`$schema`**: absent on marketplace.json and plugin.json. `server.json` (MCP Registry manifest, separate file) does pin `"$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"`.
- **Reserved-name collision**: no. Plugin name is `thumbgate`; marketplace name is `thumbgate-marketplace`.
- **Pitfalls observed**: marketplace-entry `metadata` sub-object duplicates the sibling `author`/`homepage`/`license`/`keywords`/`category` fields — two sources of truth for the same facts on the same entry. `keywords` and `tags` at the entry level are identical arrays, doing the same job twice. `owner.email` is a personal Gmail in cleartext, not a group/role alias.

## 2. Plugin source binding

- **Source format(s) observed**: `npm` only. Entry: `"source": { "source": "npm", "package": "thumbgate" }`. This is the outlier pattern — no `"source": "github"` / `relative` variants elsewhere in the repo.
- **`strict` field**: absent (implicit default). The plugin ships purely via the npm tarball contents; no marketplace-level skills carve-out.
- **`skills` override on marketplace entry**: absent. (The published package declares `"skills": "./skills/"` in `plugin.json`, so skills come from the npm tarball rather than the marketplace entry.)
- **Version authority**: both `plugin.json` (`1.14.1`) and marketplace entry (`1.14.1`) carry the version, and `package.json`, `server.json`, and all adapter manifests also carry it. `scripts/sync-version.js` treats `package.json` as the single source of truth and rewrites the other files; `node scripts/sync-version.js --check` runs in CI, pre-commit, and the publish workflows to reject drift.
- **Pitfalls observed**: Source format `npm` means `claude plugin install` resolves against the public npm registry — users can't get a fork/PR without publishing. Also, because the Claude plugin is literally an alias of the npm package, any npm unpublish / version yank breaks plugin installs; there is no local fallback in the manifest.

## 3. Channel distribution

- **Channel mechanism**: no split. One marketplace, one plugin entry, one version. Users pin by cloning a commit or by npm's dist-tag (`--tag latest` via the publish step).
- **Channel-pinning artifacts**: absent at the marketplace level. Dual-asset aliasing exists at the release-artifact level (`publish-claude-plugin.yml` uploads both a versioned `.mcpb` and a channel-named `.mcpb` via `cp`, and the same for the review zip) — this gives consumers a "latest" URL and a pinned URL for the GitHub Release download, but it is orthogonal to the marketplace manifest, not a channel-branch split.
- **Pitfalls observed**: Because there's no `stable`/`latest` marketplace split, the `latest.mcpb` URL in the root README silently rolls forward across majors; consumers downloading that file have no pin unless they reach for the versioned filename.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: `v*` tags on commits that the `publish-npm.yml` workflow creates after a successful `npm publish`. The workflow calls `git tag "v${VERSION}"` and `git push origin "v${VERSION}"` from inside the action, so tags land on whatever commit on `main` triggered the publish. No release branches.
- **Release branching**: none (tag-on-main).
- **Pre-release suffixes**: none observed among the ~20 visible tags (v1.2.0 … v1.14.1 are all clean semver). `scripts/distribution-surfaces.js` exposes an `isPrereleaseVersion()` helper consumed by `publish-claude-plugin.yml` to pass `--prerelease` to `gh release create`, so the machinery supports them — just none in the current tag list.
- **Dev-counter scheme**: absent. Every commit to main is a candidate for a real semver bump; the workflow only actually publishes when `package.json` changed and the version isn't already on npm.
- **Pre-commit version bump**: no. The `.githooks/pre-commit` hook runs `scripts/sync-version.js --check` (a drift *detector* — it fails the commit if `package.json` disagrees with the adapter/manifest files), but never bumps. Bumps come from `@changesets/cli` (`changeset version`) invoked manually or by a changeset PR. `scripts/prepare` runs `bash bin/install-hooks.sh` on `npm install` to wire the hooks directory.
- **Pitfalls observed**: Silent-no-op detector in `publish-npm.yml` is purpose-built for this repo's history — the `"1.5.2 already on npm, content changes don't ship"` comment names the exact regression. That guard is a response to a real incident, not a generic precaution. Gap between `v1.5.4` and `v1.5.8` in the tag list suggests deleted/failed releases in the 1.5.x window.

## 5. Plugin-component registration

- **Reference style in plugin.json**: mixed — `"skills": "./skills/"` (string path), and `"mcpServers": { "thumbgate": { "command": "npx", "args": [...] } }` as an inline object. No `commands` / `agents` / `hooks` fields at the plugin manifest level.
- **Components observed**: skills = yes (4 dirs under `skills/`: `thumbgate`, `thumbgate-feedback`, `agent-memory`, `solve-architecture-autonomy`; each holds a `SKILL.md`, two also have a `tool.js`/`INSTALL.md`); commands = no; agents = no (no `agents/` referenced from plugin.json; `.github/agents/` exists but is outside the plugin tree); hooks = no (no `hooks.json` in `.claude-plugin/`); .mcp.json = no at the plugin root (inline `mcpServers` in plugin.json serves that role); .lsp.json = no; monitors = no; bin = yes (at repo root, but declared via `package.json` `"bin": { "thumbgate": "bin/cli.js" }`, not via plugin.json — it ships to users through npm, not through plugin loading); output-styles = no.
- **Agent frontmatter fields used**: not applicable (no agents).
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**: There are two copies of the `thumbgate-feedback` skill — one under `skills/thumbgate-feedback/SKILL.md` (the package-level copy) and one under `plugins/claude-skill/SKILL.md` (a different-body alternate that uses `name: thumbgate-feedback` and invokes `node .claude/scripts/feedback/capture-feedback.js` paths that don't exist in the npm tarball). The plugin.json points at `./skills/` (the former), so the `plugins/claude-skill/` copy is drift from some earlier layout and will *not* be what Claude loads.

## 6. Dependency installation

- **Applicable**: yes.
- **Dep manifest format**: `package.json` (npm). 40+ runtime deps including `@anthropic-ai/sdk`, `@google/genai`, `@huggingface/transformers`, `@lancedb/lancedb`, `apache-arrow`, `better-sqlite3`, `playwright-core`, `stripe`. No `requirements.txt` / pyproject anywhere — pure Node.
- **Install location**: `${CLAUDE_PLUGIN_ROOT}` is unused; the runtime is the user's npm install of the `thumbgate` package. When the plugin fires, it runs `npx --yes --package thumbgate thumbgate serve` which resolves through the user's npm cache (ad-hoc runtime fetch pattern).
- **Install script location**: `bin/postinstall.js` (wired via `package.json` `"postinstall": "node bin/postinstall.js || true"`) — prints a commercial nudge banner, respects `CI`/`THUMBGATE_NO_NUDGE=1`, is *not* used for dependency install. Git-hooks install lives in `bin/install-hooks.sh`, fired via `"prepare"` script on `npm install`. There is no SessionStart-triggered install script — the plugin is a pre-built npm package.
- **Change detection**: npm itself via `package-lock.json` integrity. The CI pin uses `npm ci --onnxruntime-node-install-cuda=skip` (interesting flag: disables the CUDA download path of `onnxruntime-node`, which is pulled transitively by `@huggingface/transformers`). `scripts/sync-version.js --check` is the cross-manifest drift detector, not a dep-change detector.
- **Retry-next-session invariant**: not applicable (no hook-based installer).
- **Failure signaling**: `postinstall` is wrapped in `|| true` in `package.json` so an install-time banner crash never fails `npm install`. `prepare` wraps `bin/install-hooks.sh` with `>/dev/null 2>&1 || true` for the same reason. `scripts/hook-pre-tool-use.js` is explicit about defensive try/catch everywhere because "a bug in the hook never deadlocks the agent" (quoted from its header).
- **Runtime variant**: Node npm (and specifically `npx --yes --package thumbgate thumbgate serve` as the MCP server command).
- **Alternative approaches**: `npx` ad-hoc resolution (no install at plugin setup time — npx pulls from cache or fetches on first run). Explicit version pinning is available via `scripts/sync-version.js`'s `explicitPinnedServeArgs(version)` helper, but the default `mcpServers.args` uses the unpinned form `[--yes, --package, thumbgate, thumbgate, serve]`.
- **Version-mismatch handling**: Node `>=18.18.0` declared via `package.json` `engines`. No ABI-specific pinning beyond that; `better-sqlite3` is a native module so Node version is load-bearing.
- **Pitfalls observed**: Unpinned `npx` args mean every MCP launch silently upgrades to whatever npm's `latest` tag resolves to — users get automatic version drift with no rollback knob. The `onnxruntime-node-install-cuda=skip` flag is passed everywhere `npm ci` runs; if a user installs without it, they pull a multi-hundred-MB CUDA binary they will never use.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes (this is the primary distribution surface).
- **`bin/` files**: `bin/cli.js` (79 KB — the ThumbGate CLI with `init`, `serve`, `gate-check`, `capture`, `import-doc`, `export-dpo`, `stats`, `cfo`, `pro`, plus session/hook subcommands); `bin/postinstall.js` (npm postinstall banner, 2 KB); `bin/install-hooks.sh` (activates `.githooks/` via `git config core.hooksPath`); `bin/memory.sh` (2 KB, memory-dir helper); `bin/obsidian-sync.sh` (Obsidian export helper).
- **Shebang convention**: `#!/usr/bin/env node` on the `.js` CLIs; `#!/bin/bash` on the pre-commit hook; bare `bash …` on the `.sh` helpers (inspected `install-hooks.sh`-adjacent code only for postinstall, `bin/memory.sh` not inspected — inferred).
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` is not used. `cli.js` uses `require(path.join(__dirname, '..', 'scripts', ...))` for internals — all lookups are relative to the resolved `bin/` location, which npm arranges via `node_modules/.bin/thumbgate → package/bin/cli.js`.
- **Venv handling (Python)**: not applicable (pure Node).
- **Platform support**: POSIX (bash hooks + env-node shebangs). No `.cmd`/`.ps1` pair for Windows; the npm-installed `thumbgate.cmd` shim is generated by npm itself, not shipped.
- **Permissions**: inferred 100755 for `bin/cli.js` (npm standard); not verified via `gh api` on this pass.
- **SessionStart relationship**: the `.claude/settings.json` in the repo (present for ThumbGate's own dev sessions, *not* shipped to plugin consumers via `.claude-plugin/`) wires `node bin/cli.js session-start` on SessionStart and `node bin/cli.js hook-auto-capture` on UserPromptSubmit — i.e., the binary is the target of the hook rather than the hook producing the binary. This is dogfood: ThumbGate uses its own CLI against itself during development.
- **Pitfalls observed**: The `package.json` `"files"` allow-list is 200+ entries long and enumerates each `scripts/*.js` individually. If a new script is added without being added to `files`, it silently won't ship — this is exactly the `public-package-parity.test.js` regression the pre-commit hook guards against ("catches the 1.5.0/1.5.1/1.5.3 regression class").

## 8. User configuration

- **`userConfig` present**: no (not in `.claude-plugin/plugin.json`).
- **Field count**: none in plugin manifest. Separately, `.env.example` lists ~40 environment variables (Stripe, Anthropic, OpenAI, Perplexity, Resend, Railway, etc.) for the ThumbGate service itself — those are service configuration, not Claude plugin user configuration.
- **`sensitive: true` usage**: not applicable (no `userConfig` schema).
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable — `mcpServers.thumbgate` uses a plain `npx ... serve` command with no `${user_config.*}` substitutions; any secrets the runtime needs are read from process env (e.g., `THUMBGATE_API_KEY` set by the user externally).
- **Pitfalls observed**: The Claude-plugin surface exposes *zero* configuration knobs — users get the default free tier. A `userConfig` for `THUMBGATE_API_KEY` (Pro tier) and for `THUMBGATE_HOOKS_ENFORCE` would be the obvious additions; their absence means Pro users have to set env vars through Claude Desktop's separate env config, outside the plugin manifest.

## 9. Tool-use enforcement

- **PreToolUse hooks**: present in the *dogfood* `.claude/settings.json` (not in `.claude-plugin/`). Matcher `Bash|Edit|Write`; command `node scripts/hook-pre-tool-use.js`. Purpose: inject matched ThumbGate lessons as `hookSpecificOutput.additionalContext`, and conditionally block via `decision: "block"` when `THUMBGATE_HOOKS_ENFORCE=1` and a lesson's `highRiskTags` overlap the command with risk score ≥ threshold. Also auto-creates `claim_gate` entries for `git commit` on non-main branches when `THUMBGATE_AUTOGATE_PR_COMMITS=1`.
- **PostToolUse hooks**: one (dogfood). Matcher `mcp__thumbgate__feedback_stats|mcp__thumbgate__dashboard`; command `node bin/cli.js cache-update`. Purpose: refresh a statusline cache after a feedback-stats read.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stderr for human messages, stdout JSON for the hook contract (`{decision?, reason?, hookSpecificOutput?}`). Header comment on `hook-pre-tool-use.js` explicitly states the stdin/stdout/exit contract.
- **Failure posture**: fail-open. Header states "every step is wrapped in try/catch. Any uncaught failure falls through to allow, so a bug in the hook never deadlocks the agent." Blocking requires *both* a match *and* the `THUMBGATE_HOOKS_ENFORCE=1` env var — default is advisory-only (injects lessons but does not block).
- **Top-level try/catch wrapping**: observed (explicitly).
- **Pitfalls observed**: None of these hooks ship with the Claude plugin — `.claude/settings.json` is in the repo for *ThumbGate developers*' own sessions. The `.claude-plugin/plugin.json` has no `hooks` field, and the npm package does not write settings.json on install. Users who install ThumbGate via the plugin marketplace get the MCP server and the skills but not the hooks that the README advertises as "PreToolUse blocks the pattern before execution"; they have to run `npx thumbgate init` separately to install hooks into their own `.claude/settings.json` (confirmed by `cli.js` header: `npx thumbgate init --wire-hooks`).

## 10. Session context loading

- **SessionStart used for context**: yes in the dogfood settings — `node bin/cli.js session-start` fires on SessionStart (no matcher filter, so on startup, clear, and compact). Loads the prior-session summary, prevention rules, and lesson stats into the new session.
- **UserPromptSubmit for context**: yes (dogfood) — `node bin/cli.js hook-auto-capture` on UserPromptSubmit watches for "thumbs up"/"thumbs down" phrases and triggers capture without waiting for the skill trigger.
- **`hookSpecificOutput.additionalContext` observed**: yes — PreToolUse emits it to inject matched lessons. Header doc strings and source are explicit.
- **SessionStart matcher**: none (fires on all sub-events). The hook entry has no `matcher` key.
- **Pitfalls observed**: Same shipping gap as purpose 9 — this context-loading machinery is dev-mode only unless the user runs `thumbgate init --wire-hooks` post-install.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none (feature not used).
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: The repo has a statusLine entry in `.claude/settings.json` (`node bin/cli.js statusline-render`) which is the per-session equivalent of a monitor — but it is also dogfood-only, not shipped via the plugin.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no (not in `plugin.json` or the marketplace entry).
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace; tag format is plain `v{version}`).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: `node --test` (Node's built-in test runner). 200+ `test:*` npm scripts each pointing to one `tests/*.test.js`. The root `npm test` script chains 70+ of them with `&&`.
- **Tests location**: `tests/` at repo root (single flat directory with ~200 `.test.js` files — no per-plugin subdivision).
- **Pytest config location**: not applicable (JS).
- **Python dep manifest for tests**: not applicable.
- **CI present**: yes, extensively.
- **CI file(s)**: 36 workflows under `.github/workflows/` — `ci.yml`, `changeset-check.yml`, `codeql.yml`, `publish-npm.yml`, `publish-claude-plugin.yml`, `publish-codex-plugin.yml`, `publish-tessl.yml`, `mcp-registry-publish.yml`, `deploy-railway.yml`, `sentry-release.yml`, `sonarcloud.yml`, `self-healing-monitor.yml`, `self-healing-auto-fix.yml`, `dependabot-automerge.yml`, `agent-automerge.yml`, `claude-code-review.yml`, `daily-revenue-loop.yml`, `gtm-autonomous-loop.yml`, `instagram-autopilot.yml`, `linkedin-*-engage.yml`, `linkedin-post-dispatch.yml`, `marketing-autopilot.yml`, `perplexity-command-center.yml`, `ralph-loop.yml`, `ralph-mode.yml`, `reply-monitor.yml`, `rotate-stripe-webhook-secret.yml`, `railway-diagnostics.yml`, `social-*.yml` (4), `video-autopilot.yml`, `weekly-social-post.yml`, `merge-branch.yml`.
- **CI triggers**: `ci.yml` on `push: [main, feat/**]`, `pull_request: [main]`, `merge_group`, `workflow_dispatch`. `publish-npm.yml` on `push: main` with paths filter on `package.json`/`package-lock.json`/`server.json`/workflow file, plus `release: [published]` and `workflow_dispatch`. `codeql.yml` adds `schedule: cron '23 6 * * 1'`. Many autonomous workflows use `schedule:` cron.
- **CI does**: very wide surface — `npm ci`, `scripts/sync-version.js --check`, changeset coverage check, `budget:status`, `ops:integrity:ci`, `branch-protection:check`, `npm test` (the 70-step chain), `npm run test:coverage`, `test:congruence`, then seven `prove:*` scripts (`prove:adapters`, `prove:automation`, `prove:runtime`, `prove:evolution`, `prove:workflow-contract`, `prove:autoresearch`, `prove:tessl`) that each emit a `proof/*/report.{json,md}` pair uploaded as a workflow artifact. On main push also: `github:about:sync` and `test:congruence:live` to verify the live GitHub About panel matches the repo content.
- **Matrix**: none in `ci.yml`. `codeql.yml` has a language matrix (`javascript-typescript` only, so effectively single-cell).
- **Action pinning**: tag pinning (`actions/checkout@v6`, `actions/setup-node@v6`, `actions/upload-artifact@v7`, `github/codeql-action/init@v4`). No SHA pinning.
- **Caching**: `actions/setup-node@v6`'s built-in `cache: 'npm'` with `cache-dependency-path`.
- **Test runner invocation**: direct `npm test` (which chains 70+ `npm run test:*` scripts, each calling `node --test tests/<name>.test.js`).
- **Pitfalls observed**: The `npm test` chain is a single long `&&`-sequence of ~70 entries — any failure aborts the rest; ordering is load-bearing and no parallelism. The seven `prove:*` scripts are a repo-specific invention (beyond the standard test framework) that emit report.json/report.md pairs — a pattern most other marketplaces don't have. The `test:congruence:live` step reaches out to live GitHub APIs during CI (requires `GH_PAT`); this is self-observability but also a real external dependency that can flake. `self-healing-auto-fix.yml` and `ralph-loop.yml` are agent-driven self-modification loops running on cron — exotic and specific to this repo's "autonomous business operations" story.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes — two workflows. `publish-npm.yml` (npm + GitHub Release creator, ~250 lines) and `publish-claude-plugin.yml` (`.mcpb` bundle builder + GitHub Release asset uploader). `mcp-registry-publish.yml` handles publication to the MCP Registry; `publish-codex-plugin.yml` and `publish-tessl.yml` cover the other adapter surfaces.
- **Release trigger**: multi-trigger. `publish-npm.yml` fires on `push: [main]` (with paths filter on `package.json`/`package-lock.json`/`server.json`/workflow file), `release: [published]`, and `workflow_dispatch`. Same trigger shape on `publish-claude-plugin.yml` but with paths filtered to `.claude-plugin/**`, selected docs, `public/index.html`, and the two build scripts. Tag creation happens *inside* the workflow, not as the trigger.
- **Automation shape**: npm publish with `--provenance` (via `id-token: write` OIDC permission and Node 24.x per the comment "npm provenance on GitHub Actions is most reliable on current LTS"), plus `.mcpb` bundle build + attach-to-GitHub-Release. The `.mcpb` builder (`scripts/build-claude-mcpb.js`) stages `bin/`, `src/`, `scripts/`, `adapters/`, `config/`, `plugins/`, `skills/`, `openapi/`, `public/`, `.well-known/`, `.claude-plugin/`, `README.md`, `LICENSE`, `SECURITY.md`, `server.json` into a staging dir and zips it.
- **Tag-sanity gates**: `publish-npm.yml` runs `scripts/publish-decision.js` which takes `VERSION`, `CURRENT_SHA`, `CURRENT_BRANCH`, `DEFAULT_BRANCH`, `NPM_PUBLISHED`, `TAG_EXISTS`, `TAG_SHA` and outputs `skip_publish` / `create_tag` / `publish_npm` / `ensure_release` / `npm_tag` / `reason`. Plus an inline "silent no-op guard" step that errors out when the version is already on npm but main has commits touching `package.json` / `src/**` / `scripts/*.js` / `README.md` / etc. since the last `v*` tag (the "`1.5.2` already on npm, content changes don't ship" regression class). `scripts/sync-version.js --check` is a separate tag-format-adjacent check that refuses inconsistent version strings across manifests.
- **Release creation mechanism**: `gh release create` / `gh release edit` / `gh release upload` via the authenticated `GH_TOKEN`. Not `softprops/action-gh-release`, not `release-please`, not `semantic-release`.
- **Draft releases**: no — releases are created directly (not drafts). Prerelease flag is set from `isPrereleaseVersion()` in `scripts/distribution-surfaces.js`.
- **CHANGELOG parsing**: yes — `scripts/release-notes.js` is invoked per release with `--version`, `--current-ref`, `--github-run-url`, `--npm-shasum`, `--npm-tarball-url`, `--npm-published-at`, and writes a Markdown file uploaded as an artifact and piped into `$GITHUB_STEP_SUMMARY`. Changesets drive the underlying CHANGELOG via `@changesets/changelog-github` (configured in `.changeset/config.json`).
- **Pitfalls observed**: This is the richest release automation in the sample. Several features are defensive responses to *past incidents* (the `1.5.2` silent-no-op guard, the `public-package-parity.test.js` pre-commit check for the `1.5.0/1.5.1/1.5.3` regression class). The publish workflow also verifies the *published* runtime via `prove-packaged-runtime.js --package-spec "thumbgate@${VERSION}" --install-attempts 12 --install-delay-ms 10000` — i.e., after publishing, pulls the tarball back from npm and smoke-tests it, with retry to ride out npm CDN propagation. That's closed-loop release verification, not just publish-and-hope.

## 15. Marketplace validation

- **Validation workflow present**: not as a standalone workflow labeled "marketplace validate." The `scripts/sync-version.js --check` step is invoked from `ci.yml`, `publish-npm.yml`, `publish-claude-plugin.yml`, and `.githooks/pre-commit`, and it validates cross-manifest consistency (including `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` version fields). The `tests/claude-mcpb.test.js` and `tests/claude-skill.test.js` cases validate the `.mcpb` bundle and skill artifacts during the main test run. No `claude plugin validate` CLI invocation observed.
- **Validator**: bespoke Node scripts (`sync-version.js --check`, `build-claude-mcpb.js` internal manifest construction, test cases). No bun+zod, no Python+json, no official CLI.
- **Trigger**: `push`, `pull_request`, `merge_group`, pre-commit (via `.githooks/pre-commit`).
- **Frontmatter validation**: yes — `tests/claude-skill.test.js` exists (not read in detail, but the name and `scripts.test:thumbgate-skill` entry imply skill-frontmatter coverage).
- **Hooks.json validation**: no dedicated step (the plugin has no `hooks.json` to validate).
- **Pitfalls observed**: Validation is spread across ~7 scripts and a dozen tests rather than one consolidated `validate-marketplace` job. Functional, but discovery-hostile — a newcomer has to trace `ci.yml` backwards to learn what "validated" means here.

## 16. Documentation

- **`README.md` at repo root**: present, ~22 KB. Marketing-forward with emoji-heavy framing, feature matrix, pricing tiers, installation recipes for Claude Desktop / Cursor / Codex / Gemini / Amp / OpenCode.
- **`README.md` per plugin**: present at `.claude-plugin/README.md` (~6 KB, Claude-Desktop-scoped variant of the root README).
- **`CHANGELOG.md`**: present, ~117 KB — very large. Format appears to be a Keep-a-Changelog variant generated by `@changesets/changelog-github`.
- **`architecture.md`**: absent (not at repo root; not a standard file in this repo).
- **`CLAUDE.md`**: present at repo root (~10 KB — agent-operating instructions). Also `AGENTS.md` (~7 KB) and `GEMINI.md` (~6 KB) as peer agent-onboarding docs, plus `SKILL.md` at repo root (~3.7 KB). None of these live in the plugin subtree.
- **Community health files**: `.github/FUNDING.yml`, `.github/dependabot.yml`, `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/`, `.github/CODEOWNERS`, `.github/github-app-manifest.json`. No `SECURITY.md` at root (but it's referenced as shipped-in-tarball by `build-claude-mcpb.js`'s copy list — file exists somewhere but not listed at root by `gh api`; may live under `docs/`). No `CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` observed at root.
- **LICENSE**: present (MIT, SPDX-MIT).
- **Badges / status indicators**: not verified (README not fully inspected for badge block).
- **Pitfalls observed**: Documentation sprawl is a defining feature — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `SKILL.md`, `LAUNCH.md`, `LAUNCH_NOW.md`, `LAUNCH_POSTS.md`, `DISTRIBUTION_RUNBOOK.md`, `FIRST_CUSTOMER_BATTLE_PLAN.md`, `RAILWAY_BILLING_SETUP.md`, `WORKFLOW.md`, `gate-program.md`, `primer.md` all at repo root. Much of this is go-to-market content, not developer docs. A new contributor can't tell from a `ls` which doc to read first.

## 17. Novel axes

- **Publish-trigger paths-filter on `package.json`**: `publish-npm.yml` uses `on: push: branches: [main]: paths: ['package.json', 'package-lock.json', 'server.json', '.github/workflows/publish-npm.yml']` — most other sampled marketplaces trigger on `v*` tag pushes. Tag creation is moved *inside* the workflow and conditioned on `publish-decision.js`'s output; `git push origin "v${VERSION}"` runs from inside the job after a successful publish. Main-is-the-trigger + workflow-creates-its-own-tag is a distinctive model.
- **Silent-no-op regression detector**: `publish-npm.yml`'s guard step that fails CI when `npm view thumbgate@X` already returns the version *and* `git diff --name-only vX..HEAD` on the shipped-files allow-list is non-empty. Directly encodes the `1.5.2` regression ("version already published, but content changed — you forgot to bump"). A pattern worth extracting if pattern-doc wants to cover "protecting against a published-but-stale version."
- **Post-publish runtime smoke**: `prove-packaged-runtime.js --package-spec "thumbgate@${VERSION}" --install-attempts 12 --install-delay-ms 10000` pulls the freshly-published tarball *from the npm registry* (with retries to ride out CDN propagation) and smoke-tests it. Closed-loop: "publish verified only when the thing downstream users would pull actually works." Novel relative to the rest of the sample.
- **Proof pipeline as a test tier**: Seven `prove:*` scripts distinct from the `test:*` scripts, each emitting `proof/<area>/report.{json,md}` uploaded as a CI artifact. Structured, machine-readable post-CI artifact output. Not a known pattern elsewhere in the sample.
- **Version-sync-as-validation** (`scripts/sync-version.js --check`): single-source-of-truth mechanism rewriting `~15` manifests/HTML pages from `package.json`'s version. `--check` mode is the *validator* (fails on drift) and runs in pre-commit, CI, both publish workflows, and changeset workflow. Generalization candidate for "single source of truth for version, enforced across all manifests."
- **Dual-asset filename aliasing on GitHub Release**: `publish-claude-plugin.yml` uploads both `thumbgate-claude-desktop.mcpb` (channel-latest filename) and `thumbgate-claude-desktop-v1.14.1.mcpb` (versioned filename) via `cp`. Users can link to either. An alternative to branch-based channel distribution.
- **Autonomous-operations workflow surface**: 20+ workflows (`daily-revenue-loop.yml`, `instagram-autopilot.yml`, `gtm-autonomous-loop.yml`, `perplexity-command-center.yml`, `marketing-autopilot.yml`, `ralph-loop.yml`, `self-healing-auto-fix.yml`, etc.) run on cron and drive non-code activity (social posting, revenue polling, self-healing, engagement). Orthogonal to plugin distribution but a hallmark of this repo's "the repo runs the business" stance.
- **Multi-adapter single-package shape**: `adapters/{amp,chatgpt,claude,codex,forge,gemini,mcp,opencode}/` all ship inside the same npm tarball, each with its own integration descriptor (`config.toml`, `opencode.json`, `function-declarations.json`, `openapi.yaml`). `plugins/{amp-skill,claude-codex-bridge,claude-skill,codex-profile,cursor-marketplace,gemini-extension,opencode-profile}/` mirror that at the plugin-format level. One package, multiple ecosystems — a "universal adapter" distribution pattern.
- **Changeset governance in CI**: `changeset-check.yml` + `scripts/changeset:check` fail PRs that touch release-relevant paths without a changeset entry, outside the standard Changesets bot. Enforces manual release-note discipline per-PR.
- **MCP Registry `server.json`**: separate manifest (`server.json` with `$schema` pin to `static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`) drives `mcp-registry-publish.yml`. This is a third registry surface (npm, GitHub Release .mcpb, MCP Registry) that the other sampled marketplaces generally don't touch.
- **`npx --yes --package thumbgate thumbgate serve` unpinned launch**: default `mcpServers.args` is unpinned; a pinned variant exists in code but isn't surfaced to users. Trade-off pattern worth calling out — users get auto-upgrade at launch time vs. predictable versioning.

## 18. Gaps

- `.claude-plugin/bundle/icon.{png,svg}` is present but their referencing manifest key was not located — the `plugin.json` doesn't declare an `icon` path. Unclear whether the `.mcpb` runtime consumes them via a convention (e.g., `bundle/` relative to plugin root) or whether they are dead files. Would need to fetch `scripts/build-claude-mcpb.js` in full to confirm icon wiring in the generated `.mcpb` manifest.
- The four skill directories (`thumbgate`, `thumbgate-feedback`, `agent-memory`, `solve-architecture-autonomy`) were not all read in full — only `thumbgate/SKILL.md` and `thumbgate-feedback/SKILL.md` inspected. Whether the other two are fully-formed or stubs is not confirmed.
- The `publish-codex-plugin.yml`, `publish-tessl.yml`, `mcp-registry-publish.yml` workflows were listed but not read — their shape (adapter-specific publish flows) is inferred from the corresponding `test:*`/`prove:*` scripts rather than the YAML.
- `package.json` was fetched but its full `"files"` allow-list, `dependencies` list (40+ entries), and the body of most `scripts` were only sampled. Exact dep pins and the complete test-chain structure are not exhaustively catalogued.
- The `.claude/settings.json` analysis assumes this file is *dogfood* (for ThumbGate's own dev sessions) rather than shipped to plugin consumers. Confirmed by checking `package.json` `"files"`: `.claude/` is not listed, only `.claude-plugin/`. However, the `build-claude-mcpb.js` stage-copy list *also* omits `.claude/`, confirming it does not ship in the `.mcpb` either. This is an observed fact, not inferred — but the broader claim that users have to run `thumbgate init --wire-hooks` to get hooks is inferred from the CLI's usage header.
- Pre-release tag handling (`isPrereleaseVersion()`) is present in code but has no example — whether any actual prerelease has been published through this path is unconfirmed (no `v*-rc` / `v*-beta` in the tag list, but only the last 20 tags were inspected).
- `.changeset/` contents (other than `config.json`) not enumerated; individual changeset markdown files that might exist between releases were not inspected.
- `SECURITY.md` is referenced in `build-claude-mcpb.js`'s copy list but not in the root `gh api` listing — it exists somewhere in the tree (or the copy-list has a dead reference); location unconfirmed.
- The full `tests/` directory was truncated at 40 entries; ~200 total test files exist by `package.json` `test:*` scripts count, but the directory listing was not paginated.
