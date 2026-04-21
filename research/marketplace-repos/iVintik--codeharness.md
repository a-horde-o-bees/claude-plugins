# iVintik/codeharness

## Identification

- **URL**: https://github.com/iVintik/codeharness
- **Stars**: 1
- **Last commit date**: 2026-04-14 (release: v0.47.0)
- **Default branch**: master
- **License**: MIT
- **Sample origin**: bin-wrapper
- **One-line purpose**: npm CLI + Claude Code plugin that "makes autonomous coding agents produce software that actually works — real-world verification, observability, and mechanical enforcement via Claude Code hooks"

## 1. Marketplace discoverability

- **Manifest layout**: not applicable — no `.claude-plugin/marketplace.json` at the repo root; this is a single-plugin git repo installed directly via `claude plugin install github:iVintik/codeharness`. A separate `iVintik/private-claude-marketplace` aggregator (referenced by `.github/workflows/release.yml`) handles marketplace registration via `repository_dispatch` — its contents were not researched here
- **Marketplace-level metadata**: not applicable — no marketplace manifest in this repo
- **`metadata.pluginRoot`**: not applicable
- **Per-plugin discoverability**: not applicable at the marketplace level; at the plugin level `.claude-plugin/plugin.json` carries only `name`, `version`, `description` — no `category`, `tags`, `keywords`, `author`, or `homepage`
- **`$schema`**: absent (neither on the plugin manifest nor any marketplace manifest in this repo)
- **Reserved-name collision**: no
- **Pitfalls observed**: the plugin manifest is extraordinarily minimal (236 bytes, three fields). Discoverability fields that marketplace aggregators typically surface (category, tags, author) are absent — the aggregator in `private-claude-marketplace` must supply them externally or the plugin ships without discovery metadata. The repo has no top-level GitHub description either (`gh api repos/iVintik/codeharness` returns `description: null`), so even the README-opening sentence isn't mirrored as repo metadata.

## 2. Plugin source binding

- **Source format(s) observed**: not applicable in this repo — installation is direct (`claude plugin install github:iVintik/codeharness`). The `release.yml` workflow dispatches a `plugin-release` event to `iVintik/private-claude-marketplace` with `{plugin, version}` payload; the source binding in that marketplace was not researched
- **`strict` field**: not applicable (no marketplace entry in this repo)
- **`skills` override on marketplace entry**: not applicable
- **Version authority**: both `package.json` and `.claude-plugin/plugin.json` carry the version (`0.47.0` in each); CI enforces they match via a `Verify version sync` step in both `ci.yml` and `release.yml`. Drift risk mitigated by CI gate, not by single-source derivation
- **Pitfalls observed**: dual-version-field setup requires mechanical enforcement — CI refuses builds when `package.json != plugin.json`. The CLAUDE.md explicitly warns: "After `/plugin-ops:release` bumps `plugin.json`, you MUST also update `package.json` version to match BEFORE creating the GitHub Release." The system is bilingual (npm + plugin) and the two ecosystems each insist on owning the version — the pattern here is "two sources, one gate" rather than a derived secondary field.

## 3. Channel distribution

- **Channel mechanism**: not applicable in this repo — single-channel from the plugin consumer's perspective (install from the git repo at whatever ref). The dual-channel split that exists here is npm-registry (CLI binary) vs git-repo (plugin contents), not stable-vs-latest plugin channels
- **Channel-pinning artifacts**: absent — no stable/latest split, no `release/*` branches, no dev-counter scheme. Releases are tagged on `master` directly
- **Pitfalls observed**: users installing via `claude plugin install github:iVintik/codeharness` without a `@ref` pin track `master` HEAD — there's no channel guidance in README. The plugin's SessionStart hook auto-pins the `codeharness` npm CLI to the plugin's `plugin.json` version, which is the real "channel alignment" mechanism — plugin ref and CLI version are coupled through the hook, not through a marketplace manifest.

## 4. Version control and release cadence

