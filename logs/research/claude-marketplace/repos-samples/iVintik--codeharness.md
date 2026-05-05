# Sample

Mirrors of `https://github.com/iVintik/codeharness`. Single-plugin git repo at `v0.47.0` shipping a bilingual npm CLI + Claude Code plugin that "makes autonomous coding agents produce software that actually works" through real-world verification, observability, and mechanical enforcement via Claude Code hooks.

## Marketplace manifest layout

### No marketplace manifest (plugin source repo only)

No `.claude-plugin/marketplace.json` at the repo root. The plugin is installed directly via `claude plugin install github:iVintik/codeharness`. A separate `iVintik/private-claude-marketplace` aggregator (referenced by `.github/workflows/release.yml`) handles marketplace registration via `repository_dispatch` events with `{plugin, version}` payload — its contents are private and not directly observable from this repo.

## Plugin source binding

### Direct git install (no marketplace.json in source repo)

Installation is direct: `claude plugin install github:iVintik/codeharness`. The release workflow dispatches a `plugin-release` event to `iVintik/private-claude-marketplace`; the source binding format used by that aggregator is not visible from this repo.

## Per-plugin discoverability metadata

### Bare-minimum (name, version, description only)

`.claude-plugin/plugin.json` is 236 bytes, three fields: `name`, `version`, `description`. No `category`, `tags`, `keywords`, `author`, or `homepage`. The repo also has no GitHub description (`gh api repos/iVintik/codeharness` returns `description: null`), so even the README-opening sentence is not mirrored as repo metadata. Aggregator-supplied metadata in the private marketplace would be the only discoverability surface.

### `$schema` absence on per-plugin manifests

`$schema` is absent on `plugin.json`. No marketplace manifest exists in this repo to bear a `$schema` either.

## Channel distribution

### npm registry as de facto channel substrate

Two distribution surfaces coexist: npm-registry (CLI binary) and git-repo (plugin contents). Users installing the plugin via `claude plugin install github:iVintik/codeharness` track `master` HEAD without a `@ref` pin (no channel guidance in README). The plugin's SessionStart hook then auto-pins the `codeharness` npm CLI to the plugin's `plugin.json` version — plugin ref and CLI version are coupled through the hook, not through a marketplace manifest. npm is the version-coordination substrate the plugin reaches for, even though the install entry point is git.

### SessionStart self-update

The SessionStart hook `hooks/ensure-cli-version.sh` runs `npm install -g codeharness@${REQUIRED_VERSION}` pinned to the plugin's own `plugin.json` version on every session start. This is a self-update path — when a user updates the plugin (new git ref), the next session pulls the matching npm version. Opt-out via `CODEHARNESS_NO_AUTO_INSTALL=1`.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Tags `v0.47.0`, `v0.46.0`, `v0.45.1`, `v0.45.0`, `v0.44.2` all sit on `master`. Cadence is high — `v0.44.2 → v0.47.0` within days of the snapshot. Pre-1.0 per CLAUDE.md ("Major (X.0.0): breaking changes (not yet — still pre-1.0)"). All tags are plain `vX.Y.Z` (no pre-release suffixes). No release branching.

### Tag-on-main with manual GitHub Release

The release workflow is triggered by a GitHub Release `published` event, not by tag push. CLAUDE.md spells out: "After `/plugin-ops:release` pushes the tag, create a GitHub Release from that tag to trigger the pipeline: `gh release create v{version} --generate-notes`." Tagging alone does not ship; the manual `gh release create` step is load-bearing.

## Version coordination

### Dual-file version (manifest pair)

Both `package.json` and `.claude-plugin/plugin.json` carry the version (`0.47.0` in each). Neither derives from the other; both are authoritative in their own ecosystem. CI enforces equality as a hard gate via a `Verify version sync` step in both `ci.yml` and `release.yml`. CLAUDE.md warns: "After `/plugin-ops:release` bumps `plugin.json`, you MUST also update `package.json` version to match BEFORE creating the GitHub Release." Two sources, one CI gate; not a single-source-of-truth sed-derivation.

## Plugin-component registration

### Default convention discovery

`plugin.json` declares no component fields (just `name`, `version`, `description`). Claude Code auto-discovers the standard `commands/`, `agents/`, `skills/`, `hooks/` directories.

## Plugin-component placement

### Inside plugin directory

