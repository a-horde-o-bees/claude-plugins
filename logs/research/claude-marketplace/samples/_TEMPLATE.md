# _TEMPLATE

Per-repo research file structure. Every field below must be filled in every repo file. "Not present" / "not applicable" with a one-line reason is valid — nothing silently defaults. Preset values are prompts, not menus: if reality doesn't fit, describe what's actually there in free-form. Every purpose section ends with any repo-specific pitfalls observed.

Filename convention: `<owner>--<repo>.md` (double-hyphen separator).

---

# <owner>/<repo>

## Identification

- **URL**:
- **Stars**:
- **Last commit date**:
- **Default branch**:
- **License**:
- **Sample origin**: primary / dep-management / bin-wrapper / (multiple — list all)
- **One-line purpose**: (what the marketplace / plugin does, from README opening)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root / multiple manifests / other: …
- **Marketplace-level metadata**: `metadata.{description, version, pluginRoot}` wrapper / top-level `description` / none / other: …
- **`metadata.pluginRoot`**: absent / present (value)
- **Per-plugin discoverability**: category / tags / keywords / category+tags / all three / none / other: … (per plugin if multi-plugin; note "all same" if uniform)
- **`$schema`**: absent / present (URL)
- **Reserved-name collision**: no / yes (which reserved name)
- **Pitfalls observed**: …

## 2. Plugin source binding

- **Source format(s) observed**: relative / github / url / git-subdir / npm / other: … (note mix if aggregator)
- **`strict` field**: default (implicit true) / `true` explicit / `false` / mixed across entries
- **`skills` override on marketplace entry**: absent / present (used for strict: false carving) / other: …
- **Version authority**: `plugin.json` only / marketplace entry only / both (drift risk) / neither / other: …
- **Pitfalls observed**: …

## 3. Channel distribution

- **Channel mechanism**: no split (users pin via `@ref`) / two separate marketplaces (stable+latest pattern) / other: …
- **Channel-pinning artifacts**: absent / `stable-tools` + `latest-tools` style / dev-counter + release-branch split / other: …
- **Pitfalls observed**: …

## 4. Version control and release cadence

- **Default branch name**: main / master / other: …
- **Tag placement**: on main / on `release/*` / on tagged commits only / none / other: …
- **Release branching**: none (tag-on-main) / `release/*` long-lived / `v*` legacy / other: …
- **Pre-release suffixes**: none observed / `-rc` / `-beta` / `-alpha` / other: …
- **Dev-counter scheme**: absent / present (e.g., `0.0.z` on main + real semver on release branches)
- **Pre-commit version bump**: no / yes (mechanism — hook type)
- **Pitfalls observed**: …

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery (no component fields) / explicit path arrays / external file reference (e.g., `mcpServers: "./.mcp.json"`) / inline config objects / mixed / other: …
- **Components observed**: skills / commands / agents / hooks / .mcp.json / .lsp.json / monitors / bin / output-styles — (mark each yes/no)
- **Agent frontmatter fields used**: (list if agents present — e.g., model, tools, skills, memory, background, isolation) / not applicable
- **Agent tools syntax**: permission-rule syntax (e.g., `Bash(uv run *)`) / plain tool names / other: … / not applicable
- **Pitfalls observed**: …

## 6. Dependency installation