- **Default branch name**: master
- **Tag placement**: on master (tags are `v0.47.0`, `v0.46.0`, `v0.45.1`, `v0.45.0`, `v0.44.2` observed — all on the default branch)
- **Release branching**: none (tag-on-master)
- **Pre-release suffixes**: none observed (all tags are plain `vX.Y.Z`)
- **Dev-counter scheme**: absent — versions are real semver from the start. Current at `0.47.0`, still pre-1.0 per CLAUDE.md ("Major (X.0.0): breaking changes (not yet — still pre-1.0)")
- **Pre-commit version bump**: no — CLAUDE.md describes `/plugin-ops:release` as the release driver but no evidence of a pre-commit hook in this repo
- **Pitfalls observed**: cadence is high (v0.44.2 → v0.47.0 within days of the observed snapshot). The release workflow is triggered by a GitHub Release `published` event, not by tag push — CLAUDE.md spells out "After `/plugin-ops:release` pushes the tag, create a GitHub Release from that tag to trigger the pipeline: `gh release create v{version} --generate-notes`." Tagging alone doesn't ship; the manual release step is load-bearing.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` declares no component fields at all (just `name`, `version`, `description`). Claude Code auto-discovers the standard `commands/`, `agents/`, `skills/`, `hooks/` directories
- **Components observed**:
    - skills: yes (`skills/bmad-integration/`, `skills/visibility-enforcement/`)
    - commands: yes (`commands/harness-init.md`, `harness-docs.md`, `harness-onboard.md`, `harness-status.md`, `harness-teardown.md`; an `AGENTS.txt` also sits there — unusual)
    - agents: yes (`agents/doc-gardener.md`, `agents/verifier.md`)
    - hooks: yes (`hooks/hooks.json`, `hooks/ensure-cli-version.sh`)
    - .mcp.json: no
    - .lsp.json: no
    - monitors: no
    - bin: yes (`bin/codeharness`)
    - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `tools` (e.g., `verifier.md` declares `tools: [Bash, Read, Write, Glob, Grep, Agent]` as a YAML list). No `model`, `skills`, `memory`, `background`, `isolation` observed
- **Agent tools syntax**: plain tool names (no permission-rule syntax like `Bash(uv run *)`)
- **Pitfalls observed**: `commands/AGENTS.txt` sits alongside `.md` command files — unusual coexistence; unclear whether Claude Code's discovery treats `.txt` files gracefully (likely ignored by the command scanner but worth flagging). The bare-minimum `plugin.json` relies entirely on directory-name convention for every component — no explicit paths declared means a subdirectory rename or reorg would silently break discovery with no schema to catch it.

## 6. Dependency installation

