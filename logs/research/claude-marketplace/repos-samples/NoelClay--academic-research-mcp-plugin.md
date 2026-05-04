# NoelClay/academic-research-mcp-plugin

## Identification

- **URL**: https://github.com/NoelClay/academic-research-mcp-plugin
- **Stars**: 0
- **Last commit date**: 2026-04-11 (single-day repo; created 2026-04-11T19:16:45Z, pushed 2026-04-11T23:27:15Z)
- **Default branch**: main
- **License**: Not declared in GitHub metadata (`license: null`); `package.json` declares `"license": "MIT"` and README ends with "License / MIT". No `LICENSE` file in tree.
- **Sample origin**: dep-management
- **One-line purpose**: "Multi-agent Claude Code plugin for hallucination-free academic research via Agentic RAG" (GitHub description); README opens: "A Claude Code plugin that teaches any subject using only retrieved, cited sources — never parametric knowledge."

## 1. Marketplace discoverability

- **Manifest layout**: Not applicable — this is a standalone plugin repo, not a marketplace. There is no `.claude-plugin/marketplace.json`; only `.claude-plugin/plugin.json`. Installed per README via `claude --plugin-dir /path/to/research-learning-tutor`.
- **Marketplace-level metadata**: Not applicable — no marketplace manifest.
- **`metadata.pluginRoot`**: Not applicable — no marketplace manifest.
- **Per-plugin discoverability**: `keywords` array in `plugin.json`: `["research", "learning", "tutor", "academic", "citation", "RAG"]`. No `category` or `tags`. GitHub repo `topics` array is empty.
- **`$schema`**: Absent from `plugin.json`.
- **Reserved-name collision**: No — plugin `name` is `research-learning-tutor`.
- **Pitfalls observed**: Repo-level name (`academic-research-mcp-plugin`) does not match the plugin `name` (`research-learning-tutor`). README title is a third variant ("Research Learning Tutor"). A user cloning and installing via `--plugin-dir` gets the plugin-level name, but the GitHub identity says something different — harmless but slightly disorienting. No marketplace entry means no `source` / `strict` / channel surface to inspect.

## 2. Plugin source binding

- **Source format(s) observed**: Not applicable — no marketplace manifest. Installation is local-directory (`claude --plugin-dir /path/to/...`) per README; equivalent to a `relative` source if someone else packaged this into a marketplace.
- **`strict` field**: Not applicable — no marketplace entry.
- **`skills` override on marketplace entry**: Not applicable — no marketplace entry.
- **Version authority**: `plugin.json` only — sole version declaration is `"version": "0.1.0"` in `.claude-plugin/plugin.json`. `package.json` also carries `"version": "0.1.0"` for the Node sub-manifest, but that governs the parser subtree, not the plugin identity.
- **Pitfalls observed**: Plugin `version` and `package.json` `version` are independently editable and currently coincide at `0.1.0` — if one bumps without the other, downstream consumers see a mismatch. Not a marketplace plugin so no drift between plugin and marketplace declarations.

## 3. Channel distribution

- **Channel mechanism**: No split — single `main` branch, no tags, no release branches. Users installing via `--plugin-dir` get whatever is on disk at clone time.
- **Channel-pinning artifacts**: Absent.
- **Pitfalls observed**: No pinning story at all — any consumer of this repo has to track commit SHAs themselves.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: None — `gh api .../tags` returns empty.
- **Release branching**: None — only `main` exists.
- **Pre-release suffixes**: None observed — version stays at `0.1.0`.
- **Dev-counter scheme**: Absent.
- **Pre-commit version bump**: No — no `.pre-commit-config.yaml`, no git hooks shipped, no CI.
- **Pitfalls observed**: The entire repo history is five commits on a single day (2026-04-11) with no tagging, no releases, no CHANGELOG. Version `0.1.0` has persisted through every commit. For a consumer this means "latest `main`" is the only pointer.