- **Applicable**: yes / no (why not — e.g., pure skill content, no runtime deps)
- **Dep manifest format**: requirements.txt / pyproject.toml / package.json / Cargo.toml / go.mod / other: … / none
- **Install location**: `${CLAUDE_PLUGIN_DATA}` / `${CLAUDE_PLUGIN_ROOT}` / ad-hoc runtime fetch (npx/uvx) / mixed / other: …
- **Install script location**: (exact path relative to plugin root, or "inline in hooks.json")
- **Change detection**: `diff -q` / sha256 / md5 / version file stamp / existence only / mtime / other: … / none
- **Retry-next-session invariant**: `rm` on failure (docs-prescribed) / no `rm` / other: …
- **Failure signaling**: silent (exit code propagates) / stderr human-readable / `set -euo pipefail` halts / JSON `systemMessage` / `continue: false` + stopReason / exit 2 + stderr / other: …
- **Runtime variant**: Python uv / Python pip / Node npm / Node bun / Go binary download / Rust binary / mixed / WASM / other: …
- **Alternative approaches**: PEP 723 inline metadata (`uv run --script`) / pointer-file pattern / `npx`/`uvx` ad-hoc / other: … / none
- **Version-mismatch handling**: (e.g., Python minor version tracking, Node ABI tracking) / none
- **Pitfalls observed**: …

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes / no (why not)
- **`bin/` files**: (list with one-line purpose each)
- **Shebang convention**: `env bash` / `/bin/bash` / `env python3` / `env node` / `env bun` / `/bin/sh` / PEP 723 `env -S uv run --script` / mixed / other: …
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback / `${CLAUDE_PLUGIN_ROOT}` required / script-relative only / pointer file written by hook / user-PATH first then plugin-managed / standalone / other: …
- **Venv handling (Python)**: direct `exec venv python` / `source activate` then exec / pointer file read + exec / `uv run --script` ephemeral / pip-install at first run / no venv (system python3) / not applicable
- **Platform support**: nix-only / POSIX / bash + .cmd pair / bash + .ps1 pair / OS-detecting runtime / other: …
- **Permissions**: 100755 (executable) / 100644 (non-executable, invoked via `bash <path>`) / 120000 (symlink) / mixed / other: …
- **SessionStart relationship**: static (no hook relationship) / hook builds/populates bin/ / hook writes pointer file consumed by bin/ / hook lazily downloads binary / not applicable
- **Pitfalls observed**: …

## 8. User configuration

- **`userConfig` present**: yes / no
- **Field count**: (number, or "none")
- **`sensitive: true` usage**: correct (secrets flagged) / incorrect (description says "secret" but flag absent — anti-pattern) / mixed / not applicable
- **Schema richness**: minimal (description only) / typed (`type`, `default`, etc.) / not applicable
- **Reference in config substitution**: `${user_config.KEY}` observed in MCP/LSP/hook/monitor commands / `CLAUDE_PLUGIN_OPTION_<KEY>` env var usage / not applicable
- **Pitfalls observed**: …

## 9. Tool-use enforcement

- **PreToolUse hooks**: count + matcher(s) + purpose, or none
- **PostToolUse hooks**: count + matcher(s) + purpose, or none
- **PermissionRequest/PermissionDenied hooks**: observed / absent
- **Output convention**: stderr human + stdout JSON / stderr only / stdout JSON only / other: … / not applicable
- **Failure posture**: fail-open / fail-closed / mixed per-hook / documented conventions (e.g., centralized emit helpers) / not applicable
- **Top-level try/catch wrapping**: observed / absent / not applicable
- **Pitfalls observed**: …

## 10. Session context loading

- **SessionStart used for context**: yes / no / only for dep install (see purpose 6)
- **UserPromptSubmit for context**: yes / no
- **`hookSpecificOutput.additionalContext` observed**: yes / no / not applicable
- **SessionStart matcher**: none (fires on all sub-events) / `startup` only / `startup|clear|compact` / other: … / not applicable
- **Pitfalls observed**: …

## 11. Live monitoring and notifications

- **`monitors.json` present**: yes / no
- **Monitor count + purposes**: (list, or "none")
- **`when` values used**: `always` / `on-skill-invoke:<skill>` / mixed / not applicable
- **Version-floor declaration**: in README / plugin.json / absent / not applicable
- **Pitfalls observed**: …

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: yes / no
- **Entries**: (list — bare string vs object with version constraint vs cross-marketplace) / none
- **`{plugin-name}--v{version}` tag format observed**: yes / no / not applicable (not a multi-plugin marketplace)
- **Pitfalls observed**: …

