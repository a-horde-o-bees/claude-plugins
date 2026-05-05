# Sample

Mirrors of `https://github.com/Vortiago/cmcp-outline`. Single-plugin marketplace wrapping `mcp-outline`, a pip-installable MCP server bridging Claude Code to the Outline knowledge-base product. Distributed via PyPI + ghcr.io Docker + Claude plugin. MIT-licensed, default branch `main`, 140 stars, last commit 2026-04-06; sample origin: primary (community).

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root, alongside `.claude-plugin/plugin.json`. Repo doubles as both the MCP server source (`src/mcp_outline/`) and the Claude plugin. The marketplace entry duplicates fields from `plugin.json` (name, description, version, author, license) — the bump script rewrites version in both, but nothing else prevents the free-text fields from drifting.

### Top-level `metadata` wrapper variants

Top-level `name`, `owner.{name,url}`, and `metadata.description`. No marketplace-level `version` or `pluginRoot`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`source: "./"` — relative self-reference, since the repo is simultaneously the marketplace and the plugin.

### `strict` field default

`strict` is not present on the marketplace entry (defaults to implicit `true`). No `skills` override on the marketplace entry — no skills in this plugin at all, so no carving is needed.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry carries no `category`, `tags`, or `keywords`; `plugin.json` carries `keywords: ["outline", "documents", "wiki", "knowledge-base", "mcp"]`. No category or tags anywhere. `mcp-outline` is not a reserved plugin name.

### `$schema` absence on per-plugin manifests

`$schema` is absent on both `marketplace.json` and `plugin.json`. Present only on the sibling `server.json`, which is the MCP-registry schema, not a Claude Code schema.

## Version coordination

### Multi-site sprawl (5+ locations)