## 5. Plugin-component registration

- **Reference style in plugin.json**: Default discovery — `plugin.json` contains only identity/metadata (`name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `userConfig`). No component path fields. MCP servers live in the separate repo-root `.mcp.json` (the native Claude Code discovery location); skills under `skills/`, agents under `agents/`, commands under `commands/`, hooks under `hooks/hooks.json` — all at Claude Code's default locations.
- **Components observed**:
    - skills: yes — `skills/research-tutor/SKILL.md`
    - commands: yes — `commands/learn.md`
    - agents: yes — `agents/researcher.md`
    - hooks: yes — `hooks/hooks.json` (SessionStart)
    - .mcp.json: yes — at repo root, two servers (`academic-search`, `web-search`)
    - .lsp.json: no
    - monitors: no
    - bin: no
    - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `model` (`sonnet`), `isolation` (`worktree`), `maxTurns` (`30`), `tools`. Note `isolation: worktree` on an agent — the agent is explicitly declared to run in a git-worktree isolation envelope.
- **Agent tools syntax**: Plain tool names — fully-qualified MCP tool names (`mcp__academic-search__search_papers`, etc.) mixed with built-in tool names (`Read`, `Bash`, `Glob`, `Grep`). No permission-rule syntax like `Bash(uv run *)`. The command file (`commands/learn.md`) uses `allowed-tools` with wildcard matchers (`mcp__academic-search__*`, `mcp__web-search__*`).
- **Pitfalls observed**: Agent declares `isolation: worktree` but the plugin doesn't ship a git repo inside the plugin — agent worktree isolation presumes the invoking session's project is a git repo; in the research/teaching use case (where the agent downloads PDFs and writes reports) the worktree's purpose is ambiguous. `maxTurns: 30` is a hard ceiling — an agent hit limit would truncate mid-research with no documented recovery.

## 6. Dependency installation

- **Applicable**: Yes — the plugin has both Python and Node runtime deps that must be present before the MCP servers or PDF parser can run.
- **Dep manifest format**: Both — `requirements.txt` at repo root (Python) and `package.json` at repo root (Node).
- **Install location**: `${CLAUDE_PLUGIN_DATA}` — Python venv lands at `$PLUGIN_DATA/venv`, `node_modules` installs into `$PLUGIN_DATA` (hook does `cd "$PLUGIN_DATA" && cp "$PKG_SRC" . && npm install`).
- **Install script location**: `hooks/session-start.sh` (registered in `hooks/hooks.json` as the sole SessionStart handler).
- **Change detection**: `diff -q` for both managers. Python compares `$PLUGIN_ROOT/requirements.txt` against a cached `$PLUGIN_DATA/requirements.txt`; Node compares `$PLUGIN_ROOT/package.json` against `$PLUGIN_DATA/package.json`. On `diff` miss, install runs and cache is refreshed; on install failure, cache marker is removed.
- **Retry-next-session invariant**: `rm` on failure — explicit `|| rm -f "$REQ_DST"` (Python) and `|| rm -f "$PKG_DST"` (Node). Next session's `diff -q` will again miss, triggering a retry. This is the documented "retry-next-session" pattern.
- **Failure signaling**: Silent — `set -euo pipefail` is at the top, but both install branches suppress output with `2>/dev/null` and the `|| rm -f` fallback swallows non-zero exit codes. The script always `exit 0`s (final line) after emitting the persona-injection JSON. No stderr surfaced to the user; no `continue: false` or exit-2 gating. Missing deps surface later as MCP server import errors.
- **Runtime variant**: Mixed — Python (pip via stdlib `venv`, not `uv`) + Node (npm).
- **Alternative approaches**: None — uses the "venv + pip install -r" classic pattern for Python and `npm install` for Node. No PEP 723 inline scripts, no `uvx`/`npx` ad-hoc, no pointer files.
- **Version-mismatch handling**: None — no Python-minor-version tracking (venv is created once with whatever `python3` resolves on the user's system; if they upgrade Python, the venv silently bitrots). Same for Node ABI (`node_modules` compiled native modules would break on Node major-version change with no detection).
- **Pitfalls observed**:
    - `python3 -m venv ... 2>/dev/null || true` means venv-creation failure is invisible — a user without `python3-venv` apt package gets a silent no-op and then `$VENV_DIR/bin/pip` doesn't exist, so the subsequent `pip install` fails and the `rm "$REQ_DST"` runs, but the user never learns why. No corrective error message per Graceful Degradation.
    - `diff -q` change detection compares source against cached copy, but the cached copy is the pre-install snapshot. If `pip install` succeeds but the install itself fails to actually land a package (network flake), `diff -q` will say "in sync" next session and not retry. The `|| rm -f` only runs if pip's exit code is non-zero — partial-install scenarios aren't detected.
    - Hook output combines stdout JSON (the persona `hookSpecificOutput.additionalContext`) with silenced stderr from pip/npm. Works because `2>/dev/null` routes noise away from the JSON channel, but any loud install error would currently break the JSON emission.
    - Persona-injection JSON and dep-install live in the same hook script; a change to persona text means the dep-install path is re-reviewed unnecessarily.

## 7. Bin-wrapped CLI distribution

- **Applicable**: No — no `bin/` directory. The PDF parser (`src/parsers/pdf-parser.js`) is invoked directly by path from the `/learn` command (`node ${CLAUDE_PLUGIN_ROOT}/src/parsers/pdf-parser.js <pdf-path> <output-path>`) rather than exposed via a bin wrapper. The MCP servers are invoked via `.mcp.json` with an explicit `command` path (`${CLAUDE_PLUGIN_DATA}/venv/bin/python`). No bin-wrapping pattern observed.
- **`bin/` files**: Not applicable.
- **Shebang convention**: Not applicable (no bin). For context: `hooks/session-start.sh` uses `#!/usr/bin/env bash`; `src/parsers/pdf-parser.js` uses `#!/usr/bin/env node` but is invoked via `node <path>`, not directly.
- **Runtime resolution**: Not applicable.
- **Venv handling (Python)**: Not applicable (no bin layer). The MCP servers resolve via `.mcp.json`'s explicit `command: "${CLAUDE_PLUGIN_DATA}/venv/bin/python"` — no exec-wrapper, no `uv run --script`, no pointer file. The Claude Code harness spawns the interpreter directly.
- **Platform support**: Not applicable. (Hook script is POSIX bash; `.mcp.json` assumes `venv/bin/python` which is nix-style — no Windows story.)
- **Permissions**: Not applicable.
- **SessionStart relationship**: Not applicable — no bin layer to populate. SessionStart does install the venv that `.mcp.json` later references, but that's a dep-install concern, not a bin-wrapper relationship.
- **Pitfalls observed**: `.mcp.json` hard-codes `venv/bin/python` — on Windows this would be `venv\Scripts\python.exe`. Plugin has no Windows path branch and no documented platform requirement beyond "Python 3.10+, Node.js 18+" in README.

## 8. User configuration

- **`userConfig` present**: Yes — in `plugin.json`.
- **Field count**: 2 — `semantic_scholar_api_key` and `unpaywall_email`.
- **`sensitive: true` usage**: Correct — `semantic_scholar_api_key` is `sensitive: true` (genuine API secret); `unpaywall_email` is `sensitive: false` (correctly un-flagged since Unpaywall treats the email as a public rate-limit identifier, not a credential).
- **Schema richness**: Minimal — each field has only `description` and `sensitive`. No `type`, no `default`, no enum, no validation pattern.
- **Reference in config substitution**: `${user_config.KEY}` substitution in `.mcp.json`'s `env` block translates to `CLAUDE_PLUGIN_OPTION_<KEY>` env vars consumed by the server (e.g., `CLAUDE_PLUGIN_OPTION_SEMANTIC_SCHOLAR_API_KEY`, `CLAUDE_PLUGIN_OPTION_UNPAYWALL_EMAIL`). The Python server reads them via `os.environ.get(...)`. Round-trip is observed — substitution in manifest, env consumption in server.
- **Pitfalls observed**:
    - No `required: true` on `unpaywall_email`, and the server only raises `ValueError("UNPAYWALL_EMAIL not configured...")` at tool-invocation time rather than at session start. A user who skips the prompt gets a runtime error deep inside tool execution, not an install-time error.
    - No validation that the email is actually an email string — any non-empty value passes the server's `if not email` check.
    - `web-search` MCP server receives no `env` block in `.mcp.json`, so user_config isn't piped to it even though it's a sibling server — intentional (no API keys needed) but easy to overlook when adding a new config field later.

## 9. Tool-use enforcement

- **PreToolUse hooks**: None.
- **PostToolUse hooks**: None.
- **PermissionRequest/PermissionDenied hooks**: Absent.
- **Output convention**: Not applicable — no enforcement hooks. The single SessionStart hook emits stdout JSON (`hookSpecificOutput.additionalContext`) with silenced stderr.
- **Failure posture**: Not applicable — no enforcement hooks.
- **Top-level try/catch wrapping**: Not applicable.
- **Pitfalls observed**: None — the plugin takes a pure persona-injection approach to behavior shaping (the persona lives in the SessionStart `additionalContext`) rather than runtime enforcement. Consistent with the skill/command instructions that tell the model what to do rather than a hook that blocks wrong tools.

## 10. Session context loading

- **SessionStart used for context**: Yes — the same `hooks/session-start.sh` that installs deps also emits a large `hookSpecificOutput.additionalContext` block containing the tutor persona, citation rules, and paid-resource flow. The dep-install and context-injection are fused in one script.
- **UserPromptSubmit for context**: No — no UserPromptSubmit hook.
- **`hookSpecificOutput.additionalContext` observed**: Yes — a heredoc `PERSONA_EOF` containing a JSON object with `hookSpecificOutput.hookEventName: "SessionStart"` and `additionalContext: "..."` with the full persona prompt (persona rules, citation rules, paid-resource flow, Korean-language fallback phrase).
- **SessionStart matcher**: None — `hooks.json` has a single `SessionStart` entry with no `matcher` field, so it fires on every sub-event (`startup`, `clear`, `compact`, `resume`).
- **Pitfalls observed**:
    - Persona is re-emitted on every `SessionStart` sub-event (including `compact`), which means the persona block is added to context every time auto-compact fires. That's effectively idempotent per session but doubles the token cost on long sessions. A `matcher: "startup"` would limit to fresh-session injection.
    - Persona content is duplicated between `hooks/session-start.sh` (injected into context) and `skills/research-tutor/SKILL.md` (loaded when the skill activates). Both sources describe the cold-researcher persona and citation rules — two copies diverging on edit is a maintenance hazard.

## 11. Live monitoring and notifications

- **`monitors.json` present**: No.
- **Monitor count + purposes**: None.
- **`when` values used**: Not applicable.
- **Version-floor declaration**: Not applicable — no monitors; README states "Claude Code >= 1.0.0" but that's a plugin-general version floor, not a monitor-specific one.
- **Pitfalls observed**: None.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: No.
- **Entries**: None.
- **`{plugin-name}--v{version}` tag format observed**: Not applicable — not a multi-plugin marketplace.
- **Pitfalls observed**: None.

## 13. Testing and CI

- **Test framework**: None — no `tests/` directory, no test files, no `pytest.ini`, no `jest.config.js`, no test script in `package.json` (`"scripts"` field is entirely absent).
- **Tests location**: Not applicable.
- **Pytest config location**: Not applicable.
- **Python dep manifest for tests**: Not applicable.
- **CI present**: No — `.github/` directory does not exist (GitHub API 404).
- **CI file(s)**: None.
- **CI triggers**: Not applicable.
- **CI does**: Not applicable.
- **Matrix**: Not applicable.
- **Action pinning**: Not applicable.
- **Caching**: Not applicable.
- **Test runner invocation**: Not applicable.
- **Pitfalls observed**: No automated validation of any kind — no manifest schema check, no MCP-server smoke test, no linter. The most recent commit message mentions "Fix code review issues: shared httpx client in batch_check_oa, remove Unpaywall silent fallback, remove unused PyMuPDF dep, Korean report template" which implies manual review happened, but there's no CI to enforce continued correctness.

## 14. Release automation

- **`release.yml` (or equivalent) present**: No.
- **Release trigger**: Not applicable.
- **Automation shape**: Not applicable.
- **Tag-sanity gates**: Not applicable.
- **Release creation mechanism**: Not applicable — no tags, no GitHub releases, no workflow.
- **Draft releases**: Not applicable.
- **CHANGELOG parsing**: Not applicable — no CHANGELOG.
- **Pitfalls observed**: None.

## 15. Marketplace validation

- **Validation workflow present**: No.
- **Validator**: Not applicable.
- **Trigger**: Not applicable.
- **Frontmatter validation**: Not applicable.
- **Hooks.json validation**: Not applicable.
- **Pitfalls observed**: Not applicable — not a marketplace repo and no plugin-manifest validation in CI either.

## 16. Documentation

- **`README.md` at repo root**: Present — ~2.3 KB, covers what-it-does / persona / install / usage / requirements / architecture / pedagogical-foundation / license. No badges.
- **`README.md` per plugin**: Not applicable — single-plugin repo; the root README is the plugin README.
- **`CHANGELOG.md`**: Absent.
- **`architecture.md`**: Absent at repo root and per plugin. README has an "Architecture" section with component bullets, and `docs/superpowers/specs/2026-04-12-research-learning-tutor-design.md` (12.8 KB) plus `docs/superpowers/plans/2026-04-12-research-learning-tutor.md` (37.8 KB) hold design/plan history, but none of these are a conventional `architecture.md`.
- **`CLAUDE.md`**: Absent.
- **Community health files**: None — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, or `LICENSE` file.
- **LICENSE**: Declared as MIT in `package.json` and mentioned in README, but no `LICENSE` file in the tree. GitHub's license detector accordingly returns `null`.
- **Badges / status indicators**: Absent.
- **Pitfalls observed**:
    - README's install command is `claude --plugin-dir /path/to/research-learning-tutor` — refers to a directory name (`research-learning-tutor`) that isn't the actual repo name (`academic-research-mcp-plugin`). A user following the README verbatim after `git clone` would fail unless they renamed the directory.
    - Declaring MIT license without shipping a `LICENSE` file makes legal reuse ambiguous; GitHub's own tooling can't confirm the license choice.
    - `docs/superpowers/plans/*.md` and `docs/superpowers/specs/*.md` suggest this repo was generated from a spec-driven workflow ("superpowers" naming), but those design docs are checked in as historical artifacts rather than actively maintained architecture references.

## 17. Novel axes

- **Mixed-runtime install in a single shell hook.** `hooks/session-start.sh` handles both Python venv + `pip install -r requirements.txt` and Node `cp package.json + npm install` in the same script, each guarded by its own `diff -q` against a `$PLUGIN_DATA`-cached copy with symmetric `|| rm -f` retry markers. Not a novel mechanism per manager, but the side-by-side twin-manager pattern — one hook script driving two ecosystems with identical diff/retry semantics — is a distinctive shape worth noting for the pattern doc.
- **Persona-injection fused with dep-install.** The SessionStart hook does two orthogonal things: install dependencies AND emit a large `hookSpecificOutput.additionalContext` persona block. Typical plugins split these: dep-install is a pure side-effect hook, context-injection is a separate SessionStart hook or lives in a skill. This plugin runs both through a single shell script that prints JSON to stdout at the end. Design axis worth calling out: "hook scripts that both mutate state and emit context in one exit cycle".
- **`isolation: worktree` on an agent frontmatter field.** The researcher agent declares `isolation: worktree` directly in its YAML, alongside `model: sonnet` and `maxTurns: 30`. Worth noting in the pattern doc as a concrete example of declaring agent-level isolation in frontmatter rather than invocation-site code.
- **Fully-qualified MCP tool names in agent `tools` list.** `tools: [mcp__academic-search__search_papers, ...]` — the agent restricts itself to specific MCP tool names rather than using a wildcard (`mcp__academic-search__*`) the way the sibling `commands/learn.md` does in its `allowed-tools` field. Two different conventions for the same kind of access-scoping in the same plugin — an authoring inconsistency but also a demonstration that both shapes are valid.
- **Non-English content inside persona/report templates.** The persona prompt in `session-start.sh` and the report template in `commands/learn.md` are multilingual — the user-facing prompts and report headings are in Korean (`학습 보고서`, `현재 수집된 자료로는 이 부분을 확인할 수 없다.`) while the surrounding skill/agent instructions remain in English. Novel for the pattern doc only if we care about localization conventions, but flagged here because it affects how citation-enforcement phrasing is validated — the "insufficient evidence" sentinel string is a Korean literal.
- **PDF parser reaches into `$CLAUDE_PLUGIN_DATA/node_modules` from `$CLAUDE_PLUGIN_ROOT`.** `src/parsers/pdf-parser.js` lives in `$CLAUDE_PLUGIN_ROOT` but `require()`s `pdf-parse` via `path.join(process.env.CLAUDE_PLUGIN_DATA || ".", "node_modules", "pdf-parse")`. Splits code (source-controlled) from deps (not source-controlled) along the `$ROOT` / `$DATA` boundary without relying on standard Node resolution. Pattern worth naming if multiple repos do this.

## 18. Gaps

- **Windows compatibility story.** Plugin ships only nix-style `venv/bin/python` in `.mcp.json` and `#!/usr/bin/env bash` in the hook. Unclear if the plugin is intentionally POSIX-only or if Windows was unexamined. Would resolve by: testing on Windows or asking upstream.
- **`diff -q` partial-install failure mode.** Can't confirm from static inspection whether a flaky-network `pip install` that returns 0 but partially installs would leave an inconsistent venv plus an up-to-date requirements cache. Would resolve by: running the hook with a hostile pip mirror.
- **Actual license status.** README says MIT, `package.json` says MIT, but no `LICENSE` file and GitHub's API reports `license: null`. Can't tell if this is author oversight or an intentional no-file declaration. Would resolve by: opening an issue upstream or reading the commit history for any removed LICENSE.
- **Whether the plugin ever worked end-to-end.** Five commits in one day with no tags, no CI, no tests, and no installation evidence in the README beyond a command line. Unclear if the author actually ran the full `/learn` flow against live Semantic Scholar + Unpaywall + DuckDuckGo + PDF-parse. Would resolve by: local installation and integration run — outside static-research budget.
- **Skill discovery from `skills/research-tutor/`.** Only `SKILL.md` is present in the skill directory — no component files (`_*.md`), no prompt fragments, no additional instructions. Pattern-doc-relevant question: does this plugin rely entirely on `SKILL.md` frontmatter description to be matched by Claude Code's skill router, or does something else (the `/learn` command explicitly referencing "research-tutor skill workflow") drive activation? Would resolve by: running the plugin and observing router behavior.
- **`isolation: worktree` semantics with no surrounding git repo.** Unclear whether Claude Code's worktree-isolation for agents requires the invoking session's project root to be a git repo, and what happens if a user runs `/learn <topic>` from a non-git directory. Would resolve by: testing or checking the plugin-reference docs' agent-isolation section.