## 13. Testing and CI

- **Test framework**: pytest / unittest / jest / vitest / node:test / go test / bash scripts / multiple / none / other: …
- **Tests location**: `tests/` at repo root / `tests/plugins/<name>/` nested / inside plugin directory / per-plugin `tests/` / not applicable
- **Pytest config location**: `[tool.pytest.ini_options]` in pyproject.toml / dedicated `pytest.ini` / `setup.cfg` / not applicable
- **Python dep manifest for tests**: pyproject.toml / requirements.txt / requirements-dev.txt / not applicable
- **CI present**: yes / no
- **CI file(s)**: (list — e.g., `ci.yml`, `test.yml`, `validate.yml`)
- **CI triggers**: `push` branches / `pull_request` / `schedule` / `tags: v*` / `workflow_dispatch` / other: … / not applicable
- **CI does**: pytest / linting (ruff/pyright/black) / custom validators / manifest validation / `npm test` / multiple / not applicable
- **Matrix**: none / Python versions / OS / Node versions / OS × Python / OS × Node / OS × Node × PM / other: …
- **Action pinning**: tag / SHA / mixed / not applicable
- **Caching**: built-in setup-X cache / `actions/cache` / none / not applicable
- **Test runner invocation**: direct `pytest` / `scripts/test.sh` wrapper / `uv run pytest` / `npm test` / other: …
- **Pitfalls observed**: …

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes / no
- **Release trigger**: `push: tags: ['v*']` / `release: [published]` / `workflow_dispatch` / multi-trigger / other: … / not applicable
- **Automation shape**: skill-zip build + draft release / tag-sanity + GitHub release / npm publish with `--provenance` / PyPI OIDC trusted publishing / Go/Rust binary build + attach / other: … / not applicable
- **Tag-sanity gates**: none / verify-tag-on-main / verify-tag=package-version / tag-format regex / all three / other: … / not applicable
- **Release creation mechanism**: `softprops/action-gh-release` / `gh release create` / `release-please` / `semantic-release` / other: … / not applicable
- **Draft releases**: yes / no / not applicable
- **CHANGELOG parsing**: yes (awk/script) / no (generate_release_notes only) / not applicable
- **Pitfalls observed**: …

## 15. Marketplace validation

- **Validation workflow present**: yes / no
- **Validator**: bun+zod / Python+json / node custom / `claude plugin validate` CLI / pre-commit hook / other: … / not applicable
- **Trigger**: `push` / `pull_request` / pre-commit / manual / not applicable
- **Frontmatter validation**: yes / no / not applicable
- **Hooks.json validation**: yes / no / not applicable
- **Pitfalls observed**: …

## 16. Documentation

- **`README.md` at repo root**: present (rough size) / absent
- **Owner profile README at `github.com/<owner>/<owner>`**: absent / present (~N lines, category — e.g. trivial / decorative / brief landing card / resume-tier portfolio / marketing collateral)
- **`README.md` per plugin**: present / absent / mixed
- **`CHANGELOG.md`**: absent / present (format — Keep a Changelog / custom / unclear)
- **`architecture.md`**: absent / at repo root / per plugin / both
- **`CLAUDE.md`**: absent / at repo root / per plugin / both
- **Community health files**: (list — `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`) / none
- **LICENSE**: present (SPDX identifier) / absent
- **Badges / status indicators**: observed / absent
- **Pitfalls observed**: …

## 17. Novel axes

Open bullets — any design choice observed in this repo that doesn't fit cleanly into purposes 1-16. Candidates for new purpose sections in the pattern doc. Examples: distinctive config surfaces, unusual permission handling, novel installation tricks, unique release-notes structures.

- …

## 18. Gaps

Open bullets — what couldn't be determined within the WebFetch / GitHub API budget + what source would resolve it.

- …