Four files hold the version string and must stay in lockstep: `server.json` (two version fields — top-level and `packages[0].version`), `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, plus a regex-pinned `uvx mcp-outline==<ver>` literal in `.mcp.json`'s args array. `scripts/bump_version.py` is the single source of truth that writes all four atomically and validates semver-bump legality (patch/minor/major) before writing. Drift is prevented by the bump script, not by structure — a manual edit to any one file leaves the other three behind. No CI validation that the four values agree (the bump script only runs at author-initiated bump time, not as a guard). `pyproject.toml` uses `setuptools-scm` with `fallback_version = "0.0.0"` and `local_scheme = "no-local-version"`, so dev builds between tags get a synthetic `X.Y.Z.devN` from setuptools-scm but the four JSON files hold the last released semver.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split at the marketplace level. Users pin by `@ref` (tag or commit) when installing the plugin, or rely on the PyPI package's semver. `.mcp.json` pins `mcp-outline==<exact-ver>` literally (not `latest`) — installing the plugin at an old tag wires the client to the exact PyPI version from that commit. Intentional reproducibility (plugin and runtime wheel stay lockstep), but the plugin cannot float ahead of the wheel without a tag+rebuild.

### Pre-release tag suffixes on a single channel

The release pipeline explicitly handles `-rc` — the TestPyPI publish job gates on `contains(github.ref, '-rc')`, while `release.yml` (GitHub Release) and `docker-build.yml` (ghcr.io) have no rc filter. An `-rc` tag therefore goes to TestPyPI for PyPI publishing, but ALSO cuts a real GitHub Release and pushes a ghcr.io image including the `latest` tag (on default branch). The partial filter is almost certainly an unintended exposure for prereleases. `bump_version.py` accepts only bare `X.Y.Z` (no rc bumps), so rc tags are cut manually outside the bump script. None of the 18 published tags are rc-suffixed; the TestPyPI pathway exists but hasn't been exercised in the released-tag sample.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Tags `v0.3.0`-`v1.8.0` (18 tags) all land on merged-to-main commits. No release branches; everything ships from `main`. 18 tags over ~13 months (v0.3.0 2025-03 → v1.8.0 2026-03), nearly all major numbered v1.x in a burst Nov 2025 through March 2026 — active release cadence but no automation beyond the bump script. Pre-commit hooks run ruff, pyright, pytest, and basic hygiene hooks — no version-bump hook. Version bumps are manual via `uv run poe bump-version <ver>`.

## Plugin-component registration

### Default convention discovery

`plugin.json` carries only `name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`. No `mcpServers`, `agents`, `skills`, or `hooks` fields. Claude Code auto-discovers `agents/` and `.mcp.json` at the plugin root by convention.

### `.mcp.json` sibling file

Root-level `.mcp.json` pins `uvx mcp-outline==1.8.0` with six env passthroughs. A sibling `.mcp.dev.json` swaps `uvx` for `uv run mcp-outline` against the in-repo source plus an extra env var (`OUTLINE_DYNAMIC_TOOL_LIST`). Neither is wired into the plugin config as the authoritative source; developers select which to use in their Claude Code install manually.

## Component composition

### Agents

One agent: `agents/outline-explorer.md`, a single haiku-model agent with inline prompt for read-only Outline exploration.

### MCP servers

One stdio MCP server `mcp-outline` declared in `.mcp.json`, launched via `uvx mcp-outline==<exact-ver>`.

## Agent declaration conventions

### Standard fields plus model / color

Agent frontmatter uses `name`, `description` (with `<example>` blocks narrating when to invoke), `model: haiku`, `color: cyan`.

### MCP-server allowlist binding

Agent frontmatter declares `mcpServers: [mcp-outline]` — explicit allowlist binding the agent to the plugin's own MCP server. No `tools:` list; the frontmatter uses `mcpServers:` to scope access and lets the agent discover the server's tools dynamically. The agent body lists expected tool-name suffixes in prose ("tools whose names end with `search_documents`, `read_document`, `list_collections`, etc.").

### Defensive prompt directives in agent body

The agent prompt reminds the model to "USE THE TOOL-CALLING INTERFACE" and "NEVER simulate, write out, or fake function calls" — an inline guard against haiku hallucinating tool output instead of calling tools. Agent body also defines three thoroughness levels (quick / medium / very thorough) as a caller-supplied parameter the agent uses to decide how many searches and reads to perform — an interface contract documented in the prompt body, not in frontmatter.

## Server runtime (MCP)

### Pinned PyPI wheel via `uvx`

`.mcp.json` declares `uvx mcp-outline==1.8.0` as the launch command. `uvx` (Astral's ad-hoc runner) fetches the exact pinned wheel into its cache (`~/.cache/uv/` by default) per invocation. The plugin directory itself holds no installed deps. Any Python 3.10-3.13 interpreter on the host is accepted (per `pyproject.toml` `requires-python = ">=3.10"` and CI's 4-version matrix). Wheel is pure-Python, so no ABI concerns. Old plugin tags will always install old wheels even after security patches to the wheel are released. Alternatives documented in README: `pip install mcp-outline`, and `docker run ghcr.io/vortiago/mcp-outline:latest` (multi-arch amd64+arm64 image).

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory at the plugin root. `start_server.sh` at repo root is a 10-line dev convenience for running the server inside WSL2 — not a plugin `bin/` entry, not on the MCP launch path. Sources `.venv/activate` if present, exports `.env`, and runs `python src/mcp_outline/server.py`. Dev-only; plugin users never see this. The repo cleanly separates "how dev runs the server" (start_server.sh + `.mcp.dev.json` + uv) from "how end users run it via the plugin" (`.mcp.json` + uvx + pinned PyPI wheel).

## Dependency installation

### Delegated to PyPI runner (`uvx`)

The Claude plugin ships no Python deps of its own — it delegates runtime to `uvx mcp-outline==1.8.0`. Claude Code never sees Python requirements; `uvx` fetches the exact pinned wheel per-invocation into its own cache. No SessionStart install hook. The pin `mcp-outline==<exact>` in `.mcp.json` is stricter than most `uvx` MCP setups that leave the version unpinned — this repo trades fresh-on-every-run for reproducibility and atomic version cuts. For the underlying MCP server (which is what `uvx` actually installs): `pyproject.toml` + `uv.lock` declare runtime deps (`mcp[cli]>=1.20.0`, `httpx>=0.27.0`, `python-dotenv>=1.0.0`); dev deps include `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `pyright`, `anyio`, `trio`, `poethepoet`, `pre-commit`. Failure mode for unavailable `uvx` is a standard MCP server launch failure from Claude Code.

## User configuration and authentication

### No userConfig, env-var only

`plugin.json` has no `userConfig` block. Configuration is via env-var passthrough in `.mcp.json` using shell-style `${OUTLINE_API_KEY:-}` defaults — six vars: API key, URL, read-only, disable-delete, disable-AI-tools, verify-SSL. No `${user_config.KEY}` substitution and no `CLAUDE_PLUGIN_OPTION_*` usage. The plugin punts configuration entirely to the user's shell environment — they must export `OUTLINE_API_KEY` before launching Claude Code, or use the VS Code/Cursor/MCP-inputs mechanism shown in README. Multi-user HTTP deployments are routed through the `x-outline-api-key` HTTP header mechanism documented in the server's CLAUDE.md.

### MCP-registry-schema sidecar