Single-tree layout — the plugin is the repo. All component dirs are at repo root.

## Component composition

### Skills (universal)

Two skills: `skills/bmad-integration/`, `skills/visibility-enforcement/`.

### Commands

Five `.md` command files — `commands/harness-init.md`, `harness-docs.md`, `harness-onboard.md`, `harness-status.md`, `harness-teardown.md` — alongside an unusual `commands/AGENTS.txt`.

### Agents

Two: `agents/doc-gardener.md`, `agents/verifier.md`.

### Hooks

`hooks/hooks.json` plus `hooks/ensure-cli-version.sh`.

### bin

`bin/codeharness` — bash wrapper.

## Agent declaration conventions

### Plain tool-name list

`verifier.md` declares `tools: [Bash, Read, Write, Glob, Grep, Agent]` as a YAML list. No permission-rule syntax like `Bash(uv run *)`. Frontmatter fields used: `name`, `description`, `tools` — no `model`, `skills`, `memory`, `background`, `isolation`.

## Dependency installation

### SessionStart hook → npm install local to plugin

The SessionStart hook `hooks/ensure-cli-version.sh` runs `npm install -g codeharness@${REQUIRED_VERSION}` — installs globally into the user's npm prefix (NOT into `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}`). Dep manifest is `package.json` (Node.js) declaring `@inkjs/ui`, `ajv`, `commander`, `ink`, `react`, `lilflow`, `yaml`. Install command is exact-version-pinned (`codeharness@${REQUIRED_VERSION}`) — no floating tags, fully deterministic per-session. Opt-out via `CODEHARNESS_NO_AUTO_INSTALL=1`. Requires `npm` on PATH; if absent, prints `"npm not found — skipping auto-install. Install Node.js ≥22 manually."` and exits 0, leaving the `bin/codeharness` wrapper broken (the wrapper `exec node "$PLUGIN_ROOT/dist/index.js"` fails because there is no `dist/` in a fresh plugin clone). The hook parses `plugin.json` with `grep`+`sed` to avoid a `jq` dependency. 120-second hook timeout.

## Install change detection

### Existence-plus-version-compare

The SessionStart hook greps `"version"` out of `plugin.json`, compares to `codeharness --version` output word 1. Silent no-op when equal. No state file or stamp; the running CLI's self-reported version is the comparison anchor.

## Install failure posture

### Multi-layer fail-open with stderr advisory

