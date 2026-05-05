# Sample

Mirrors of `https://github.com/IgorGanapolsky/ThumbGate`. A self-improving agent governance plugin: thumbs-up/down feedback distills lessons that drive PreToolUse Pre-Action Gates blocking repeat AI mistakes. Distributed as an npm package (`thumbgate`); the `.claude-plugin/` manifest wraps the published npm package as a Claude plugin. Default branch `main`, MIT licensed, version `1.14.1` at sample capture, last commit `2026-04-21`, 16 stars.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root, co-located with `plugin.json`, a plugin-level `README.md`, and an mcpb `bundle/` subdirectory (`icon.png`, `icon.svg`, `server/index.js`). Top-level fields: `name`, `version`, `owner` (`name`, `email`), `plugins[]`. No `metadata` wrapper. No top-level `description`. `metadata.pluginRoot` absent (source binding is `npm`, so no local root applies). Plugin name is `thumbgate`; marketplace name is `thumbgate-marketplace`.

### Redundant metadata sub-object on plugin entries

Plugin entry has a nested `metadata` dict that duplicates sibling `author`, `homepage`, `license`, `keywords`, `category` fields. `keywords` and `tags` arrays at the entry level are identical, doing the same job twice. `owner.email` is a personal Gmail in cleartext, not a group/role alias.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

Single plugin entry (`thumbgate`) with `category: "developer-tools"`, `tags: [pre-action-gates, ai-agent-safety, mcp, memory, workflow-hardening]`, and `keywords: [claude-desktop, desktop-extension, pre-action-gates, ai-agent-safety, mcp, memory, workflow-hardening]`. Category, keywords, and tags all present plus a nested `metadata` dict.

### `$schema` absence on per-plugin manifests

`$schema` absent on both `marketplace.json` and `plugin.json`. The separate `server.json` (MCP Registry manifest) does pin `"$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"`.

## Plugin source binding

### `source: npm`

Marketplace entry is `{ "source": "npm", "package": "thumbgate" }`. `claude plugin install` resolves against the public npm registry. Users can't install a fork or PR without publishing under a different name; npm unpublish or version yank breaks plugin installs with no local fallback in the manifest.

### `strict` field default

`strict` absent (implicit default). The plugin ships purely via the npm tarball contents; no marketplace-level skills carve-out. The published package declares `"skills": "./skills/"` in `plugin.json`, so skills come from the npm tarball rather than the marketplace entry.

## Version coordination

### Multi-site sprawl (5+ locations)

`plugin.json` (`1.14.1`), marketplace entry (`1.14.1`), `package.json`, `server.json`, and all adapter manifests carry the same version. `scripts/sync-version.js` treats `package.json` as the single source of truth and rewrites the other ~15 files. `node scripts/sync-version.js --check` runs in CI, pre-commit, and the publish workflows to reject drift.

## Channel distribution

### Dual-asset filename aliasing on GitHub Release

`publish-claude-plugin.yml` uploads both a versioned `.mcpb` (`thumbgate-claude-desktop-v1.14.1.mcpb`) and a channel-named `.mcpb` (`thumbgate-claude-desktop.mcpb`) via `cp`, plus the same dual aliasing for the review zip. The `latest.mcpb` URL silently rolls forward across majors; the versioned filename is stable. Marketplace level has no `stable`/`latest` split — the dual-asset aliasing operates at the GitHub Release artifact level, orthogonal to the marketplace manifest.

### Pre-release tag suffixes on a single channel

No prereleases observed in the published tag list, but `scripts/distribution-surfaces.js` exposes `isPrereleaseVersion()`, consumed by `publish-claude-plugin.yml` to pass `--prerelease` to `gh release create` when applicable. Machinery supports them.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Default branch `main`. `v*` tags created by `publish-npm.yml` after a successful `npm publish` — the workflow runs `git tag "v${VERSION}"` and `git push origin "v${VERSION}"` from inside the action. Tags land on whatever commit on `main` triggered the publish. ~20 visible tags from `v1.2.0` to `v1.14.1` are clean semver. No release branches.

### Mixed annotated and lightweight tags

