# Vortiago/mcp-outline

## Identification

- **URL**: https://github.com/Vortiago/mcp-outline
- **Stars**: 140
- **Last commit date**: 2026-04-06 (HEAD commit; repo `pushed_at` 2026-04-20)
- **Default branch**: `main`
- **License**: MIT
- **Sample origin**: primary (community)
- **One-line purpose**: "A Model Context Protocol (MCP) server enabling AI assistants to interact with Outline documentation services" — single-plugin marketplace wrapping a pip-installable MCP server for the Outline knowledge-base product, distributed via PyPI + ghcr.io Docker + Claude plugin.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, alongside `.claude-plugin/plugin.json`. Repo doubles as both the MCP server source (`src/mcp_outline/`) and the Claude plugin.
- **Marketplace-level metadata**: top-level `name`, `owner.{name,url}`, and `metadata.description`. No marketplace-level `version` or `pluginRoot`.
- **`metadata.pluginRoot`**: absent — `source: "./"` on the single plugin entry points at the repo root directly.
- **Per-plugin discoverability**: neither `category`, `tags`, nor `keywords` on the marketplace entry itself; `plugin.json` carries `keywords: ["outline", "documents", "wiki", "knowledge-base", "mcp"]`. No category or tags anywhere.
- **`$schema`**: absent on both `marketplace.json` and `plugin.json`. (Present only on the sibling `server.json`, which is the MCP registry schema, not a Claude Code schema.)
- **Reserved-name collision**: no — `mcp-outline` is not a reserved plugin name.
- **Pitfalls observed**: marketplace entry duplicates fields from `plugin.json` (name, description, version, author, license) — the bump script rewrites version in both, but nothing else prevents the free-text fields from drifting.

## 2. Plugin source binding

- **Source format(s) observed**: `source: "./"` — relative self-reference, since the repo is simultaneously the marketplace and the plugin.
- **`strict` field**: not present on the marketplace entry (defaults to implicit `true`).
- **`skills` override on marketplace entry**: absent — no skills in this plugin at all, so no carving is needed.
- **Version authority**: intentionally dual-written. `scripts/bump_version.py` is the single source of truth that writes all four files atomically (`server.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.mcp.json`) with a regex for the pinned `uvx mcp-outline==<ver>` arg. Validates semver monotonicity before writing.
- **Pitfalls observed**: four places hold the version string. Drift is prevented by the bump script, not by structure — a manual edit to any one file leaves the other three behind. No check/CI validation that the four values agree (the bump script only runs at author-initiated bump time, not as a guard).

## 3. Channel distribution

- **Channel mechanism**: no channel split at the marketplace level. Users pin by `@ref` (tag or commit) when installing the plugin, or rely on the PyPI package's semver.
- **Channel-pinning artifacts**: absent — no stable/latest duplication of entries; single entry, single version field.
- **Pitfalls observed**: because `.mcp.json` pins `mcp-outline==<ver>` literally (not `latest`), installing the plugin at an old tag wires the client to the exact PyPI version from that commit. That's intentional — the plugin and the runtime wheel stay lockstep — but it means the plugin cannot float ahead of the wheel without a tag+rebuild.

## 4. Version control and release cadence

