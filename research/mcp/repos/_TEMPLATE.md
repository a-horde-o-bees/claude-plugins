# _TEMPLATE

Per-repo research file structure for MCP server repositories. Every field below must be filled in every repo file. "Not present" / "not applicable" with a one-line reason is valid — nothing silently defaults. Preset values are prompts, not menus: if reality doesn't fit, describe what's actually there in free-form. Each field accepts `other: ...` catchalls so novel choices aren't forced into the nearest preset. Every structured section ends with `Pitfalls observed` — one or more bullets capturing axis-specific gotchas this repo reveals, or `none` with a one-line reason.

The `## Python-specific` section is appended only for Python-primary repos. For other languages, omit it or adapt the sub-fields to the relevant ecosystem.

Filename convention: `<owner>--<repo>.md` (double-hyphen separator to avoid collision with single-hyphen repo names). Not-found / unresolvable records go to `_missing--<best-guess>.md` with a brief note on names tried.

---

# <owner>/<repo>

## Identification

- url:
- stars:
- last-commit (date or relative):
- license:
- default branch:
- one-line purpose: (what this MCP server does, extracted from the README opening)

## Language and runtime

- language(s) + version constraints:
- framework/SDK in use:
- pitfalls observed:

## Transport

- supported transports:
- how selected (flag, env, separate entry point, auto-detect, other):
- pitfalls observed:

## Distribution

- every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, remote-hosted URL, Smithery, custom installer, other):
- published package name(s):
- install commands shown in README:
- pitfalls observed:

## Entry point / launch

- command(s) users/hosts run:
- wrapper scripts, launchers, stubs:
- pitfalls observed:

## Configuration surface

- how config reaches the server (env vars, CLI args, config file with path and format, stdin prompt, OS keyring, host-passed params, combinations, other):
- pitfalls observed:

## Authentication

- flow (none, static token, OAuth with description, per-request header, in-server vault, multi-mode, other):
- where credentials come from:
- pitfalls observed:

## Multi-tenancy

- single-user / per-request tenant via middleware / workspace-keyed / OAuth-scoped remote / base-directory sandboxing / tenancy-as-tool-argument / not applicable / other:
- pitfalls observed:

## Capabilities exposed

- tools / resources / prompts / sampling / roots / logging / other:
- pitfalls observed:

## Observability

- logging destination and format, metrics, tracing, debug flags:
- pitfalls observed:

## Host integrations shown in README or repo

For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, Codex CLI, Warp, Gemini CLI, Kiro, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, other).

- hosts observed:
- pitfalls observed:

## Claude Code plugin wrapper

- presence and shape (`.claude-plugin/plugin.json`, `.mcp.json` at repo root, full plugin layout, `.claude-plugin/marketplace.json` only, not present, other):
- pitfalls observed:

## Tests

- presence, framework, location, notable patterns (fixture style, golden files, protocol conformance, etc.):
- pitfalls observed:

## CI

- presence, system (GitHub Actions, Buildkite, GitLab CI, other), triggers, what it runs:
- pitfalls observed:

## Container / packaging artifacts

- Dockerfile, docker-compose, Helm chart, systemd unit, brew formula, DXT manifest, other:
- pitfalls observed:

## Example client / developer ergonomics

- MCP Inspector launcher, curl stubs, make targets, Justfile, dev scripts, sample configs:
- pitfalls observed:

## Repo layout

- single-package / monorepo / vendored / other — describe what's actually there:
- pitfalls observed:

## Notable structural choices

Open bullets for anything unusual or interesting not captured by the fields above. Serves as the catchall for patterns that don't fit a labeled axis.

-

## Unanticipated axes observed

Open bullets naming decision dimensions this repo reveals that aren't in the structured fields above. Candidates for new rows in the pattern doc's Decisions or Features tables.

-

## Python-specific

Present only for Python-primary repos. Omit for non-Python or adapt the sub-fields to the relevant ecosystem (e.g., a `## TypeScript-specific` section would parallel this structure: SDK variant, packaging manifest, entry point, install workflow, testing idioms, dev tooling).

### SDK / framework variant

- which SDK: raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / FastMCP 3.x / custom
- version pin from pyproject.toml:
- import pattern observed:

### Python version floor

- `requires-python` value from pyproject.toml:
- any CI matrix confirming tested versions:

### Packaging

- build backend (hatchling / setuptools / uv build / poetry-core / flit / pdm / other):
- lock file present (uv.lock / poetry.lock / pdm.lock / none):
- version manager convention (uv / poetry / pdm / pip-tools / plain pip / other):

### Entry point

- how the server is launched: `[project.scripts]` console script / `__main__.py` module (`python -m pkg`) / bare script / CLI wrapper with subcommands / custom `install.py` / other
- actual console-script name(s) registered:
- host-config snippet shape in README (`uvx <pkg>` / `uv run` / `pipx run` / `python -m` / absolute venv-python path / other):

### Install workflow expected of end users

- pip / pipx / uv tool install / uvx run / poetry / from-source clone + venv / Docker / other:
- one-liner the README recommends:

### Async and tool signatures

- tools declared sync (`def`) or async (`async def`):
- explicit asyncio / anyio usage:

### Type / schema strategy

- Pydantic models / dataclasses / TypedDict / raw dict / `Annotated[...]` for field docs:
- schema auto-derived (FastMCP style) or hand-authored JSON Schema:

### Testing

- pytest / pytest-asyncio / unittest / none:
- fixture style — plain-function calls vs in-memory MCP client vs protocol conformance:

### Dev ergonomics

- `mcp dev`, `fastmcp dev`, MCP Inspector launcher script, Makefile, Justfile, other hot-reload tooling:

### Notable Python-specific choices

Open bullets for anything unusual about this repo's Python stack not captured above. Serves as the Python-specific catchall analogous to `## Notable structural choices` above.

-

## Gaps

Open bullets — what couldn't be determined within the WebFetch / GitHub API budget + what source would resolve it.

-
