# stellarlinkco/myclaude

## Identification

- **URL**: https://github.com/stellarlinkco/myclaude
- **Stars**: 2606
- **Last commit date**: 2026-04-09 (master `c4a1567129`)
- **Default branch**: `master`
- **License**: AGPL-3.0
- **Sample origin**: bin-wrapper (primary focus); also a multi-plugin marketplace and dep-management case (Go binary download via `install.sh`)
- **One-line purpose**: Multi-agent development workflow distribution (BMAD / requirements / dev-kit / OmO / SPARV) with an npx self-installer that stitches the marketplace layout onto a mutually-exclusive "modules + skills" installer config

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: top-level `name` / `version` / `description` / `owner` (no `metadata.{...}` wrapper). `version` (5.6.1) at the marketplace level is set independently of individual plugin versions and drifts against `package.json` version (6.7.0)
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `category` only (values: `development` on four plugins, `productivity` on `dev-kit`). No `tags` and no `keywords`. No `strict` field on any entry
- **`$schema`**: present — `https://anthropic.com/claude-code/marketplace.schema.json`
- **Reserved-name collision**: no (plugin names: `omo`, `requirements`, `bmad`, `dev-kit`, `sparv`)
- **Pitfalls observed**: the marketplace lists 5 plugins; the sibling `config.json` the npx installer consumes declares 8+ modules (adds `course`, `harness`, `claudekit`, `do`) plus a separate "skills" axis (`browser`, `codeagent`, `codex`, `dev`, `gemini`, `product-requirements`, `prototype-prompt-generator`, `skill-install`, `test-cases`). The two inventories are intentionally disjoint — slash-command install via `/plugin marketplace add` gets the 5-plugin subset; npx install gets the richer module/skill menu. Version authority is also split (marketplace 5.6.1, npx package 6.7.0; plugin.json files lag at 5.6.1 / 1.1.0)

## 2. Plugin source binding

- **Source format(s) observed**: relative only — each plugin's `source` is a relative path like `./skills/omo` or `./agents/bmad`
- **`strict` field**: default (implicit true) on every entry — no explicit value observed
- **`skills` override on marketplace entry**: absent
- **Version authority**: marketplace entry and plugin.json both carry versions (`5.6.1` on most, `1.1.0` for sparv in both places). Neither references the other. The npx package.json carries its own `6.7.0`. Drift is pervasive: marketplace and plugin.json agree internally but the whole `.claude-plugin/` tree is out of sync with the npx distribution version
- **Pitfalls observed**: three parallel version spaces — marketplace+plugin.json (5.6.1), package.json (6.7.0), git tags (v6.8.2 most recent). A consumer installing via `/plugin marketplace add` gets 5.6.1 artifacts; a consumer running `npx ...` gets master-at-latest-tag (v6.8.2 as of snapshot). `plugin.json` carries no `name` collision with `source` paths, but `dev-kit` (marketplace name) maps to `./agents/development-essentials` whose `plugin.json` declares `"name": "essentials"` — the two names disagree

## 3. Channel distribution

- **Channel mechanism**: no split — users always pin via `@ref` (or default to latest release tag via the npx installer). The `--tag <tag>` CLI flag on `bin/cli.js` is the sole channel-pinning mechanism
- **Channel-pinning artifacts**: absent. Release branches observed (`rc/*` pattern in CI triggers), but no stable/latest split in marketplace.json
- **Pitfalls observed**: none specific — the repo uses tags-on-master as the single release channel, with the npx installer defaulting to the GitHub releases "latest" endpoint. An `rc/*` branch pattern is declared in CI triggers but no release artifact ties to it

## 4. Version control and release cadence