- **Default branch name**: `main`
- **Tag placement**: on `main` directly — tags `v0.3.0`-`v1.8.0` all land on merged-to-main commits. No release branches.
- **Release branching**: none (tag-on-main). Everything ships from `main`.
- **Pre-release suffixes**: none present in the 18 published tags, but the release pipeline explicitly handles `-rc` — the TestPyPI job gates on `contains(github.ref, '-rc')`, and `bump_version.py` accepts only bare `X.Y.Z` (no rc bumps), suggesting rc tags would be cut manually outside the bump script.
- **Dev-counter scheme**: absent. `pyproject.toml` uses `setuptools-scm` with `fallback_version = "0.0.0"` and `local_scheme = "no-local-version"`, so dev builds between tags get a synthetic `X.Y.Z.devN` from setuptools-scm but the four JSON files hold the last released semver.
- **Pre-commit version bump**: no. Pre-commit hooks run ruff, pyright, pytest, and basic hygiene hooks — no version-bump hook. Version bumps are manual via `uv run poe bump-version <ver>`.
- **Pitfalls observed**: 18 tags over ~13 months (v0.3.0 2025-03 → v1.8.0 2026-03), nearly all major numbered v1.x in a burst Nov 2025 through March 2026 — indicates active release cadence but no automation beyond the bump script.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` carries only `name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`. No `mcpServers`, `agents`, `skills`, or `hooks` fields. Claude Code auto-discovers `agents/` and `.mcp.json` at the plugin root by convention.
- **Components observed**:
  - skills — no
  - commands — no
  - agents — yes (`agents/outline-explorer.md`, a single haiku-model agent with inline prompt for read-only Outline exploration)
  - hooks — no
  - `.mcp.json` — yes (root-level, pins `uvx mcp-outline==1.8.0` with six env passthroughs)
  - `.lsp.json` — no
  - monitors — no
  - bin — no
  - output-styles — no
- **Agent frontmatter fields used**: `name`, `description` (with `<example>` blocks narrating when to invoke), `model: haiku`, `color: cyan`, `mcpServers: [mcp-outline]` — explicit allowlist binding the agent to the plugin's own MCP server.
- **Agent tools syntax**: no `tools:` list. The frontmatter uses `mcpServers:` to scope access and lets the agent discover the server's tools dynamically; the agent body lists expected tool-name suffixes in prose ("tools whose names end with `search_documents`, `read_document`, `list_collections`, etc.").
- **Pitfalls observed**: the agent prompt reminds the model to "USE THE TOOL-CALLING INTERFACE" and "NEVER simulate, write out, or fake function calls" — an inline guard against haiku hallucinating tool output instead of calling tools. Suggests empirical prompt-level failure mode the author hit and patched. Also: agent enforces read-only via prose only, not via tool filtering — `OUTLINE_READ_ONLY=true` at server level would be the structural enforcement, but the agent doesn't set it; relies on the model obeying.

## 6. Dependency installation

- **Applicable**: no (from the plugin's perspective). The Claude plugin ships no Python deps of its own — it delegates runtime to `uvx mcp-outline==1.8.0`, which is a PyPI wheel. Claude Code never sees Python requirements; `uvx` fetches the exact pinned wheel per-invocation into its own cache.
- **Dep manifest format**: not used for the plugin. For the underlying MCP server (which is what `uvx` actually installs): `pyproject.toml` + `uv.lock` (runtime deps: `mcp[cli]>=1.20.0`, `httpx>=0.27.0`, `python-dotenv>=1.0.0`; dev deps include `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `pyright`, `anyio`, `trio`, `poethepoet`, `pre-commit`).
- **Install location**: wherever `uvx` caches wheels on the user's system (default `~/.cache/uv/`). The plugin directory itself holds no installed deps.
- **Install script location**: not applicable — no SessionStart install hook.
- **Change detection**: not applicable at the plugin layer. At the runtime layer, `uvx` hash-locks via the exact `==1.8.0` pin.
- **Retry-next-session invariant**: not applicable — no plugin-owned install state to leave stale.
- **Failure signaling**: not applicable at the plugin layer. An unavailable `uvx` surfaces as a standard MCP server launch failure from Claude Code.
- **Runtime variant**: Python via `uvx` (the Astral ad-hoc runner). Alternatives available in README: `pip install mcp-outline`, and `docker run ghcr.io/vortiago/mcp-outline:latest` (multi-arch amd64+arm64 image). `.mcp.dev.json` swaps `uvx` for `uv run mcp-outline` against the in-repo source for developer workflows.
- **Alternative approaches**: `uvx`-based ad-hoc is the default distribution path; pip and Docker are user-facing alternatives documented in README.
- **Version-mismatch handling**: the pinned `==1.8.0` locks to an exact wheel; any Python 3.10-3.13 interpreter on the host is accepted (per `pyproject.toml` `requires-python = ">=3.10"` and CI's 4-version matrix). Wheel is pure-Python, so no ABI concerns.
- **Pitfalls observed**: the pin in `.mcp.json` is `mcp-outline==<exact>`. That's stricter than most `uvx` MCP setups that leave the version unpinned — this repo trades fresh-on-every-run for reproducibility and atomic version cuts. The cost is that old plugin tags will always install old wheels, even after security patches to the wheel are released.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. `start_server.sh` at repo root is a 10-line dev convenience for running the server inside WSL2 — not a plugin `bin/` entry, not on the MCP launch path.
- **`bin/` files**: none — no `bin/` directory at the plugin root.
- **Shebang convention**: `start_server.sh` uses `#!/bin/bash`; not applicable for plugin distribution.
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: `start_server.sh` sources `.venv/activate` if present, exports `.env`, and runs `python src/mcp_outline/server.py`. Dev-only; plugin users never see this.
- **Platform support**: not applicable.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable.
- **Pitfalls observed**: none — the repo cleanly separates "how dev runs the server" (start_server.sh + `.mcp.dev.json` + uv) from "how end users run it via the plugin" (`.mcp.json` + uvx + pinned PyPI wheel).

## 8. User configuration

- **`userConfig` present**: no — `plugin.json` has no `userConfig` block.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable (no `userConfig`). However, `server.json` (MCP registry) marks `OUTLINE_API_KEY` with `isSecret: true`, which is the MCP-registry-schema equivalent.
- **Schema richness**: not applicable for Claude Code `userConfig`.
- **Reference in config substitution**: env-var passthrough in `.mcp.json` via shell-style `${OUTLINE_API_KEY:-}` defaults (six vars: API key, URL, read-only, disable-delete, disable-AI-tools, verify-SSL). No `${user_config.KEY}` substitution and no `CLAUDE_PLUGIN_OPTION_*` usage.
- **Pitfalls observed**: the plugin punts configuration entirely to the user's shell environment — they must export `OUTLINE_API_KEY` before launching Claude Code, or use the VS Code/Cursor/MCP-inputs mechanism shown in README. No in-plugin prompt. This works for personal use but forces multi-user HTTP deployments to route through the `x-outline-api-key` HTTP header mechanism documented in the server's CLAUDE.md. For a plugin with a required secret, `userConfig` with `sensitive: true` would be the idiomatic Claude Code surface; the author chose not to use it.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable — no hooks.
- **Failure posture**: not applicable.
- **Top-level try/catch wrapping**: not applicable.
- **Pitfalls observed**: none — this plugin is pure MCP-server bridge; it doesn't try to police tool use at the Claude Code layer. The server itself enforces its own read-only/disable-delete/dynamic-tool-list policy at MCP registration time (before Claude ever sees the tools).

## 10. Session context loading

- **SessionStart used for context**: no — no `hooks.json`.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: no.
- **SessionStart matcher**: not applicable.
- **Pitfalls observed**: none — the plugin ships no context-injection behavior. Users get a fresh session and the MCP server's tool descriptions, nothing else.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace; tags use bare `v<ver>` (e.g., `v1.8.0`).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: pytest (with `pytest-asyncio`, `pytest-cov`, `anyio`, `trio`). Markers: `integration`, `e2e` — default `addopts` excludes both, so bare `pytest` runs unit tests only.
- **Tests location**: `tests/` at repo root — split into `tests/features/` (unit tests per feature module), `tests/e2e/` (Docker-compose-backed integration), `tests/utils/`, plus top-level server/health/stdio/dotenv/copilot-simulation tests.
- **Pytest config location**: `[tool.pytest.ini_options]` in `pyproject.toml`. Adjacent markdown sidecars (`test_*.md`) exist next to some test files — appear to be human-written per-test documentation, not machine-consumed.
- **Python dep manifest for tests**: `pyproject.toml` `[dependency-groups].dev` section (uv native dep groups).
- **CI present**: yes.
- **CI file(s)**: eight workflows.
  1. `ci.yml` — unit tests, lint, type-check (the primary quality gate)
  2. `e2e.yml` — Docker-compose E2E against a real Outline stack
  3. `publish-pypi.yml` — PyPI + TestPyPI + MCP registry publish on `v*` tag
  4. `release.yml` — GitHub Release creation on `v*` tag
  5. `docker-build.yml` — multi-arch (amd64+arm64) ghcr.io Docker image
  6. `codeql.yml` — CodeQL security analysis (python + actions languages, scheduled weekly + PR)
  7. `claude.yml` — Claude Code action wired up but `workflow_dispatch`-only (triggers commented out)
  8. `claude-code-review.yml` — Claude PR review action, also `workflow_dispatch`-only (disabled)
- **CI triggers**: `ci.yml` runs on `push: ["**"]` + `pull_request: [main]` — every branch gets CI. `e2e.yml` same plus `workflow_dispatch`. Tag-triggered workflows (publish-pypi, release, docker-build on `v*`) fire only on release tags. CodeQL adds `schedule: "25 14 * * 1"` weekly cron.
- **CI does**: ruff format check, ruff lint, pyright type-check (against `src/` only), pytest with junit XML + coverage, junit report posting via `mikepenz/action-junit-report`. E2E brings up a full Docker Compose stack (Outline + Dex OIDC, configurable ports via env) and runs the e2e-marked subset.
- **Matrix**: `ci.yml` matrices Python 3.10 × 3.11 × 3.12 × 3.13 (`fail-fast: false`); OS is ubuntu-latest only, no Windows/macOS. E2E pins Python 3.12 single-version.
- **Action pinning**: **SHA-pinned with version-tag comment** — every third-party action uses full 40-char SHA + `# v<tag>` comment (e.g., `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6`, `astral-sh/setup-uv@cec208311dfd045dd5311c1add060b2062131d57 # v8.0.0`). Dependabot weekly-updates the SHAs. A few workflows (codeql.yml, release.yml, claude.yml) still use `@v6`/`@v4` floating tags — inconsistency.
- **Caching**: `astral-sh/setup-uv` with `enable-cache: true` (uv's built-in GH-Actions cache backend); Docker uses `type=gha` buildx cache. No `actions/cache` directly.
- **Test runner invocation**: `uv run pytest tests/ -v -m "not e2e" --cov=src/mcp_outline --cov-report=term --junit-xml=test-results.xml` — direct uv-run invocation in CI; locally users drive via `uv run poe test-unit` / `test-integration` / `test-e2e` tasks defined in pyproject.toml (`poethepoet`).
- **Pitfalls observed**: the `addopts = "-m 'not e2e and not integration'"` combined with markers named `integration` and `e2e` means a bare `pytest` silently skips a category most users don't realize is there — the poe tasks hide this, but a developer who invokes pytest directly sees fewer tests than CI runs in the aggregate. Also: claude.yml + claude-code-review.yml shipped fully wired but intentionally disabled (triggers commented), suggesting the author sketched the Anthropic automation and then backed off — comment in each says "Disabled — uncomment triggers below to re-enable".

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes — in fact three tag-driven workflows fire concurrently on `push: tags: ['v*']`: `publish-pypi.yml` (PyPI + TestPyPI + MCP Registry), `release.yml` (GitHub Release), and `docker-build.yml` (ghcr.io multi-arch).
- **Release trigger**: `push: tags: ['v*']` for all three.
- **Automation shape**: this is the most sophisticated release pipeline in the sample. Full shape:
  - `publish-pypi.yml`:
    - Job 1 `build`: checkout with `fetch-depth: 0` + `fetch-tags: true` (so setuptools-scm can compute the dynamic version from the tag), installs `build`, runs `python -m build`, uploads `dist/` as artifact.
    - Job 2 `publish-to-pypi`: downloads artifact, uses `pypa/gh-action-pypi-publish` with `environment: {name: pypi, url: https://pypi.org/p/mcp-outline}` + `permissions: {id-token: write}` → **OIDC trusted publishing** (no PyPI API token in secrets). Requires the publisher to be configured PyPI-side for this exact repo + workflow file + environment.
    - Job 3 `publish-to-testpypi`: conditional `if: contains(github.ref, '-rc')` — rc-suffixed tags (`v1.2.0-rc1` etc.) go to TestPyPI instead/additionally; uses a separate `testpypi` environment and `repository-url: https://test.pypi.org/legacy/`.
    - Job 4 `publish-to-mcp-registry`: `needs: [publish-to-pypi]`, downloads the mcp-publisher CLI binary from the modelcontextprotocol/registry release, rewrites `server.json` in-place with `jq --arg v "$VERSION" '.version = $v | .packages[0].version = $v'`, authenticates via `./mcp-publisher login github-oidc`, publishes. GitHub OIDC authenticates the repo to the MCP registry — no stored credentials.
  - `release.yml`: single-job, uses raw `gh release create` (not a marketplace action) with `--generate-notes --notes-start-tag $(git describe --tags --abbrev=0 ${{ github.ref_name }}^)` — auto-computes previous tag for range. Appends a literal Markdown body with PyPI + Docker install snippets.
  - `docker-build.yml`: `docker/setup-qemu-action` + `docker/setup-buildx-action` + `docker/metadata-action` computes the full tag set (`{{version}}`, `{{major}}.{{minor}}`, `{{major}}`, `latest` on default branch, branch name, PR number, short SHA) via `type=semver` + `type=raw` + `type=ref` + `type=sha` patterns. Build-push-action builds amd64 first, runs a smoke-test container (`curl /health` with 30 s retry loop), then builds+validates multi-arch amd64+arm64. Only pushes on `refs/tags/v*`. Uses `type=gha` cache.
- **Tag-sanity gates**: the `publish-pypi.yml` has **no** tag-sanity validation — no check that the tag's commit is on main, no check that `server.json`/`plugin.json` version matches the tag. setuptools-scm derives the wheel's version from the tag itself (`v1.8.0` → `1.8.0`), and the MCP-registry job rewrites `server.json` at publish time (`.version = $v`). So tag-form enforcement is implicit: whatever `${GITHUB_REF_NAME#v}` produces is what ships, and a malformed tag would surface as a PyPI-rejected version. The `bump_version.py` script enforces semver-bump validity locally at author time but isn't re-run in CI.
- **Release creation mechanism**: raw `gh release create` in release.yml (not `softprops/action-gh-release`). `--generate-notes` uses GitHub's auto-generated changelog between `--notes-start-tag` and the new tag.
- **Draft releases**: no — published immediately.
- **CHANGELOG parsing**: no — no `CHANGELOG.md` in the repo, and the release workflow relies on `gh release create --generate-notes` + a hard-coded markdown install stanza. Release notes are commit-based.
- **Pitfalls observed**: the pipeline is tag-form-fragile — a tag like `v1.8.0-rc1` triggers all three workflows (publish-pypi, release, docker-build) and relies on the `-rc` filter in publish-pypi's TestPyPI job being correct. But `release.yml` and `docker-build.yml` have no rc filter, so a pre-release tag also cuts a GitHub Release and pushes a ghcr.io image tagged `1.8.0-rc1` + `latest` (on default branch) alongside. That's almost certainly unintended for pre-releases — the Docker tag `latest` would leak an rc build. No gate prevents this. Also: the MCP-registry job rewrites `server.json` in the ephemeral checkout but never commits it back — source-of-truth stays on the previously-committed value (which the local bump script kept in sync) and the registry gets the tag-derived value; if those disagree, the registry silently wins for that publish.

## 15. Marketplace validation

- **Validation workflow present**: no — no CI step validates `.claude-plugin/marketplace.json` or `.claude-plugin/plugin.json`. The only "validation" is the `bump_version.py` semver-bump check invoked manually.
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: no — agent frontmatter in `agents/outline-explorer.md` is untested.
- **Hooks.json validation**: not applicable (no hooks).
- **Pitfalls observed**: the marketplace/plugin JSON files have no schema guard. CI runs ruff + pyright + pytest but no `jsonschema` check against the Claude Code plugin schema. A typo in `marketplace.json` would only surface when a user tried to add the marketplace in Claude Code.

## 16. Documentation

- **`README.md` at repo root**: present (~12 KB, ~240 lines) — comprehensive: features, prereqs, one-click-install buttons for VS Code/Cursor, manual install, per-client config snippets, configuration table with 16 env vars, access-control section, tool catalog organized into nine categories, resources, development quick-start, troubleshooting.
- **Owner profile README at `github.com/Vortiago/Vortiago`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: same file serves both roles (single-plugin repo).
- **`CHANGELOG.md`**: absent. Release notes live only in GitHub Releases (auto-generated from commits by `gh release create --generate-notes`).
- **`architecture.md`**: absent at repo root. `CLAUDE.md` embeds an informal architecture section ("Tool Categories", "Feature Registration Flow", "MCP Resources", "Health Check Endpoints") but it's operational-doc shape.
- **`CLAUDE.md`**: at repo root (~17 KB) — comprehensive developer/agent guide: purpose, architecture, tool-registration pattern, client/connection-pool/rate-limit internals, module-structure template, error-handling patterns, test conventions, env-var catalog, pre-commit + CI verification recipes, and a full release-workflow runbook (`uv run poe bump-version` → commit → PR → merge → tag → push).
- **Community health files**: `CONTRIBUTING.md` present (~1 KB). No `SECURITY.md`, no `CODE_OF_CONDUCT.md`. `.github/PULL_REQUEST_TEMPLATE.md` present. `.github/ISSUE_TEMPLATE/` directory present (contents not enumerated). `.github/dependabot.yml` present — weekly updates for `pip` (grouped minor+patch) and `github-actions`.
- **LICENSE**: present, MIT (SPDX: `MIT`, 1065 bytes).
- **Badges / status indicators**: PyPI, Python 3.10+, MIT, CI workflow, Docker — five shields in README.
- **Pitfalls observed**: `CLAUDE.md` conflates architectural reference with operational procedure — includes a registration-flow diagram, client internals, and test conventions in the same file as "before committing run these commands". For the scope of this plugin (single-person project, moderate size) it's pragmatic; for the project-doc-separation discipline a larger team would enforce, it mixes concerns.

## 17. Novel axes

- **Triple-target publish on a single tag push**: `publish-pypi.yml` runs four jobs — build → PyPI → TestPyPI-if-rc → MCP Registry — chained via `needs:`, using two separate OIDC trusted-publishing surfaces (PyPI and the MCP Registry) and a tag-derived `server.json` rewrite in the ephemeral checkout. No token secrets stored anywhere. This is the release-automation ceiling observed in the sample: end-to-end signed publishing across three independent registries from a single tag, plus a fourth channel (ghcr.io multi-arch Docker) fired by a parallel workflow on the same trigger.
- **TestPyPI pre-release branch via ref-contains filter**: the `-rc` suffix routes builds to TestPyPI instead of clobbering PyPI. This is a minimal but effective pre-release channel — no release-branch infra, just a string match on `github.ref`.
- **Docker image tag-ladder via `docker/metadata-action`**: the metadata-action computes a six-form tag set automatically (`{{version}}`, `{{major}}.{{minor}}`, `{{major}}`, `latest`, branch, short-SHA) for every image build. Pushes only on tag refs, but the validation build runs on every PR. Includes a live smoke-test (`docker run` + `curl /health` retry loop) between the amd64 single-arch validate and the multi-arch final build.
- **Companion MCP-registry manifest (`server.json`) alongside `plugin.json`**: the repo publishes the same server to two registries with two different manifest formats — `.claude-plugin/plugin.json` for Claude Code plugins and `server.json` (the modelcontextprotocol/registry schema, complete with `isSecret`, `isRequired`, `registryType: "pypi"`) for the MCP registry. The bump script keeps both in lockstep with `.claude-plugin/marketplace.json` and `.mcp.json` — four files, one atomic script.
- **Glama manifest `glama.json`**: three-line maintainer declaration for glama.ai's MCP server directory. Indicates the plugin targets at least three discovery surfaces: Claude Code marketplaces, the official MCP registry, and glama.ai.
- **Dual `.mcp.json` / `.mcp.dev.json`**: the production `.mcp.json` pins `uvx mcp-outline==<ver>` for end users; `.mcp.dev.json` swaps to `uv run mcp-outline` against the in-repo source plus an extra env var (`OUTLINE_DYNAMIC_TOOL_LIST`). Neither is wired into the plugin config as the authoritative source; developers select which to use in their Claude Code install manually.
- **Version-bump-script as single source of truth across four files**: `scripts/bump_version.py` atomically rewrites `server.json` (two version fields), `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and a regex substitution on the pinned `==<ver>` in `.mcp.json`. Validates that the new version is a legal semver bump (patch/minor/major, not arbitrary) from the current `server.json` before writing. This is the in-repo answer to the "version scattered across N files" problem — not a pre-commit hook, but a `poe` task the author runs by hand.
- **Pre-commit runs pytest**: the `.pre-commit-config.yaml` invokes `uv run pytest tests/ -v` as a local hook (`pass_filenames: false`, `types: [python]`). Most projects pre-commit ruff+format only — including pytest at commit time forces every commit to pass the unit suite, which is costlier but catches breakage at the lowest friction point.
- **CodeQL with `security-extended` queries + `actions` language**: `codeql.yml` scans not just the Python source but the workflow files themselves (`language: actions`), using the extended query set. Scheduled weekly (`25 14 * * 1`) plus on main push/PR.
- **Dependabot with grouped minor+patch**: `dependabot.yml` groups all non-major Python updates into a single weekly PR labeled `minor-and-patch` — reduces PR churn when multiple deps tick in the same week.
- **Intentionally-disabled Claude Code workflows**: both `claude.yml` and `claude-code-review.yml` are wired up with full credentials and prompts but have triggers commented out and only `workflow_dispatch: {}` enabled. The comments explicitly state "Disabled — uncomment triggers below to re-enable" — deliberate opt-in staging of Anthropic automation, easy to flip on later without re-authoring.
- **Agent frontmatter with `mcpServers:` allowlist binding an agent to the plugin's own MCP server**: the `outline-explorer` agent's frontmatter contains `mcpServers: [mcp-outline]` — a plugin-internal reference that both names the plugin's exported MCP server and restricts the agent to it. The agent uses `model: haiku` and `color: cyan` (cosmetic), and its prompt body includes a defensive "USE THE TOOL-CALLING INTERFACE" directive guarding against haiku-model hallucination of fake tool calls.
- **Agent body defines thoroughness levels as a caller-supplied parameter**: the agent prompt declares three modes (quick / medium / very thorough) that the caller names when invoking the agent, which the agent uses to decide how many searches and reads to perform. An interface contract documented in the prompt body, not in frontmatter.

## 18. Gaps

- `agents/` directory holds only one file in this commit but additional agent specs could have been added in later commits not inspected — verified by `ls` at HEAD only. Source that would resolve: enumerating `git log -- agents/` for the full history of additions.
- Whether the MCP-registry publish step (`./mcp-publisher publish`) has ever rejected a publish due to `server.json` schema drift isn't visible from workflow files alone — would need the Actions run history. Resolves via `gh api repos/Vortiago/mcp-outline/actions/workflows/publish-pypi.yml/runs` with conclusion filters.
- The `.github/ISSUE_TEMPLATE/` directory contents weren't enumerated (budget). Would resolve via one more `gh api` call but doesn't affect any of the 16 purposes.
- Whether any of the 18 tags are pre-release (`-rc`) tags isn't confirmed from the tag-name sample — all 18 listed are bare `vX.Y.Z`. No `-rc` tags have been cut; the TestPyPI pathway exists but hasn't been exercised in the released-tag sample.
- The `conftest.py` (12 KB) and integration-test layout in `tests/features/` and `tests/e2e/` weren't read. What the test framework actually asserts versus what the ecosystem claims (e.g., how `MockMCP` in unit tests relates to the Docker-backed `mcp_session` fixture in e2e) would need those files. Doesn't affect the purpose 13 summary above (framework, location, config, CI integration are all determinable from the surface).
- Whether the `bump_version.py` script is invoked by any pre-commit or CI guard (beyond manual `poe bump-version` invocation) was ruled out by reading `.pre-commit-config.yaml` and all eight workflows — confirmed manual only.