- **Applicable**: yes — the plugin's bin-wrapped CLI requires a runtime that isn't bundled in the plugin source, so a dependency install must happen
- **Dep manifest format**: package.json (Node.js). The `dependencies` block lists `@inkjs/ui`, `ajv`, `commander`, `ink`, `react`, `lilflow`, `yaml`
- **Install location**: not the plugin directory. The SessionStart hook runs `npm install -g codeharness@${REQUIRED_VERSION}` — installs globally into the user's npm prefix, not into `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}`. This is the novel axis (see §17)
- **Install script location**: `hooks/ensure-cli-version.sh` (run by `hooks/hooks.json` on `SessionStart` matcher `*`)
- **Change detection**: version comparison — grep `"version"` out of `plugin.json`, compare to `codeharness --version` output word 1. Silent no-op when equal
- **Retry-next-session invariant**: hook exits 0 on any failure; no `rm` or state file to clear — next session simply retries the version check. If `npm install` fails, a stderr warning is printed but the session proceeds
- **Failure signaling**: stderr human-readable, `exit 0` always. Fail-open posture — never blocks the session. `set -uo pipefail` is used (no `-e`, so failures don't abort the hook)
- **Runtime variant**: Node npm — global install of the `codeharness` npm package, which supplies `dist/index.js` for the bin wrapper to `exec node` against
- **Alternative approaches**: opt-out env var `CODEHARNESS_NO_AUTO_INSTALL=1` — when set, the hook logs current state and skips the install. No `npx`/`uvx` ad-hoc variant
- **Version-mismatch handling**: exact version pin (`codeharness@${REQUIRED_VERSION}`) — no floating tags, fully deterministic per-session
- **Pitfalls observed**: the hook requires `npm` on PATH — if absent, prints `"npm not found — skipping auto-install. Install Node.js ≥22 manually."` and exits 0, leaving the `bin/codeharness` wrapper broken (the wrapper `exec node "$PLUGIN_ROOT/dist/index.js"` fails because there's no `dist/` in a fresh plugin clone). No `jq` dependency — the hook parses `plugin.json` with grep+sed to avoid that dependency. 120-second timeout on the hook might be tight for a cold `npm install -g` on a slow network.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — `bin/codeharness` is the advertised entry point
- **`bin/` files**:
    - `codeharness` — bash wrapper that resolves `PLUGIN_ROOT` from script location and execs `node "$PLUGIN_ROOT/dist/index.js" "$@"`
- **Shebang convention**: `env bash`
- **Runtime resolution**: script-relative (`SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"; PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"`). Does NOT consult `${CLAUDE_PLUGIN_ROOT}` — script-location is the only source of truth
- **Venv handling (Python)**: not applicable (Node runtime)
- **Platform support**: POSIX / nix-only (bash shebang, no `.cmd` or `.ps1` counterpart)
- **Permissions**: not independently verified via GitHub API, but given the `#!/usr/bin/env bash` shebang and direct-exec usage it must be 100755 in practice
- **SessionStart relationship**: indirect and essential — the bin wrapper points at `$PLUGIN_ROOT/dist/index.js`, which is NOT in the repo (`.gitignore` excludes `dist/`). A fresh `claude plugin install` clones only the source tree, with no build step. The wrapper would fail immediately. The SessionStart `ensure-cli-version.sh` hook sidesteps this by `npm install -g codeharness@<version>`, after which the user has a working global `codeharness` on PATH — but the plugin's own `bin/codeharness` wrapper still points at the nonexistent plugin-local `dist/`. In practice the wrapper appears vestigial: hooks and commands in this plugin call `codeharness` as a bare PATH lookup (resolving to the npm-global install), not via `${CLAUDE_PLUGIN_ROOT}/bin/codeharness`. Comment at the top of the wrapper claims "Used by hooks via `${CLAUDE_PLUGIN_ROOT}/bin/codeharness` so the CLI works without global npm install" — this is aspirational; without a pre-built `dist/` shipped in the plugin tarball it cannot be true
- **Pitfalls observed**: the bin wrapper's stated contract ("works without global npm install") is contradicted by the repo's actual shipping artifacts — `dist/` is gitignored, not a git-lfs artifact, not a release asset attached to the tarball, and no `prepare`/`postinstall` script builds it at install time. The SessionStart hook's global-install workaround is what actually makes the CLI usable, and the wrapper is effectively dead code for now. If the repo were to ship `dist/` (e.g., by inverting the `.gitignore` rule or moving to a release-tarball model), the wrapper would become self-sufficient and the SessionStart hook redundant. This is a live architectural ambiguity: two independent CLI resolution paths claim to be primary.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable. One env-var-based opt-out observed in the hook (`CODEHARNESS_NO_AUTO_INSTALL=1`) but it's read directly from the environment, not declared in any `userConfig` surface
- **Pitfalls observed**: the opt-out env var has no discoverability — it's documented only in the shell comment header of `ensure-cli-version.sh`. A plugin user who wanted to prevent the global npm write would have to read the hook source to find the flag. A `userConfig` field with a `boolean` type and description would surface it in the plugin configuration UI.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none observed in `hooks/hooks.json`. ARCHITECTURE.md references a `pre-commit-gate.sh` ("PreToolUse (Bash) — Gate commits: require tests passed, coverage met") but that file isn't wired into the published `hooks.json` at the sampled ref — likely local-development/future content described in architecture docs but not shipped
- **PostToolUse hooks**: none in `hooks.json` at this ref (ARCHITECTURE.md mentions `post-write-check.sh` and `post-test-verify.sh` — similarly unwired)
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: not applicable (no tool-use enforcement hooks shipped)
- **Failure posture**: not applicable
- **Top-level try/catch wrapping**: not applicable
- **Pitfalls observed**: documentation/implementation drift — ARCHITECTURE.md describes a richer hook surface (`pre-commit-gate.sh`, `post-write-check.sh`, `post-test-verify.sh`, `session-start.sh`) than `hooks.json` actually wires. The shipped config has exactly one SessionStart hook (the version-lock). Either the other hooks are future work or they're invoked via a different mechanism (e.g., orchestrated by the CLI itself rather than Claude Code hooks). This is a research-relevant gap — the pattern the plugin advertises ("mechanical enforcement via Claude Code hooks") is smaller in the shipped artifact than in the docs.

## 10. Session context loading

- **SessionStart used for context**: no — used only for the CLI version-lock dep install (see §6)
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no — the hook uses plain stderr logging, no structured JSON output
- **SessionStart matcher**: `*` (single entry, fires on all sub-events — `startup`, `clear`, `compact`)
- **Pitfalls observed**: using `matcher: "*"` means the expensive-ish version check + potential `npm install -g` runs on every clear/compact too, not just cold startup. Most plugins scope version checks to `startup` only. This is intentional belt-and-braces — but it means a mid-session `/clear` could trigger a 120-second `npm install` if the user had somehow downgraded the global CLI between prompts.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: absent — no declared minimum Claude Code version. `package.json` declares `engines.node >= 22` for the npm package but that's the Node runtime, not Claude Code
- **Pitfalls observed**: no version-floor means the plugin can be installed into older Claude Code versions that might not understand, e.g., `matcher: "*"` on SessionStart — in which case the hook silently never fires and the CLI never gets version-locked. No detection of this failure mode.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin repo)
- **Pitfalls observed**: the plugin integrates with BMAD Method (documented in CLAUDE.md and README) but that integration is via forked/embedded artifacts (`_bmad/`, `_bmad-output/`) and a separate skill (`skills/bmad-integration/`) — not a plugin dependency. The integration is content-level, not manifest-level. If BMAD Method ever ships as a Claude Code plugin, a `dependencies` entry would be a cleaner binding.

## 13. Testing and CI

- **Test framework**: multiple — vitest (1650+ unit tests per AGENTS.md) and BATS (shell-script integration tests via `bats tests/*.bats`)
- **Tests location**: `tests/` at repo root (BATS) and `test/` also exists at root (vitest likely via `vitest.config.ts`). Plus a `verification/` directory for Showboat proof docs (product artifact, not test code)
- **Pytest config location**: not applicable (no Python). Vitest config in `vitest.config.ts`
- **Python dep manifest for tests**: not applicable
- **CI present**: yes
- **CI file(s)**: `.github/workflows/ci.yml`, `.github/workflows/release.yml`
- **CI triggers**: `ci.yml` on `push: branches: [master, main]` and `pull_request: branches: [master, main]`; `release.yml` on `release: [published]` and `workflow_dispatch` with a `tag` input
- **CI does**:
    - `ci.yml` — two jobs: `build-and-test` (npm ci → version-sync gate → `npm run build` → `npm run test:unit` → install BATS → `bats tests/*.bats`) and `validate-plugin` (JSON parse of `plugin.json`, required-field check for name/version/description, `bash -n` syntax check on `ralph/*.sh` and `scripts/*.sh`)
    - `release.yml` — three jobs: `test` (reuses the CI test flow plus `npm run lint` and `npm run lint:sizes` with `FILE_SIZE_ENFORCEMENT=warn`), `publish-npm` (npm publish `--access public --provenance` via OIDC, no NPM_TOKEN), `marketplace` (dispatches `plugin-release` event to `iVintik/private-claude-marketplace`)
- **Matrix**: none — `ci.yml` pins `ubuntu-latest` + Node 20; `release.yml` uses Node 20 for `test` and Node 24 for `publish-npm`
- **Action pinning**: tag (`actions/checkout@v4`, `actions/setup-node@v4`) — no SHA pinning
- **Caching**: none — `setup-node@v4` is configured without the `cache: 'npm'` option, so `npm ci` pays the full download cost every run
- **Test runner invocation**: `npm run test:unit` (vitest), `bats tests/*.bats` (BATS installed via git clone + `/tmp/bats/install.sh` — not via GitHub Action)
- **Pitfalls observed**: Node 20 in `test` but Node 24 in `publish-npm` — split-runtime guards against the "tests pass on 20 but publish fails on 24" failure mode only by luck; an npm engines-compatibility issue could slip through. Also the `publish-npm` job re-runs `npm ci` + `npm run build` rather than consuming a built artifact from `test` — no artifact caching across jobs, so the built `dist/` the tests validated is not the `dist/` that ships to npm (rebuild from source both times). For a small CLI this is fine; for a release pipeline that cares about reproducibility it's a gap.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes
- **Release trigger**: `release: [published]` (GitHub Release published event) OR `workflow_dispatch` with a `tag` input. Notably NOT `push: tags: ['v*']` — tag-push alone does not trigger a release; a GitHub Release must be created from the tag (CLAUDE.md: `gh release create v{version} --generate-notes`)
- **Automation shape**: npm publish with `--provenance` (OIDC trusted publishing, no NPM_TOKEN) + marketplace-dispatch to a sibling repo. No skill-zip, no tarball attach, no binary build (Node source-based)
- **Tag-sanity gates**: version-sync between `package.json` and `plugin.json` — enforced in the `test` job before anything publishes. No verify-tag-on-main, no tag-format regex check
- **Release creation mechanism**: `gh release create` (manual, per CLAUDE.md instructions — not automated)
- **Draft releases**: no — releases are published directly
- **CHANGELOG parsing**: no CHANGELOG.md exists in the repo. Release notes come from `--generate-notes` on the `gh release create` call, which autogenerates from commit messages
- **Pitfalls observed**: releases hinge on a human running `gh release create` — if they tag but don't create the release, npm never publishes. The `workflow_dispatch` escape hatch takes a `tag` input but the `test` job checks out `ref: ${{ github.event.inputs.tag || github.ref }}` — which works only if the tag exists at dispatch time. The `marketplace` job does `gh api repos/iVintik/private-claude-marketplace/dispatches` with `secrets.MARKETPLACE_TOKEN` — cross-repo dispatch requires a PAT or app token scoped to the marketplace repo, not the default `GITHUB_TOKEN`. That coupling is opaque — a forked user could never release because they lack that token.

## 15. Marketplace validation

- **Validation workflow present**: yes (partial) — the `validate-plugin` job in `ci.yml` validates `plugin.json` JSON parseability, required fields (`name`, `version`, `description`), and shell-script syntax for `ralph/*.sh` + `scripts/*.sh`
- **Validator**: Python+json (inline `python3 -c` blocks) — no `bun+zod`, no `claude plugin validate` CLI, no formal JSON-schema validation
- **Trigger**: `push` + `pull_request` on master/main (same as the build-and-test job)
- **Frontmatter validation**: no — agent/skill/command frontmatter is not validated
- **Hooks.json validation**: no — `hooks/hooks.json` is not JSON-parse-checked
- **Pitfalls observed**: validation is limited to three hand-picked fields of `plugin.json`. A malformed `hooks/hooks.json` (missing required fields, wrong event name, invalid matcher) would pass CI and fail silently at Claude Code session start. Shell-syntax check is good, but only covers `ralph/*.sh` + `scripts/*.sh` — `hooks/*.sh` is notably absent from the glob, so `ensure-cli-version.sh` could have a syntax error and CI would pass.

## 16. Documentation

- **`README.md` at repo root**: present (~5.7 KB, substantive — install, quick start, CLI command table, plugin command table, BMAD integration, verification architecture diagram, requirements, license)
- **`README.md` per plugin**: not applicable (single-plugin repo)
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: present at repo root (`ARCHITECTURE.md`, ~6.9 KB) — describes entry point, module map, lib layout, templates, hooks (as-designed, not as-shipped — see §9)
- **`CLAUDE.md`**: present at repo root (~3.8 KB) — release process, two-channel distribution, BMAD phases, command reference
- **Community health files**: `AGENTS.md` at root (OpenAI-style agent instructions, ~3 KB) — unusual naming collision with the Claude Code "agents" concept but content is general build/test/project-structure guidance
- **LICENSE**: present (MIT)
- **Badges / status indicators**: absent — no CI badge, no npm version badge, no license badge
- **Pitfalls observed**: `AGENTS.md` at root and `agents/` subdirectory with `.md` files share naming with no cross-reference — a reader might conflate OpenAI's AGENTS.md convention with Claude Code's agents/ plugin directory. README mentions Node.js >= 18 but `package.json` declares `engines.node >= 22` — docs-code drift. No CHANGELOG means the only way to learn what changed between v0.46.0 and v0.47.0 is `git log` or GitHub Release auto-generated notes.

## 17. Novel axes

- **SessionStart → global npm install as a version-lock channel.** The plugin's SessionStart hook runs `npm install -g codeharness@<version>` pinned to the plugin's own `plugin.json` version. The plugin effectively "installs its own CLI peer" as a side effect of session startup. This couples plugin-ref and npm-version at the hook layer rather than via a package manifest dependency. Opt-out via `CODEHARNESS_NO_AUTO_INSTALL=1`. Worth a pattern-doc axis of its own: "plugin auto-pins a global tool dependency at SessionStart" is a distinct mechanism from "plugin installs its Python deps into its own venv."
- **Dual-manifest versioning with CI gate.** Neither `package.json` nor `.claude-plugin/plugin.json` derives from the other — both are authoritative in their own ecosystem and CI enforces equality as a hard gate. Different from single-source-of-truth patterns (e.g., one file sed'd into the other at build time).
- **bin-wrapper as aspirational contract.** The `bin/codeharness` wrapper points at a path (`dist/index.js`) that isn't in the repo, isn't in the release tarball, and isn't built at install time. Its comment claims it "works without global npm install" but in shipping reality the SessionStart hook's `npm install -g` is what makes the CLI available. This is a live pattern mismatch — wrapper-as-documentation vs wrapper-as-runtime.
- **Cross-repo marketplace dispatch.** Release publishes both to npm AND dispatches a `plugin-release` event to a private marketplace repo. The marketplace itself isn't public, but the pattern of "plugin repo as source, separate aggregator repo as marketplace" is visible in the workflow — worth contrasting against self-contained marketplaces.
- **`engines.node >= 22` while CI tests on Node 20.** The `test` job sets `node-version: '20'` but `package.json` engines declares `>=22`. Tests would fail to `npm ci` if dependencies hard-require Node 22 features, but currently pass — indicating the engines floor is aspirational.
- **Verification as a product concept, Showboat.** `verification/` directory holds "Showboat proof documents" — per-story evidence artifacts. Not a plugin-infrastructure axis but a novel answer to "how does an agent prove a feature works" that sits at the boundary of agent tooling.

## 18. Gaps

- **marketplace.json contents.** The `iVintik/private-claude-marketplace` aggregator repo is private (name implies it). Its manifest layout, source format, `strict` handling, and whether it carries `category`/`tags`/`keywords` for this plugin are unknown. Resolvable only with access to that repo — out of budget here.
- **Actual shipped `dist/` contents in npm tarball.** Couldn't inspect `npm view codeharness@0.47.0 dist.tarball` contents to confirm `dist/` is there and what the bundled `index.js` looks like. Would resolve whether the bin wrapper would work if users happened to also clone into a path with a pre-built `dist/`. Resolvable via `npm pack codeharness@0.47.0 && tar tzf *.tgz`.
- **Bin file permissions.** GitHub's contents API doesn't return Unix permission bits for individual files — couldn't confirm `bin/codeharness` is 100755 vs 100644. Resolvable with `git clone` + `ls -la bin/`.
- **Hook file presence mismatch.** ARCHITECTURE.md describes `session-start.sh`, `pre-commit-gate.sh`, `post-write-check.sh`, `post-test-verify.sh` but `hooks/` at this ref only contains `ensure-cli-version.sh` + `hooks.json`. Unclear whether these are future/unimplemented, deleted, or invoked via a different path (e.g., the `codeharness` CLI registers them dynamically). Resolvable by grepping the CLI source or earlier commits.
- **BATS integration test scope.** Didn't inspect `tests/*.bats` contents — what integration surface the BATS tests cover (CLI behavior? hook behavior? plugin-lifecycle behavior?) is unresolved. Resolvable via `gh api repos/iVintik/codeharness/contents/tests`.
- **Circuit-breaker artifacts at repo root.** `.circuit_breaker_history`, `.circuit_breaker_state`, `.ralph/`, `sprint-state.json`, `.tmp-review-run-XXXX.ts`, `.tmp-review-runctx-XXXX.ts` suggest runtime state is committed alongside source. Whether this is intentional (reproducible sprint history) or accidental (missed gitignore entries) is unclear. Resolvable by reading `.gitignore` in full and checking recent commit messages for context.