`server.json` (modelcontextprotocol/registry schema) marks `OUTLINE_API_KEY` with `isSecret: true` — the MCP-registry equivalent of `sensitive: true`. The `plugin.json` has no `userConfig`. Two registries each demand their own config-schema dialect; the author honors the MCP one but not the Claude Code one.

## Tool-use enforcement

### No enforcement (observational only)

No `hooks.json` and no PreToolUse/PostToolUse/PermissionRequest hooks. This plugin is a pure MCP-server bridge; it doesn't try to police tool use at the Claude Code layer. The server itself enforces its own read-only/disable-delete/dynamic-tool-list policy at MCP registration time (before Claude ever sees the tools), via the `OUTLINE_READ_ONLY`, `OUTLINE_DISABLE_DELETE`, `OUTLINE_DISABLE_AI_TOOLS`, `OUTLINE_VERIFY_SSL` env vars in `.mcp.json`. The agent enforces read-only via prose only, not via tool filtering — `OUTLINE_READ_ONLY=true` at server level would be the structural enforcement, but the agent doesn't set it; relies on the model obeying.

## Session context loading

### No session-context loading

No `hooks.json`. SessionStart is not used for context, UserPromptSubmit is not used, and `hookSpecificOutput.additionalContext` is not emitted. Users get a fresh session and the MCP server's tool descriptions, nothing else.

## Live monitoring

### `monitors.json` absent

No `monitors.json`, no `when` values, no version-floor declaration.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field in `plugin.json`. Single-plugin marketplace; tags use bare `v<ver>` (e.g., `v1.8.0`).

## Testing

### Centralized `tests/` placement

`tests/` at repo root — split into `tests/features/` (unit tests per feature module), `tests/e2e/` (Docker-compose-backed integration), `tests/utils/`, plus top-level server/health/stdio/dotenv/copilot-simulation tests.

### Pytest with asyncio support

Test framework: pytest with `pytest-asyncio`, `pytest-cov`, `anyio`, `trio`. Markers: `integration`, `e2e` — default `addopts = "-m 'not e2e and not integration'"` excludes both, so bare `pytest` runs unit tests only. The marker filter combined with the addopts means a bare `pytest` silently skips a category most users don't realize is there — the `poe` tasks hide this, but a developer who invokes pytest directly sees fewer tests than CI runs in the aggregate. `[tool.pytest.ini_options]` lives in `pyproject.toml`. Adjacent markdown sidecars (`test_*.md`) exist next to some test files — appear to be human-written per-test documentation, not machine-consumed. Python dep manifest for tests uses `pyproject.toml` `[dependency-groups].dev` section (uv native dep groups). Test runner invocation in CI is `uv run pytest tests/ -v -m "not e2e" --cov=src/mcp_outline --cov-report=term --junit-xml=test-results.xml`; locally users drive via `uv run poe test-unit` / `test-integration` / `test-e2e` tasks defined in pyproject.toml (`poethepoet`).

## CI workflow shape

### Multi-workflow with version matrix and SHA-pinned actions

Eight workflows: `ci.yml` (unit tests, lint, type-check), `e2e.yml` (Docker-compose E2E against a real Outline stack), `publish-pypi.yml` (PyPI + TestPyPI + MCP registry publish on `v*` tag), `release.yml` (GitHub Release creation on `v*` tag), `docker-build.yml` (multi-arch amd64+arm64 ghcr.io Docker image), `codeql.yml` (CodeQL security analysis, python + actions languages, scheduled weekly + PR), `claude.yml` (Claude Code action wired up but `workflow_dispatch`-only with triggers commented out), and `claude-code-review.yml` (Claude PR review action, also `workflow_dispatch`-only and disabled). `ci.yml` runs ruff format check, ruff lint, pyright type-check (against `src/` only), pytest with junit XML + coverage, junit report posting via `mikepenz/action-junit-report`. `ci.yml` matrices Python 3.10 × 3.11 × 3.12 × 3.13 (`fail-fast: false`); ubuntu-latest only, no Windows/macOS. E2E pins Python 3.12 single-version and brings up a full Docker Compose stack (Outline + Dex OIDC, configurable ports via env). `ci.yml` runs on `push: ["**"]` + `pull_request: [main]` — every branch gets CI. E2E adds `workflow_dispatch`. Tag-triggered workflows (publish-pypi, release, docker-build on `v*`) fire only on release tags. CodeQL adds `schedule: "25 14 * * 1"` weekly cron. The `claude.yml` and `claude-code-review.yml` ship fully wired with credentials but triggers commented out and only `workflow_dispatch: {}` enabled — comments explicitly state "Disabled — uncomment triggers below to re-enable", deliberate opt-in staging of Anthropic automation, easy to flip on later without re-authoring.