- **Default branch name**: `master`
- **Tag placement**: on master (tags-on-master model); `rc/*` branches exist but no tags observed on them
- **Release branching**: none for semver; `rc/*` pattern used for pre-merge validation in CI only
- **Pre-release suffixes**: none observed in the tag list sampled (v3.1 … v6.8.2); all clean semver
- **Dev-counter scheme**: absent — 78 tags total, all real semver, no `0.0.z` dev counter
- **Pre-commit version bump**: no pre-commit hook observed; CHANGELOG is generated via `git-cliff` (cliff.toml present), run manually via `make changelog`
- **Pitfalls observed**: tags march forward (v6.8.x) while in-repo version strings lag several minor versions behind (marketplace.json 5.6.1, package.json 6.7.0). The npx installer asks GitHub's releases API for `tag_name` at runtime to resolve the download, so installed artifacts match the tag — but a consumer reading the checked-in files sees stale version fields

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery (no component fields). Every plugin.json is minimal: `name`, `description`, `version`, `author` — nothing else. Components are found by directory convention (`agents/`, `commands/`, `hooks/`, etc. under the plugin root)
- **Components observed**:
    - skills — yes (`./skills/omo`, `./skills/sparv` are whole-skill plugins; `./skills/do`, `./skills/dev`, etc. ship as npx-selectable skills)
    - commands — yes (`./agents/bmad/commands/`, `./agents/requirements/commands/`, `./agents/development-essentials/commands/`)
    - agents — yes (`./agents/bmad/agents/` with 7 role agents; similar for requirements)
    - hooks — yes (two locations: repo-root `hooks/hooks.json` serving the `claudekit` npx module, and `./skills/sparv/hooks/hooks.json` for the SPARV skill)
    - .mcp.json — no
    - .lsp.json — no
    - monitors — no
    - bin — yes (`./bin/cli.js` at repo root — the npx installer itself, not a plugin-level bin)
    - output-styles — referenced in Makefile as `$(OUTPUT_STYLES_DIR)/bmad.md` but the directory is not checked into the sampled tree (Makefile is a legacy path)
- **Agent frontmatter fields used**: `name`, `description` only (observed on `bmad-architect.md`). No `model`, `tools`, `skills`, `memory`, `background`, `isolation`
- **Agent tools syntax**: not applicable — no `tools` field observed on agent frontmatter
- **Pitfalls observed**: the repo distributes components via three parallel paths: (1) marketplace.json plugins for the slash-command flow, (2) config.json modules for the npx flow (operations: `copy_file`, `copy_dir`, `merge_dir`, `run_command`), (3) legacy Makefile targets (`deploy-bmad`, etc.). Each path registers components differently — the marketplace path relies on plugin directory conventions, the npx path enumerates operations explicitly per module

## 6. Dependency installation