The hook exits 0 on any failure with a stderr warning printed; no `rm` or state file to clear. Next session simply retries the version check. `set -uo pipefail` (no `-e`, so failures don't abort the hook). Fail-open posture — never blocks the session.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/hooks.json` registers `ensure-cli-version.sh` directly on SessionStart with matcher `*`.

## Bin entry mechanism

### Bash thin exec-delegate wrapper

`bin/codeharness` is a bash wrapper that resolves `PLUGIN_ROOT` from script location (`SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"; PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"`) and execs `node "$PLUGIN_ROOT/dist/index.js" "$@"`. Shebang `#!/usr/bin/env bash`. Does NOT consult `${CLAUDE_PLUGIN_ROOT}` — script-location is the only source. The wrapper points at `$PLUGIN_ROOT/dist/index.js`, which is not in the repo (`.gitignore` excludes `dist/`), not in the release tarball, and not built at install time. Comment claims "Used by hooks via `${CLAUDE_PLUGIN_ROOT}/bin/codeharness` so the CLI works without global npm install" — aspirational. The SessionStart hook's `npm install -g codeharness@<version>` is what actually makes the CLI usable; the bin wrapper is effectively dead code until `dist/` is shipped.

## Cross-platform discipline

### POSIX-only with no Windows story

Bash shebang only; no `.cmd` or `.ps1` counterpart for `bin/codeharness` or hooks.

## User configuration and authentication

### Out-of-band env vars (no `userConfig`)

No `userConfig` block. One env-var-based opt-out observed: `CODEHARNESS_NO_AUTO_INSTALL=1`, read directly from the environment in `ensure-cli-version.sh`. Not declared in any user-facing surface — documented only in the shell comment header of the hook script. A user who wanted to prevent the global npm write would have to read the hook source to find the flag.

## Tool-use enforcement

### No enforcement (observational only)

`hooks/hooks.json` at this ref ships only the SessionStart version-lock hook. No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks. ARCHITECTURE.md describes a richer hook surface (`pre-commit-gate.sh`, `post-write-check.sh`, `post-test-verify.sh`, `session-start.sh`) than what `hooks.json` actually wires — those scripts are not present in the shipped artifact at this ref. Documentation/implementation drift: the pattern the plugin advertises ("mechanical enforcement via Claude Code hooks") is smaller in the shipped artifact than in the docs.

## Session context loading

### Dependency install only (no context emission)

The single SessionStart hook is purely for the CLI version-lock dep install. No `additionalContext`, no `systemMessage`, no UserPromptSubmit hook. Plain stderr logging only.

## SessionStart matcher scope

### Empty matcher (all sub-events)

The SessionStart entry uses explicit `matcher: "*"` (single entry, fires on all sub-events including `startup`, `clear`, `compact`). Most plugins scope version checks to `startup` only; codeharness intentionally fires on every clear/compact too — belt-and-braces against mid-session CLI downgrade. A mid-session `/clear` could trigger a 120-second `npm install` if the global CLI got downgraded between prompts.

## Live monitoring

### `monitors.json` absent

No `monitors.json` shipped.

### Version-floor declaration absent

No declared minimum Claude Code version. `package.json` declares `engines.node >= 22` for the npm package but that is the Node runtime, not Claude Code. No detection if installed into an older Claude Code that doesn't understand `matcher: "*"` on SessionStart — in which case the hook silently never fires and the CLI never gets version-locked.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` has no `dependencies` key. The plugin integrates with BMAD Method (documented in CLAUDE.md and README) but that integration is via forked/embedded artifacts (`_bmad/`, `_bmad-output/`) and a separate skill (`skills/bmad-integration/`) — content-level, not manifest-level.

## Testing

### vitest with multi-suite layout

Vitest unit suite (1650+ tests per AGENTS.md) configured via `vitest.config.ts`. Tests located under `test/` at repo root (vitest) plus `tests/` (BATS). Vitest invocation: `npm run test:unit`.

### Hand-rolled bash tests

BATS integration tests under `tests/*.bats`. BATS is installed in CI via git clone + `/tmp/bats/install.sh` (not via a GitHub Action). Invocation: `bats tests/*.bats`. The two runners coexist — vitest for unit, BATS for shell-script integration.

## CI workflow shape

### Two-job workflow — build-and-test plus validate-plugin

`.github/workflows/ci.yml` triggers on `push: branches: [master, main]` and `pull_request: branches: [master, main]`. Two jobs: `build-and-test` (npm ci → version-sync gate → `npm run build` → `npm run test:unit` → install BATS → `bats tests/*.bats`) and `validate-plugin` (JSON parse of `plugin.json`, required-field check for name/version/description, `bash -n` syntax check on `ralph/*.sh` and `scripts/*.sh`). Pinned to `ubuntu-latest` + Node 20. Action pinning is by tag (`actions/checkout@v4`, `actions/setup-node@v4`) — no SHA pinning. No npm caching configured (`setup-node@v4` without `cache: 'npm'`). `release.yml` is a separate workflow (see Release automation).

## Release automation

### Multi-target release pipeline (npm + cross-repo marketplace dispatch)

`.github/workflows/release.yml` triggers on `release: [published]` (GitHub Release published event) OR `workflow_dispatch` with a `tag` input. Notably NOT `push: tags: ['v*']` — tag-push alone does not trigger release; `gh release create v{version} --generate-notes` is required. Three jobs: `test` (reuses CI test flow plus `npm run lint` and `npm run lint:sizes` with `FILE_SIZE_ENFORCEMENT=warn`), `publish-npm` (npm publish `--access public --provenance` via OIDC trusted publishing — no NPM_TOKEN), `marketplace` (dispatches `plugin-release` event to `iVintik/private-claude-marketplace` via `gh api repos/iVintik/private-claude-marketplace/dispatches` with `secrets.MARKETPLACE_TOKEN`). Node 20 in `test` but Node 24 in `publish-npm` — split-runtime. The `publish-npm` job re-runs `npm ci` + `npm run build` rather than consuming a built artifact from `test` — no artifact caching across jobs. No CHANGELOG.md exists; release notes come from `--generate-notes` on `gh release create` (autogenerated from commit messages). No tag-format regex check, no merge-base gate.

## Marketplace validation

### JSON-parse plus version-sync only

The `validate-plugin` job in `ci.yml` validates `plugin.json` JSON parseability and required fields (`name`, `version`, `description`) plus a shell-script syntax check (`bash -n`) on `ralph/*.sh` and `scripts/*.sh`. The `Verify version sync` step in both `ci.yml` and `release.yml` enforces `package.json.version == plugin.json.version` as a hard gate. No `claude plugin validate` CLI call; no formal JSON-schema validation; no frontmatter validation; `hooks/hooks.json` is not JSON-parse-checked. `hooks/*.sh` is notably absent from the shell-syntax glob — `ensure-cli-version.sh` could have a syntax error and CI would pass.

### Inline Python validators in CI YAML

The validation steps are inline `python3 -c` blocks within `ci.yml` (not extracted scripts). Python+json reads `plugin.json`, asserts JSON parseability and required-field presence. No `bun+zod`, no shared validator script.

## Documentation surface

### Multi-document agent-context layer

Four documents at repo root: `README.md` (~5.7 KB — install, quick start, CLI command table, plugin command table, BMAD integration, verification architecture diagram, requirements, license), `ARCHITECTURE.md` (~6.9 KB — entry point, module map, lib layout, templates, hooks-as-designed-not-as-shipped), `CLAUDE.md` (~3.8 KB — release process, two-channel distribution, BMAD phases, command reference), `AGENTS.md` (OpenAI-style agent instructions, ~3 KB — general build/test/project-structure guidance). No `CHANGELOG.md` — release notes auto-generated. README mentions Node.js >= 18 but `package.json` declares `engines.node >= 22` — docs-code drift. No badges (no CI, npm version, or license badge).

### `AGENTS.md` as ecosystem-neutral alternative to `CLAUDE.md`

`AGENTS.md` at root carries OpenAI-style cross-runtime agent instructions, distinct from `CLAUDE.md` (Claude-specific). Naming collides with the Claude Code "agents" concept (the repo also has `agents/` subdirectory with `.md` files for plugin agent definitions); a reader could conflate the two without cross-reference.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

LICENSE present at repo root (MIT). SPDX `MIT` declared in `package.json` and `plugin.json`. Single source agreement.

## Community health files

### Bare minimum (LICENSE only)

LICENSE present; no `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`. No issue templates.

## Cross-ecosystem distribution

### Dual-distribution: marketplace + npm

The plugin ships both as a Claude Code plugin (via `claude plugin install github:iVintik/codeharness` plus the private marketplace aggregator) and as an npm package (`codeharness` on npm). The SessionStart hook couples the two — installing the npm CLI globally pinned to the plugin manifest version. Cross-repo dispatch (release workflow → private marketplace repo) is the marketplace-side mechanism; OIDC trusted publishing is the npm-side mechanism.

## Cross-role tools

### Node + npm + npx

Primary runtime stack. Node 20 in CI test; Node 24 in publish job; `engines.node >= 22` in package.json. `npm install -g` is the SessionStart install path. `npm ci`, `npm run build`, `npm run test:unit`, `npm run lint`, `npm run lint:sizes` in CI.

### GitHub Releases

Required for release pipeline trigger — `release.yml` keys on `release: [published]`. Tagging alone insufficient; manual `gh release create v{version} --generate-notes` is the load-bearing step.

### `${CLAUDE_PLUGIN_ROOT}` env var

Referenced in the bin wrapper's aspirational comment ("Used by hooks via `${CLAUDE_PLUGIN_ROOT}/bin/codeharness`") but the wrapper itself uses script-location resolution rather than the env var.

### `plugin.json.version`

Read by the SessionStart hook (via grep+sed) to determine the npm pin version. Read by CI's version-sync gate to compare against `package.json.version`. The plugin manifest version drives both the npm install pin and the CI gate.

## Hook handler runtime

### Bash scripts at conventional path

Hook script `hooks/ensure-cli-version.sh` is bash. Single hook script in this category at this ref.

## Hook failure posture

### Fail-open with always-exit-0

The SessionStart hook exits 0 on any failure (network down, npm missing, install timeout). Stderr advisory printed; session proceeds. `set -uo pipefail` without `-e` means individual failed commands don't abort the script.

## Hook output contract

### Stderr for human display + stdout JSON for harness

The hook uses plain stderr logging — no structured JSON output, no `additionalContext`, no `systemMessage`. Stderr-only with no machine-parseable contract.