A gap between `v1.5.4` and `v1.5.8` in the tag list suggests deleted/failed releases in the 1.5.x window.

## Plugin-component registration

### Inline `mcpServers` definition in `plugin.json`

`plugin.json` declares `"skills": "./skills/"` (string path) and `"mcpServers": { "thumbgate": { "command": "npx", "args": ["--yes", "--package", "thumbgate", "thumbgate", "serve"] } }` as an inline object. No `commands`, `agents`, or `hooks` fields at the plugin manifest level. No `.mcp.json` at the plugin root — inline `mcpServers` in plugin.json serves that role.

## Component composition

### Skills (universal)

4 directories under `skills/`: `thumbgate`, `thumbgate-feedback`, `agent-memory`, `solve-architecture-autonomy`. Each holds a `SKILL.md`; two also carry `tool.js` / `INSTALL.md`. Plugin.json points at `./skills/`. A drift copy exists under `plugins/claude-skill/SKILL.md` (different body, invokes `node .claude/scripts/feedback/capture-feedback.js` paths that don't exist in the npm tarball) — left over from an earlier layout and not what Claude loads.

### bin

`package.json` declares `"bin": { "thumbgate": "bin/cli.js" }` at repo root. Bin reaches users through npm distribution, not via plugin loading.

## Server runtime (MCP)

### Runtime-fetched server via `npx -y`

MCP server launches via `npx --yes --package thumbgate thumbgate serve` from the plugin.json `mcpServers.args`. Resolves through the user's npm cache; first launch fetches the package from the registry. The unpinned form silently rolls forward with whatever `latest` resolves to.

## Bin entry mechanism

### Plugin-bin + npm-bin dual-target

`package.json` declares `"bin": {"thumbgate": "bin/cli.js"}` so `npm install -g thumbgate` or `npx thumbgate` exposes the same CLI the plugin install does. The plugin manifest is a thin alias of the npm package; the bin reaches users through the npm package, not through `/plugin install`'s payload. `engines.node >= 18.18.0` declared in `package.json` even though Node-only consumption is the npm path. `bin/cli.js` (~79 KB) carries `#!/usr/bin/env node` and provides `init`, `serve`, `gate-check`, `capture`, `import-doc`, `export-dpo`, `stats`, `cfo`, `pro`, plus session/hook subcommands. Other `bin/` files: `bin/postinstall.js` (npm postinstall banner, ~2 KB), `bin/install-hooks.sh` (activates `.githooks/` via `git config core.hooksPath`), `bin/memory.sh` (~2 KB memory-dir helper), `bin/obsidian-sync.sh`. Shebang on `.js` files is `#!/usr/bin/env node`; on `.sh` helpers is `#!/bin/bash` (or invoked via `bash …`). Runtime resolution uses `require(path.join(__dirname, '..', 'scripts', ...))` for internals — script-relative; `${CLAUDE_PLUGIN_ROOT}` is not used. `bin/cli.js` is `100755` per npm standard. POSIX-only platform support; Windows users rely on the npm-generated `thumbgate.cmd` shim, not a shipped one.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

CLI internals resolve via `__dirname`-relative paths (`require(path.join(__dirname, '..', 'scripts', ...))`). Does not consult `${CLAUDE_PLUGIN_ROOT}`.

## Dependency installation

### Ad-hoc per-invocation fetch via `npx --yes --package`

Default `mcpServers.args` is `["--yes", "--package", "thumbgate", "thumbgate", "serve"]` — unpinned. Every MCP launch silently upgrades to whatever npm's `latest` tag resolves to; users get automatic version drift with no rollback knob. Explicit version pinning is available via `scripts/sync-version.js`'s `explicitPinnedServeArgs(version)` helper, but the default uses the unpinned form. `package.json` carries 40+ runtime deps including `@anthropic-ai/sdk`, `@google/genai`, `@huggingface/transformers`, `@lancedb/lancedb`, `apache-arrow`, `better-sqlite3`, `playwright-core`, `stripe`. No `requirements.txt` / pyproject — pure Node. CI pin uses `npm ci --onnxruntime-node-install-cuda=skip` to disable the CUDA download path of `onnxruntime-node` (transitively pulled via `@huggingface/transformers`) — users installing without that flag pull a multi-hundred-MB CUDA binary they will never use. Node `>=18.18.0` declared via `package.json` `engines`. `better-sqlite3` is a native module so Node version is load-bearing. `bin/postinstall.js` (wired via `package.json` `"postinstall": "node bin/postinstall.js || true"`) prints a commercial nudge banner, respects `CI` and `THUMBGATE_NO_NUDGE=1`, is not used for dependency install. Git-hooks install lives in `bin/install-hooks.sh`, fired via `"prepare"` script on `npm install` and wrapped `>/dev/null 2>&1 || true`.

### Postinstall failure suppression

`postinstall` in `package.json` is `"node bin/postinstall.js || true"` so an install-time banner crash never fails `npm install`. `prepare` wraps `bin/install-hooks.sh` with `>/dev/null 2>&1 || true` for the same reason.

## User configuration and authentication

### No userConfig, env-var only

`.claude-plugin/plugin.json` does not declare `userConfig`. `.env.example` lists ~40 environment variables (Stripe, Anthropic, OpenAI, Perplexity, Resend, Railway, etc.) for the ThumbGate service itself — service configuration, not Claude-plugin user configuration. `mcpServers.thumbgate` uses a plain `npx ... serve` command with no `${user_config.*}` substitution; runtime secrets read from process env (e.g., `THUMBGATE_API_KEY` set externally). The Claude-plugin surface exposes zero configuration knobs — Pro-tier users (`THUMBGATE_API_KEY`) and hook-enforcement users (`THUMBGATE_HOOKS_ENFORCE`) have to set env vars through Claude Desktop's separate env config.

## Session context loading

### SessionStart purely for non-context side effects

Dogfood `.claude/settings.json` (in the repo for ThumbGate's own dev sessions, not shipped via `.claude-plugin/`) wires `node bin/cli.js session-start` on SessionStart with no matcher (fires on startup, clear, and compact). Loads prior-session summary, prevention rules, and lesson stats into the new session. `node bin/cli.js hook-auto-capture` on `UserPromptSubmit` watches for "thumbs up"/"thumbs down" phrases and triggers capture without waiting for the skill trigger. PreToolUse emits `hookSpecificOutput.additionalContext` to inject matched lessons. None of this ships with the plugin — `.claude/` is not in `package.json` `"files"` or `build-claude-mcpb.js` stage-copy list. Users get hooks via `npx thumbgate init --wire-hooks` post-install.

## Tool-use enforcement

### PreToolUse blocking gate (env-var opt-in)

Dogfood `.claude/settings.json` registers a PreToolUse hook with matcher `Bash|Edit|Write` running `node scripts/hook-pre-tool-use.js`. Default behavior is advisory-only: injects matched ThumbGate lessons as `hookSpecificOutput.additionalContext`. Conditionally blocks via `decision: "block"` when both `THUMBGATE_HOOKS_ENFORCE=1` is set and a lesson's `highRiskTags` overlap the command with risk score ≥ threshold. Also auto-creates `claim_gate` entries for `git commit` on non-main branches when `THUMBGATE_AUTOGATE_PR_COMMITS=1`. Header on `hook-pre-tool-use.js` explicitly states the stdin/stdout/exit contract. Top-level try/catch is observed: header states "every step is wrapped in try/catch. Any uncaught failure falls through to allow, so a bug in the hook never deadlocks the agent." None of these hooks ship with the Claude plugin — users must run `npx thumbgate init --wire-hooks` to install them into their own `.claude/settings.json`.

### PostToolUse with selector matcher (targeted observation)

One dogfood PostToolUse hook with matcher `mcp__thumbgate__feedback_stats|mcp__thumbgate__dashboard` running `node bin/cli.js cache-update`. Refreshes a statusline cache after a feedback-stats read.

## Hook output contract

### Stderr for human display + stdout JSON for harness

Stderr for human messages, stdout JSON for the hook contract (`{decision?, reason?, hookSpecificOutput?}`). Header comment on `hook-pre-tool-use.js` explicitly states the contract.

## Hook failure posture

### Fail-open with always-exit-0

Header on `hook-pre-tool-use.js` states: "every step is wrapped in try/catch. Any uncaught failure falls through to allow, so a bug in the hook never deadlocks the agent." Blocking requires both a match and `THUMBGATE_HOOKS_ENFORCE=1` — default is advisory-only.

## Live monitoring

### Status line via user-settings mutation

Dogfood `.claude/settings.json` carries a `statusLine` entry running `node bin/cli.js statusline-render` — per-session status panel populated by hook output. Like the rest of the dogfood configuration it is not shipped to plugin consumers via `.claude-plugin/`.

## Plugin-to-plugin coordination

### `dependencies` field absent

Single-plugin marketplace; `dependencies` field absent from `plugin.json` or marketplace entry. Tag format is plain `v{version}`.

## Testing

### Node `node:test` chained suite

`node --test` (Node's built-in test runner) with 200+ `test:*` npm scripts each pointing to one `tests/<name>.test.js`. The root `npm test` script chains 70+ entries with `&&` — sequential, ordering-load-bearing, single failure aborts the chain. `tests/` at repo root (single flat directory). The `prove:*` tier — seven scripts (`prove:adapters`, `prove:automation`, `prove:runtime`, `prove:evolution`, `prove:workflow-contract`, `prove:autoresearch`, `prove:tessl`) — each emits `proof/<area>/report.{json,md}` artifacts uploaded as workflow artifacts. Distinct from the `test:*` tier and supports post-hoc auditing of CI runs.

### Centralized `tests/` placement

All ~200 `.test.js` files in a flat `tests/` directory at repo root. No per-plugin subdivision.

## CI workflow shape

### Sprawling autonomous workflows

36 workflows under `.github/workflows/`. Core pipeline workflows include `ci.yml`, `changeset-check.yml`, `codeql.yml`, `publish-npm.yml`, `publish-claude-plugin.yml`, `publish-codex-plugin.yml`, `publish-tessl.yml`, `mcp-registry-publish.yml`, `deploy-railway.yml`, `sentry-release.yml`, `sonarcloud.yml`, `dependabot-automerge.yml`, `agent-automerge.yml`, `claude-code-review.yml`, `merge-branch.yml`. Autonomous-operations workflows running on cron include `daily-revenue-loop.yml`, `gtm-autonomous-loop.yml`, `instagram-autopilot.yml`, `linkedin-*-engage.yml` (multiple), `linkedin-post-dispatch.yml`, `marketing-autopilot.yml`, `perplexity-command-center.yml`, `ralph-loop.yml`, `ralph-mode.yml`, `reply-monitor.yml`, `rotate-stripe-webhook-secret.yml`, `railway-diagnostics.yml`, `social-*.yml` (4), `video-autopilot.yml`, `weekly-social-post.yml`, `self-healing-monitor.yml`, `self-healing-auto-fix.yml`. `ci.yml` triggers on `push: [main, feat/**]`, `pull_request: [main]`, `merge_group`, `workflow_dispatch`. `publish-npm.yml` triggers on `push: main` with paths filter on `package.json`/`package-lock.json`/`server.json`/workflow file, plus `release: [published]` and `workflow_dispatch`. `codeql.yml` adds `schedule: cron '23 6 * * 1'`. `ci.yml` runs `npm ci`, `scripts/sync-version.js --check`, changeset coverage check, `budget:status`, `ops:integrity:ci`, `branch-protection:check`, `npm test` (the 70-step chain), `npm run test:coverage`, `test:congruence`, then the seven `prove:*` scripts. On main push also: `github:about:sync` and `test:congruence:live` to verify the live GitHub About panel matches repo content. No matrix in `ci.yml`. `codeql.yml` matrix is `javascript-typescript` only (single-cell). Action pinning by tag (`actions/checkout@v6`, `actions/setup-node@v6`, `actions/upload-artifact@v7`, `github/codeql-action/init@v4`); no SHA pinning. Caching via `actions/setup-node@v6`'s built-in `cache: 'npm'` with `cache-dependency-path`.

### Discipline-checking CI on push and PR

`changeset-check.yml` plus `scripts/changeset:check` fail PRs that touch release-relevant paths without a changeset entry. `test:congruence:live` step reaches out to live GitHub APIs during CI (requires `GH_PAT`). Self-observability dependency that can flake.

## Marketplace validation

### Cross-manifest version-sync as validation

`scripts/sync-version.js --check` invoked from `ci.yml`, `publish-npm.yml`, `publish-claude-plugin.yml`, and `.githooks/pre-commit`. Validates cross-manifest consistency including `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` version fields. Treats `package.json` as the single source of truth and rewrites the other ~15 files. `--check` mode is the validator (fails on drift). `tests/claude-mcpb.test.js` and `tests/claude-skill.test.js` validate the `.mcpb` bundle and skill artifacts during the main test run. No `claude plugin validate` CLI invocation; no consolidated `validate-marketplace` job — validation is spread across ~7 scripts and a dozen tests. Validator is bespoke Node — not bun+zod, not Python+json, not the official CLI.

## Release automation

### Multi-trigger workflow with single-snapshot path

`publish-npm.yml` (~250 lines) fires on `push: [main]` (paths filter on `package.json`/`package-lock.json`/`server.json`/workflow file), `release: [published]`, and `workflow_dispatch`. Tag creation happens inside the workflow, not as the trigger — `git push origin "v${VERSION}"` runs from inside the job after a successful publish. `scripts/publish-decision.js` takes `VERSION`, `CURRENT_SHA`, `CURRENT_BRANCH`, `DEFAULT_BRANCH`, `NPM_PUBLISHED`, `TAG_EXISTS`, `TAG_SHA` and outputs `skip_publish` / `create_tag` / `publish_npm` / `ensure_release` / `npm_tag` / `reason`. npm publish runs with `--provenance` (via `id-token: write` OIDC permission and Node 24.x — comment notes "npm provenance on GitHub Actions is most reliable on current LTS").

### Tag-triggered release with multi-gate sanity (npm)

`publish-claude-plugin.yml` triggers on the same shape as `publish-npm.yml` with paths filtered to `.claude-plugin/**`, selected docs, `public/index.html`, and the two build scripts. Builds the `.mcpb` bundle via `scripts/build-claude-mcpb.js`, which stages `bin/`, `src/`, `scripts/`, `adapters/`, `config/`, `plugins/`, `skills/`, `openapi/`, `public/`, `.well-known/`, `.claude-plugin/`, `README.md`, `LICENSE`, `SECURITY.md`, `server.json` into a staging dir and zips it. Attaches the `.mcpb` to the GitHub Release via `gh release create` / `gh release edit` / `gh release upload` with the authenticated `GH_TOKEN`. Not `softprops/action-gh-release`, not `release-please`, not `semantic-release`. Releases created directly (not drafts). Prerelease flag set from `isPrereleaseVersion()` in `scripts/distribution-surfaces.js`. Release notes generated by `scripts/release-notes.js` invoked per release with `--version`, `--current-ref`, `--github-run-url`, `--npm-shasum`, `--npm-tarball-url`, `--npm-published-at`; output written as Markdown, uploaded as an artifact, and piped into `$GITHUB_STEP_SUMMARY`. Changesets drive the underlying CHANGELOG via `@changesets/changelog-github` (configured in `.changeset/config.json`).

### Silent-no-op regression detector

`publish-npm.yml` carries an inline guard step that errors out when the version is already on npm but `git diff --name-only vX..HEAD` on the shipped-files allow-list (`package.json` / `src/**` / `scripts/*.js` / `README.md` / etc.) is non-empty since the last `v*` tag. Encodes the `1.5.2` regression class ("version already published, but content changed — you forgot to bump"). Defensive response to a past incident.

### Post-publish runtime smoke

`prove-packaged-runtime.js --package-spec "thumbgate@${VERSION}" --install-attempts 12 --install-delay-ms 10000` pulls the freshly-published tarball back from npm with retries to ride out CDN propagation, then smoke-tests it. Closed-loop release verification: "publish verified only when the thing downstream users would pull actually works."

### Multi-target release pipeline (npm + cross-repo marketplace dispatch)

`mcp-registry-publish.yml` publishes to the MCP Registry, `publish-codex-plugin.yml` publishes the Codex adapter, `publish-tessl.yml` publishes the Tessl adapter. Each adapter surface gets its own publish workflow alongside `publish-npm.yml` and `publish-claude-plugin.yml`, distributing to npm + GitHub Release `.mcpb` + MCP Registry + per-adapter targets in parallel.

## Documentation surface

### Sprawling root with many entry-point markdowns

`README.md` at repo root (~22 KB, marketing-forward with emoji-heavy framing, feature matrix, pricing tiers, installation recipes for Claude Desktop / Cursor / Codex / Gemini / Amp / OpenCode). `.claude-plugin/README.md` (~6 KB, Claude-Desktop-scoped variant). `CHANGELOG.md` very large (~117 KB, Keep-a-Changelog variant generated by `@changesets/changelog-github`). `CLAUDE.md` at repo root (~10 KB, agent-operating instructions). `AGENTS.md` (~7 KB), `GEMINI.md` (~6 KB), and a `SKILL.md` at repo root (~3.7 KB) as peer agent-onboarding docs. Other root-level markdowns: `LAUNCH.md`, `LAUNCH_NOW.md`, `LAUNCH_POSTS.md`, `DISTRIBUTION_RUNBOOK.md`, `FIRST_CUSTOMER_BATTLE_PLAN.md`, `RAILWAY_BILLING_SETUP.md`, `WORKFLOW.md`, `gate-program.md`, `primer.md`. Much of this is go-to-market content rather than developer docs — a new contributor cannot tell from a `ls` which doc to read first. No `architecture.md`. `SECURITY.md` is referenced in `build-claude-mcpb.js`'s copy list but not at root in the API listing — file exists somewhere else in the tree.

## Community health files

### Open contribution with health files

`.github/FUNDING.yml`, `.github/dependabot.yml`, `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/`, `.github/CODEOWNERS`, `.github/github-app-manifest.json`. No `SECURITY.md` at root listing (referenced by `build-claude-mcpb.js`). No `CONTRIBUTING.md` or `CODE_OF_CONDUCT.md` at root.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

LICENSE at repo root (MIT, SPDX-MIT) plus matching SPDX strings in manifests.

## Cross-ecosystem distribution

### Multi-adapter single-package shape

`adapters/{amp,chatgpt,claude,codex,forge,gemini,mcp,opencode}/` all ship inside the same npm tarball, each with its own integration descriptor (`config.toml`, `opencode.json`, `function-declarations.json`, `openapi.yaml`). `plugins/{amp-skill,claude-codex-bridge,claude-skill,codex-profile,cursor-marketplace,gemini-extension,opencode-profile}/` mirror that at the plugin-format level. One package, multiple ecosystems — universal-adapter distribution.

### MCP Registry presence (`server.json`)

Separate `server.json` manifest with `$schema` pinned to `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`. `mcp-registry-publish.yml` drives publication to the MCP Registry. Three registry surfaces total: npm, GitHub Release `.mcpb`, MCP Registry.

## Distribution exclusion and dogfood layout

### Repo-local hooks in `.claude/settings.json`

`.claude/settings.json` in the repo wires SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, and statusLine hooks for ThumbGate's own dev sessions. The plugin uses its own CLI against itself during development (dogfood). Confirmed not shipped to plugin consumers: `package.json` `"files"` allow-list does not include `.claude/`, only `.claude-plugin/`; `build-claude-mcpb.js`'s stage-copy list also omits `.claude/`. Users get hooks only by running `npx thumbgate init --wire-hooks` post-install.

## Sandbox and security posture

### Default tools, no permission escalation

No special sandbox declaration; permission posture relies on Node + npm defaults. The `.env.example` lists ~40 secret env vars that must be set externally; the plugin manifest exposes zero `userConfig` knobs.