- **Applicable**: yes — Go binary (`codeagent-wrapper`) is a runtime dependency of the `do` and `omo` modules; npx install of those modules triggers `bash install.sh` to download it
- **Dep manifest format**: `codeagent-wrapper/go.mod` for the bundled Go binary source; `package.json` for the npx CLI's own (nil) runtime deps; `config.json` for the declarative module/operation registry consumed by the installer
- **Install location**: `${INSTALL_DIR}/bin/codeagent-wrapper` where `INSTALL_DIR` defaults to `~/.claude`. Not under `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}` — the installer writes directly into the user's claude config directory because this is a pre-plugin-era bin-wrapper shape
- **Install script location**: `/install.sh` at repo root (plus `/install.bat` for Windows and `/install.py` legacy). Not inline in hooks.json
- **Change detection**: none beyond existence — `copyFile` refuses overwrite unless `--force`; `copyDirRecursive` skips if destination exists. No hash, sha, mtime, or version-stamp comparison. `--update` re-runs with `force: true` implicitly via re-copy after fetching the new tag. `installed_modules.json` records what was installed but is metadata-only (tracks installed_at timestamp, not hashes)
- **Retry-next-session invariant**: not applicable in the SessionStart-hook sense — install is a user-invoked one-shot. The installer does `tmp` directory cleanup in a `finally` block regardless of failure, so a crashed install leaves no stale tempdir
- **Failure signaling**: install script uses `set -e` (halt on first error); download failure prints `ERROR: failed to download binary` to stderr and exits 1. `runInstallSh` in cli.js rejects the promise with `install script failed (exit ${code})`. Top-level `.catch` in cli.js writes `ERROR: <msg>` to stderr and `process.exit(1)`. No JSON `systemMessage`, no `continue: false` — this is user-facing CLI output, not hook JSON
- **Runtime variant**: mixed — Node.js for the installer CLI (only stdlib: `https`, `zlib`, `fs`, `crypto`, `child_process`, `readline`, `os`, `path` — zero npm deps); Go for the `codeagent-wrapper` binary distributed as prebuilt per-OS/arch artifact; Python for some hook scripts (`pre-bash.py`, `inject-spec.py`, `log-prompt.py`) and the legacy `install.py`
- **Alternative approaches**: prebuilt-binary-per-platform (Go release artifacts) rather than PEP 723, pointer-file, or `uvx`/`npx`. The `install.sh` script detects OS and arch (`uname -s`, `uname -m`) and composes the download URL
- **Version-mismatch handling**: none — if the wrapper binary's protocol drifts from what the skills expect, the `printPostInstallInfo` step runs `codeagent-wrapper --version` and prints the version but doesn't gate or warn on compatibility
- **Pitfalls observed**: `install.sh` appends `$BIN_DIR` to shell config files (via `auto-add to shell config files with idempotency` block — code truncated in sample) — this is an auto-modification of user dotfiles that cuts against the plugin-era convention of keeping the bin under `${CLAUDE_PLUGIN_ROOT}` and letting Claude Code resolve it. The bin-wrapper approach documented here is a pre-plugin installer that happens to also ship a marketplace.json

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — `bin/cli.js` is the canonical self-installer/updater (the focus of this research)
- **`bin/` files**: one file, `cli.js` — a 1,285-line Node.js CLI that (a) parses args, (b) talks to GitHub API (`api.github.com/repos/.../releases/latest`, `api.github.com/repos/.../contents/*`), (c) downloads `codeload.github.com/.../tar.gz/refs/tags/<tag>`, (d) extracts tarball with a hand-written in-memory `extractTarGz` (no `tar` package dependency), (e) renders an interactive `readline`-raw-mode multiselect for module picking, (f) executes `copy_file` / `copy_dir` / `merge_dir` / `run_command` operations per `config.json` module definitions, (g) merges per-module hook entries into `~/.claude/settings.json` under a `__module__` tag for surgical unmerge on uninstall, (h) merges per-module agent entries into `~/.codeagent/models.json`, (i) records results to `~/.claude/installed_modules.json`
- **Shebang convention**: `#!/usr/bin/env node` (single-file Node entry — `package.json` `"bin": {"myclaude": "bin/cli.js"}` tells npm/npx to run this)
- **Runtime resolution**: `repoRootFromHere()` resolves via `path.resolve(__dirname, "..")` — i.e. script-relative. When a `--tag` is specified or fetched from the latest-release endpoint, the CLI downloads a fresh tarball to `os.tmpdir()` and uses the extracted dir as `repoRoot`, overriding the local reference. No `${CLAUDE_PLUGIN_ROOT}` — this is not a plugin-era bin
- **Venv handling (Python)**: not applicable — the bin is Node.js and orchestrates, not Python; the legacy `install.py` (1,533 lines) exists alongside but is not what npx invokes
- **Platform support**: cross-platform by design — `install.sh` for POSIX, `install.bat` and `test_install_path.bat` for Windows, `cli.js` uses `process.platform === "win32"` checks throughout (`cmd.exe /c install.bat` vs `bash install.sh`; `where` vs `which`)
- **Permissions**: `cli.js` preserved as 100755 (executable) by npm's bin-install; the Go binary is `chmod +x` by `install.sh` after download
- **SessionStart relationship**: not applicable — install is user-invoked via `npx github:stellarlinkco/myclaude`, not triggered from a hook. The CLI does not interact with Claude Code hooks at install time beyond writing the hook config into `~/.claude/settings.json`
- **Pitfalls observed**: the CLI hand-rolls tar extraction, GitHub API client, https download, and interactive multiselect — all with zero npm runtime dependencies. This is unusual and an asset (no supply-chain surface) but also a maintenance burden: the `extractTarGz` function implements TAR parsing from scratch including pad-block handling, type-53 directory detection, and path-safety checks (`safePosixPath` rejects `/`-rooted, `..`-containing, and `/../` paths). The CLI also talks to `api.github.com` without auth — unauthenticated rate limit of 60 req/h per IP is the ceiling

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none in marketplace.json. The installer reads its own config via `~/.codeagent/models.json` (API keys, agent presets per backend) but that is not a `userConfig` in the Claude Code sense — it is a separate runtime config file for the `codeagent-wrapper` Go binary
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: `${CLAUDE_PLUGIN_ROOT}` is used in the repo-root `hooks/hooks.json` commands (e.g., `python3 ${CLAUDE_PLUGIN_ROOT}/pre-bash.py ...`) and the Node.js installer re-implements substitution via `replaceHookVariables` when merging module hook configs. `${SKILL_PATH}` is used in `skills/sparv/hooks/hooks.json` — this is a SPARV-internal convention, not a Claude Code built-in variable, so its resolution depends on runtime env being set by the consumer
- **Pitfalls observed**: `${SKILL_PATH}` substitution in sparv's hooks.json is not a Claude Code platform variable; if Claude Code's hook-runtime env doesn't populate it, the hook command dereferences an empty string and the `[ -f .sparv/state.yaml ] && ${SKILL_PATH}/scripts/...` guard silently no-ops (absent file path) — fail-open but hides missing-env misconfiguration