### Action-pinning conventions

SHA-pinned with version-tag comment — every third-party action uses full 40-char SHA + `# v<tag>` comment (e.g., `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6`, `astral-sh/setup-uv@cec208311dfd045dd5311c1add060b2062131d57 # v8.0.0`). Dependabot weekly-updates the SHAs. A few workflows (codeql.yml, release.yml, claude.yml) still use `@v6`/`@v4` floating tags — inconsistency within the repo. Caching: `astral-sh/setup-uv` with `enable-cache: true` (uv's built-in GH-Actions cache backend); Docker uses `type=gha` buildx cache. No `actions/cache` directly.

## Pre-commit and pre-push hooks (git)

### Multi-tool pre-commit including pytest

`.pre-commit-config.yaml` runs ruff format check, ruff lint, pyright type-check, pytest (`uv run pytest tests/ -v` as a local hook with `pass_filenames: false`, `types: [python]`), plus basic hygiene hooks. Including pytest at commit time forces every commit to pass the unit suite — costlier per commit but catches breakage at the lowest-friction point.

## Ecosystem health automation

### Dependabot + CodeQL + grouped updates

`.github/dependabot.yml` weekly updates for `pip` (grouped minor+patch into a single PR labeled `minor-and-patch`) and `github-actions` (SHA bumps for the SHA-pinned action references). CodeQL with `security-extended` queries scans not just the Python source but the workflow files themselves (`language: actions`), scheduled weekly (`25 14 * * 1`) plus on main push/PR.

## Marketplace validation

### No validation

No CI step validates `.claude-plugin/marketplace.json` or `.claude-plugin/plugin.json`. The only "validation" is the `bump_version.py` semver-bump check invoked manually. CI runs ruff + pyright + pytest but no `jsonschema` check against the Claude Code plugin schema. A typo in `marketplace.json` would only surface when a user tried to add the marketplace in Claude Code. Agent frontmatter in `agents/outline-explorer.md` is untested. No hooks to validate (no `hooks.json`).

## Release automation

### Tag-triggered release with multi-gate sanity (npm)

This is a tag-driven multi-target publish pipeline — three workflows fire concurrently on `push: tags: ['v*']`: `publish-pypi.yml` (PyPI + TestPyPI + MCP Registry), `release.yml` (GitHub Release), and `docker-build.yml` (ghcr.io multi-arch). Full shape:

`publish-pypi.yml`:

- Job `build`: checkout with `fetch-depth: 0` + `fetch-tags: true` (so setuptools-scm can compute the dynamic version from the tag), installs `build`, runs `python -m build`, uploads `dist/` as artifact.
- Job `publish-to-pypi`: downloads artifact, uses `pypa/gh-action-pypi-publish` with `environment: {name: pypi, url: https://pypi.org/p/mcp-outline}` + `permissions: {id-token: write}` — OIDC trusted publishing, no PyPI API token in secrets. Requires the publisher to be configured PyPI-side for this exact repo + workflow file + environment.
- Job `publish-to-testpypi`: conditional `if: contains(github.ref, '-rc')` — rc-suffixed tags (`v1.2.0-rc1` etc.) go to TestPyPI; uses a separate `testpypi` environment and `repository-url: https://test.pypi.org/legacy/`.
- Job `publish-to-mcp-registry`: `needs: [publish-to-pypi]`, downloads the mcp-publisher CLI binary from the modelcontextprotocol/registry release, rewrites `server.json` in-place with `jq --arg v "$VERSION" '.version = $v | .packages[0].version = $v'`, authenticates via `./mcp-publisher login github-oidc`, publishes. GitHub OIDC authenticates the repo to the MCP registry — no stored credentials. The registry job rewrites `server.json` in the ephemeral checkout but never commits it back — source-of-truth stays on the previously-committed value (which the local bump script kept in sync) and the registry gets the tag-derived value; if those disagree, the registry silently wins for that publish.

`release.yml`: single-job, uses raw `gh release create` (not a marketplace action) with `--generate-notes --notes-start-tag $(git describe --tags --abbrev=0 ${{ github.ref_name }}^)` — auto-computes previous tag for range. Appends a literal Markdown body with PyPI + Docker install snippets. No CHANGELOG.md in repo; release notes are commit-based via `--generate-notes`. Releases are published immediately (not draft).

`docker-build.yml`: `docker/setup-qemu-action` + `docker/setup-buildx-action` + `docker/metadata-action` computes the full tag set (`{{version}}`, `{{major}}.{{minor}}`, `{{major}}`, `latest` on default branch, branch name, PR number, short SHA) via `type=semver` + `type=raw` + `type=ref` + `type=sha` patterns. Build-push-action builds amd64 first, runs a smoke-test container (`curl /health` with 30 s retry loop), then builds+validates multi-arch amd64+arm64. Only pushes on `refs/tags/v*`. Uses `type=gha` cache.

`publish-pypi.yml` has no tag-sanity validation — no check that the tag's commit is on main, no check that `server.json`/`plugin.json` version matches the tag. setuptools-scm derives the wheel's version from the tag itself (`v1.8.0` → `1.8.0`), and the MCP-registry job rewrites `server.json` at publish time (`.version = $v`). Tag-form enforcement is implicit: whatever `${GITHUB_REF_NAME#v}` produces is what ships, and a malformed tag would surface as a PyPI-rejected version. The `bump_version.py` script enforces semver-bump validity locally at author time but isn't re-run in CI. The pipeline is tag-form-fragile — a tag like `v1.8.0-rc1` triggers all three workflows and relies on the `-rc` filter in publish-pypi's TestPyPI job being correct, but `release.yml` and `docker-build.yml` have no rc filter, so a pre-release tag also cuts a GitHub Release and pushes a ghcr.io image tagged with `latest` (on default branch).

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

`README.md` at repo root (~12 KB, ~240 lines) is comprehensive: features, prereqs, one-click-install buttons for VS Code/Cursor, manual install, per-client config snippets, configuration table with 16 env vars, access-control section, tool catalog organized into nine categories, resources, development quick-start, troubleshooting. Same file serves both repo-level and plugin-level roles (single-plugin repo). `CLAUDE.md` at repo root (~17 KB) is a comprehensive developer/agent guide: purpose, architecture, tool-registration pattern, client/connection-pool/rate-limit internals, module-structure template, error-handling patterns, test conventions, env-var catalog, pre-commit + CI verification recipes, and a full release-workflow runbook (`uv run poe bump-version` → commit → PR → merge → tag → push). `CLAUDE.md` conflates architectural reference with operational procedure — includes a registration-flow diagram, client internals, and test conventions in the same file as "before committing run these commands". For the scope of this plugin (single-person project, moderate size) it's pragmatic; for the project-doc-separation discipline a larger team would enforce, it mixes concerns. `CHANGELOG.md` is absent — release notes live only in GitHub Releases (auto-generated from commits). `architecture.md` is absent at repo root; `CLAUDE.md` embeds an informal architecture section ("Tool Categories", "Feature Registration Flow", "MCP Resources", "Health Check Endpoints") but it's operational-doc shape.

### Badges and status indicators

Five Shields.io badges in README: PyPI, Python 3.10+, MIT, CI workflow, Docker.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

Full LICENSE file at repo root (MIT, 1065 bytes) plus `license` field in `plugin.json`, `marketplace.json`, `pyproject.toml`, and `server.json` carrying the SPDX identifier `MIT`. README references the same. GitHub auto-detects and badges the license.

## Community health files

### Open contribution with health files

`CONTRIBUTING.md` present (~1 KB). `.github/PULL_REQUEST_TEMPLATE.md` present. `.github/ISSUE_TEMPLATE/` directory present (contents not enumerated). `.github/dependabot.yml` present. No `SECURITY.md`, no `CODE_OF_CONDUCT.md`.

## Cross-ecosystem distribution

### Triple-ecosystem (Claude + Codex + Cursor)

The plugin advertises to four discovery surfaces from one repo: Claude Code marketplaces (`.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json`), the official MCP Registry (`server.json` with the modelcontextprotocol/registry schema, complete with `isSecret`, `isRequired`, `registryType: "pypi"`), glama.ai's MCP server directory (`glama.json` — three-line maintainer declaration), and PyPI directly (`pyproject.toml` for `pip install mcp-outline`). Plus Docker via `ghcr.io/vortiago/mcp-outline:latest` with multi-arch amd64+arm64 images. The bump script keeps all four manifest files in lockstep with each release.

### MCP Registry presence (`server.json`)

`server.json` (modelcontextprotocol/registry schema) at repo root carries `$schema`, package coordinates (`registryType: "pypi"`, `name: "mcp-outline"`, `version`), env-var schema with `isSecret`/`isRequired` flags, and is published at release time via `mcp-publisher login github-oidc` against the modelcontextprotocol/registry. The registry job rewrites the version in-place via `jq` from the tag at publish time.
