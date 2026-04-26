---
log-role: queue
---

# Expand check with community linter dimensions

## Purpose

Layer mature, community-maintained linters under `/ocd:check` as additional dimensions, alongside the existing project-specific checks (dormancy, parent-walking, markdown literal-character + blank-line). Each adopted tool wraps into a `Violation`-shaped result, merges into the unified report, and respects the same `allowlist.csv` suppression mechanism. One front-end, one report, one exit code.

The wrapper pattern is already established by the current `/ocd:check` orchestration — registering a new dimension is the same shape used by `dormancy`, `markdown`, and `python` today.

## Adoption order

The order is by bug-catching value per unit of integration cost, not by tool prominence.

1. **shellcheck** — finds real bugs in the project's shell surface: `.githooks/pre-commit`, `.githooks/post-commit`, `hooks/install_deps.sh`, `scripts/release.sh`, `scripts/test.sh`, `bin/project-run`, `plugins/*/bin/*-run`. Bash bugs are silent disasters; shellcheck has near-zero false-positive rate. Single-binary install, no Python deps. Adopt first.

2. **ruff** — Python linter + formatter (replaces flake8 / isort / partial pylint). Catches unused imports, undefined names, complexity smells, formatting drift. Configured via `pyproject.toml`. Project already conforms broadly to its defaults via the `python.md` convention; first run should produce a manageable diff. Configure rule set conservatively to start; tighten over time.

3. **PyMarkdownLnt** (or markdownlint-cli2 if Node toolchain is acceptable) — port of David Anson's markdownlint with the standard `MD###` rule registry. Layered *under* the existing custom markdown scanner: PyMarkdownLnt handles MD022 (blanks around headings), MD031 (blanks around fences), MD041 (first line is heading), etc.; our custom passes keep the project-specific rules (literal `{}<>` defensive flagging, blank-in-list with heading/blockquote interruption exemption, blank-line at fence-body boundaries, multi-blank-inside-fence, frontmatter universal opacity).

   PyMarkdownLnt's `PyMarkdownApi().scan_path(path)` returns `PyMarkdownScanFailure` records with file/line/column/rule_id — translates cleanly to our `Violation` shape. Rule IDs from its registry (`MD###`) map to `Markdown - <descriptive label>` so the existing report format is preserved.

4. **typos** (or **codespell**) — typo detection in code and prose. Project has substantial prose content (conventions, rules, decision logs) where misspellings sneak past unnoticed. Allowlist-driven for project-specific terms (PFN, dormancy, sandbox, etc.).

## Why this order

- **shellcheck** has the highest bug-discovery rate against the smallest, most-stable surface. Results are immediate and actionable.
- **ruff** opens the broadest categorical coverage on the language with the most code; standard adoption pattern across the Python ecosystem.
- **PyMarkdownLnt** aligns the project with the dominant markdown rule vocabulary (`MD###`) without sacrificing project-specific rules. Retroactive rather than disruptive.
- **typos** catches a category nothing else catches; intentionally last because it requires up-front allowlist curation to avoid noise.

## Out of scope for this idea

- **pyright in CI** — IDE shows diagnostics inline today. Adding to CI is independent of this initiative; capture separately if it's the gating concern.
- **bandit** (security) — project doesn't handle untrusted input directly.
- **gitleaks** — project doesn't process secrets.
- **vale** — prose-style linter; our voice is intentionally terse and technical, would require extensive customization for low return.
- **jsonschema** for `plugin.json` / `marketplace.json` / `hooks.json` / `settings.json` — separately useful (catches typos / missing fields against Claude Code's documented shapes), but adoption path is independent of community-linter integration. Worth its own idea entry.

## Wrapper architecture

Each adopted tool becomes a registered dimension under `systems/check/`:

- A new `_<dimension>.py` module exposes `scan_paths(paths) -> list[Violation]` mirroring the existing `_markdown.py` and `_python.py` shape.
- The module shells out to the tool (or imports its API for PyMarkdownLnt, ruff's Python API, etc.) and translates findings into `Violation` records with rule labels prefixed by the dimension name (`shellcheck - SC2086`, `ruff - F401`, `Markdown - MD022`, `typos - misspelling`).
- The `__main__.py` registers the dimension in the `DIMENSIONS` mapping; `all` picks it up automatically.
- `allowlist.csv` gains rows for `(rule, pattern)` exemptions specific to each tool's findings.

## Dependencies

- Existing `/ocd:check` orchestration (dormancy + markdown + python today)
- For Python-implemented tools (ruff API, PyMarkdownLnt): add to plugin's `pyproject.toml`; SessionStart hook auto-installs into the plugin's isolated venv
- For shell-binary tools (shellcheck, typos): runtime-check availability in the dimension's wrapper; corrective install guidance in the error message per the `system and global tool dependencies` discipline