## 9. Tool-use enforcement

- **PreToolUse hooks**: 2 matchers observed
    - repo-root `hooks/hooks.json` (claudekit module): `Bash` matcher → runs `pre-bash.py "$CLAUDE_TOOL_INPUT"` and `inject-spec.py` (dangerous command blocking + spec injection)
    - `skills/sparv/hooks/hooks.json`: `Edit|Write` matcher → `check-ehrb.sh --diff --dry-run` (risk detection for modifications, gated on `.sparv/state.yaml` existence)
- **PostToolUse hooks**: 1 matcher — sparv `Edit|Write|Bash|Read|Glob|Grep` → `save-progress.sh` (journal entry on every relevant tool use, gated on `.sparv/state.yaml`)
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: scripts invoked directly via `bash`/`python3`; commands are wrapped in `[ -f .sparv/state.yaml ] && ... || true` so a non-zero exit is swallowed (fail-open). Output convention is stderr-human (no stdout JSON), since the sparv scripts' outputs look like human messages
- **Failure posture**: fail-open — the `|| true` suffix ensures non-zero exits don't block the tool. The repo-root `pre-bash.py` (which implements the dangerous-command blocker) has no such guard, so its non-zero exit would block Bash as intended
- **Top-level try/catch wrapping**: not observable without reading the Python sources (`pre-bash.py` is 536 bytes — minimal); the shell hooks use `|| true`
- **Pitfalls observed**: the sparv `PostToolUse` matcher `Edit|Write|Bash|Read|Glob|Grep` fires on nearly every tool call, writing a journal line per call. If sparv is active (`.sparv/state.yaml` exists) the journal file grows unboundedly fast — this is the documented "2-action save" protocol but volume grows linearly with work

## 10. Session context loading

- **SessionStart used for context**: no — there is no `SessionStart` hook in any checked-in hooks.json
- **UserPromptSubmit for context**: yes — repo-root `hooks/hooks.json` has `UserPromptSubmit` → `log-prompt.py` (logging, not injection — name implies prompt logging, not context injection)
- **`hookSpecificOutput.additionalContext` observed**: not observed (would require reading `log-prompt.py` and `inject-spec.py` Python sources; both are small but not fetched). `inject-spec.py` is on `PreToolUse:Bash` which is an unusual place for context injection — more likely it rewrites the bash command than emits additional context
- **SessionStart matcher**: not applicable — no SessionStart hook
- **Pitfalls observed**: none — the repo does not lean on SessionStart. Context injection appears to happen at prompt-submit and bash-preuse stages, both deterministic trigger points

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none — monitors not used

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: no — tags are flat `v6.8.2`-style across the whole repo. The marketplace is multi-plugin but single-version (every plugin shares the same `5.6.1`)
- **Pitfalls observed**: none at the marketplace-schema level. The npx installer encodes inter-module wrapper dependencies programmatically (`WRAPPER_REQUIRED_MODULES = new Set(["do", "omo"])`, `WRAPPER_REQUIRED_SKILLS = new Set(["dev"])` in cli.js) rather than declaring them in config.json — "if you select `do` or `omo`, also run `install.sh` for the `codeagent-wrapper` binary". This is implicit module dependency baked into the installer, not declarative

## 13. Testing and CI

- **Test framework**: `go test` (for the `codeagent-wrapper` Go binary under `codeagent-wrapper/`). No Python / Node test framework observed at repo root
- **Tests location**: inside `codeagent-wrapper/` (co-located with Go source per Go convention). `scripts/` subdir of codeagent-wrapper likely holds test helpers
- **Pytest config location**: not applicable (no Python test suite)
- **Python dep manifest for tests**: not applicable
- **CI present**: yes
- **CI file(s)**: `.github/workflows/ci.yml` (861 bytes) + `.github/workflows/release.yml` (3,906 bytes)
- **CI triggers**: `ci.yml` → `push` on `master` and `rc/*`; `pull_request` on same. `release.yml` → `push: tags: ['v*']`
- **CI does**: `go test -v -cover -coverprofile=coverage.out ./...` inside `codeagent-wrapper/`, then `go tool cover -func=coverage.out | grep total | awk '{print $3}'` to print coverage, then codecov upload (continue-on-error)
- **Matrix**: `os: [ubuntu-latest, windows-latest, macos-latest]` — three-OS matrix, Go 1.21 fixed version
- **Action pinning**: tag-style (`actions/checkout@v4`, `actions/setup-go@v5`, `codecov/codecov-action@v4`). No SHA pinning
- **Caching**: built-in `setup-go` cache (implicit default in actions/setup-go@v5)
- **Test runner invocation**: direct `go test` via bash step in workflow (`shell: bash`)
- **Pitfalls observed**: only the Go binary is tested. The Node.js installer (`bin/cli.js`, 1,285 lines) has no tests — `test_install_path.bat` is a 1,946-byte Windows-only smoke script, not a real test suite. The Python hooks (`pre-bash.py`, `inject-spec.py`, `log-prompt.py`) and the 1,533-line `install.py` have no tests in CI. Coverage enforcement is absent — the awk pipeline prints coverage but doesn't fail the build below a threshold

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes
- **Release trigger**: `push: tags: ['v*']`
- **Automation shape**: prebuilt-binary build + attach. Matrix builds `codeagent-wrapper` for 6 targets (linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64, windows/arm64) with `CGO_ENABLED=0` and version stamped via `-ldflags="-s -w -X codeagent-wrapper/internal/app.version=${VERSION}"`, uploads all artifacts + `install.sh` / `install.bat` via `softprops/action-gh-release@v2`. Release notes generated inline via `git log ${PREVIOUS_TAG}..${TAG} --pretty=format:"- %s (%h)" --no-merges` (not from CHANGELOG.md — git-cliff produces CHANGELOG.md separately via the `make changelog` target)
- **Tag-sanity gates**: none — no verify-tag-on-master, no verify-tag-matches-package-version, no tag-format regex. A stray `v` tag triggers the release job
- **Release creation mechanism**: `softprops/action-gh-release@v2`
- **Draft releases**: no (`draft: false`, `prerelease: false`)
- **CHANGELOG parsing**: no (CHANGELOG.md exists and is git-cliff-maintained, but the release workflow generates its notes ad-hoc from `git log`, bypassing the CHANGELOG)
- **Pitfalls observed**: two sources of truth for release notes — `CHANGELOG.md` (Keep-a-Changelog-style, git-cliff generated, manually run) and the release-workflow-generated `release_notes.md` (raw git log). They diverge immediately: CHANGELOG groups by feat/fix/docs; the workflow emits a flat `- <subject> (<hash>)` list. Tag-sanity gates absent means package.json's version field (`6.7.0`) can lag tags (`v6.8.2`) indefinitely — which is what happened

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable. `config.schema.json` exists and the legacy `install.py` uses `jsonschema` to validate `config.json` at install-time — but this is user-runtime validation, not CI validation. The marketplace.json's `$schema` reference points at `anthropic.com/claude-code/marketplace.schema.json` (remote schema, not locally validated)
- **Trigger**: not applicable
- **Frontmatter validation**: no
- **Hooks.json validation**: no
- **Pitfalls observed**: marketplace.json and plugin.json files have no CI-side lint or schema check. The `config.schema.json` governs the npx installer's `config.json` but is only enforced by `install.py` at runtime (not by `cli.js`, which parses config.json with `JSON.parse` and trusts the structure)

## 16. Documentation

- **`README.md` at repo root**: present (6,035 bytes, with bilingual companion `README_CN.md` at 8,035 bytes)
- **`README.md` per plugin**: present on most (`./agents/bmad/README.md`, `./agents/requirements/README.md`, `./agents/development-essentials/README.md`, `./skills/omo/README.md`, `./skills/sparv/README.md`); `codeagent-wrapper/` has its own `README.md` + `README_CN.md` + `USER_GUIDE.md`
- **`CHANGELOG.md`**: present (21,255 bytes) — Keep a Changelog format with emoji section markers (🚀 Features, 🐛 Bug Fixes, 📚 Documentation, 🚜 Refactor), generated by git-cliff per cliff.toml
- **`architecture.md`**: absent at repo root and per plugin
- **`CLAUDE.md`**: present at `./memorys/CLAUDE.md` (not at repo root) — copied to install target by `installDefaultConfigs` in cli.js. Per plugin: absent
- **Community health files**: none observed (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`)
- **LICENSE**: present (SPDX: `AGPL-3.0`, file size 34,523 bytes). Commercial licensing available via `support@stellarlink.co` per README
- **Badges / status indicators**: observed (Smithery, License, Claude Code, Version)
- **Pitfalls observed**: no `architecture.md` at any level — design rationale (why Node.js self-installer, why zero-deps, why parallel marketplace+config.json inventories, why `installed_modules.json` records only metadata not hashes) is undocumented. CHANGELOG dates (2026-01-26, 2026-02-10) predate the last-commit date (2026-04-09) — the changelog hasn't been regenerated recently

## 17. Novel axes

- **Zero-dependency Node.js self-installer as the primary distribution channel.** `bin/cli.js` implements its own GitHub API client, https downloader, tar.gz extractor, interactive multiselect, and archive path-safety validator — all with only Node stdlib. Invoked as `npx github:stellarlinkco/myclaude` (no npm registry publish). The marketplace.json is the secondary channel; the README says "Quick Start: npx github:stellarlinkco/myclaude" before mentioning the `/plugin marketplace add` form
- **Two parallel plugin inventories.** `.claude-plugin/marketplace.json` lists 5 plugins for the slash-command install flow; `config.json` declares 8+ modules + a skills axis for the npx installer flow. They share some entries (omo, sparv) but the npx inventory is strictly larger and uses a richer operation model (`copy_file`, `copy_dir`, `merge_dir`, `run_command`) with per-module agent-preset merging into `~/.codeagent/models.json`
- **Hook-config stitching with `__module__` tag.** When the installer merges a module's `hooks/hooks.json` into `~/.claude/settings.json`, it tags every hook entry with `__module__: <name>`. Uninstall scans settings.json and removes only entries with the matching tag, leaving user-added hooks untouched. This is a surgical unmerge strategy worth naming in the pattern doc
- **Operations DSL in config.json.** The npx installer's `config.json` defines modules as a sequence of operations (`copy_file`, `copy_dir`, `merge_dir`, `run_command`) with a dedicated `config.schema.json`. `run_command` is restricted at the installer level to exactly `"bash install.sh"` — no arbitrary commands — which is an interesting minimum-capability safeguard on a powerful primitive
- **Installed-modules status file.** `~/.claude/installed_modules.json` tracks what was installed, with install timestamps and per-operation results. Used for `--update` to detect which modules to re-install, and for `uninstall` to know what to remove. This is a durable state file separate from Claude Code's own settings, acting as the installer's source of truth
- **Split version spaces: marketplace/plugin.json vs package.json vs tags.** Three independent version numbers drift: marketplace.json (5.6.1), package.json (6.7.0), git tags (v6.8.2). Each is meaningful in its own context but they are not reconciled. The npx installer uses tag_name from the releases API at runtime, bypassing the checked-in version fields entirely
- **Auto-shell-config modification.** `install.sh` detects user shell and writes PATH append lines to shell rc files with idempotency checks — crossing the line from "install under `~/.claude`" to "modify user dotfiles". Most plugin-era patterns avoid this
- **Post-install detection report.** `printPostInstallInfo` in cli.js runs `which codex`, `which claude`, `which gemini`, `which opencode` and reports status with `✓`/`✗` markers, plus detects whether `~/.claude/bin` is in `$PATH`. This is user-friendly telemetry without being opt-out-only phone-home — worth the pattern catalog
- **Dual installer (legacy Python + current Node).** `install.py` (1,533 lines, uses `jsonschema` to validate config.json) and `install.sh` (legacy wrapper) coexist with `bin/cli.js` (1,285 lines, the new blessed path). The shell script prints a 5-second warning banner directing users to the npx path. Migration-in-progress is visible in the repo structure

## 18. Gaps

- `do` plugin exists in config.json and in the `skills/do/` directory (with its own `install.py`) but is not in `marketplace.json`. The install semantics of `do` vs the 5 marketplace plugins were not cross-checked in detail — specifically whether `do`'s install.py and the parent cli.js's `applyModule("do", ...)` diverge. Would need to read `skills/do/install.py` to resolve
- The `auto-add to shell config files with idempotency` block in `install.sh` was truncated in the sample fetch — exact shell-rc file list and idempotency mechanism not verified. Would need full `install.sh` fetch
- `inject-spec.py` and `log-prompt.py` contents not fetched — so whether they use `hookSpecificOutput.additionalContext`, rewrite bash commands, or merely log is unverified. File sizes are small (~500 bytes each) so the full read is cheap but skipped for call budget
- Whether `pre-bash.py` is actually a safety blocker or a no-op was not verified from source — the hooks.json entry suggests dangerous-command blocking but the 536-byte file might be a stub
- The `harness` module referenced in CHANGELOG and config.json excerpt was not drilled into — its operations may introduce additional patterns (the description mentions "multi-session autonomous agent harness with progress checkpointing, failure recovery, task dependencies") that weren't captured
- `dependencies` field on plugin.json files was not re-checked individually — all five sampled plugin.json files carried no `dependencies`, but sampling was exhaustive across the marketplace roster so confidence is high
- No attempt to run the installer or read `~/.claude/installed_modules.json` format from a live install — the state-file schema is inferred from `upsertModuleStatus` / `loadInstalledStatus` source, not verified against a real file
- Whether Smithery integration (badge present) implies a separate distribution path was not investigated — could be a third channel alongside marketplace.json and npx
