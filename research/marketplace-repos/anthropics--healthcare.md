# anthropics/healthcare

## Identification

- **URL**: https://github.com/anthropics/healthcare
- **Stars**: 203
- **Last commit date**: 2026-01-16 (sha `c382e94`, merge of PR #31)
- **Default branch**: `main`
- **License**: none declared via GitHub licensing (repo `license` field is null); README states "Skills are provided under Anthropic's terms of service"
- **Sample origin**: primary (Anthropic-owned)
- **One-line purpose**: "Skills for healthcare workflows including clinical trials, prior authorization review, and FHIR API development" (README).

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: `metadata.{version, description}` wrapper (`metadata.version: "1.0.0"`, `metadata.description: "Skills for healthcare workflows …"`). No top-level `description`.
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: category + tags uniformly on all 7 plugins. Every plugin declares `category: "healthcare"` and a 3–5-element `tags` array (e.g., `["fhir","hl7","api","interoperability","smart-on-fhir"]`). No `keywords`.
- **`$schema`**: absent
- **Reserved-name collision**: no — top-level `name: "healthcare"` matches the repo name and does not collide with any reserved Claude Code name.
- **Pitfalls observed**: the marketplace file declares `owner.{name, email}` (`Anthropic`, `support@anthropic.com`) but no `owner.url`; docs allow this but leave downstream link rendering undefined. None of the three skill-carving plugins duplicates the carved skill's description in its own plugin.json (no plugin.json exists for them — see purpose 2).

## 2. Plugin source binding

- **Source format(s) observed**: all `relative`. Three skill-carving plugins use `source: "./"` (repo root); four MCP plugins use `source: "./<plugin-dir>"` (e.g., `./cms-coverage`).
- **`strict` field**: `false` explicit on exactly the three skill-carving plugins (`clinical-trial-protocol`, `prior-auth-review`, `fhir-developer`). Absent on the four MCP-only plugins (implicit `strict: true`).
- **`skills` override on marketplace entry**: present on the three `strict: false` plugins, each listing a single skill directory (e.g., `"skills": ["./clinical-trial-protocol-skill"]`). Absent on the MCP-only plugins.
- **Version authority**: split by plugin type. For the three skill-carving plugins there is no `plugin.json` in the carved skill directory (nor in any `.claude-plugin/` for those plugins) — the marketplace entry carries no `version` either, so the only version present is `metadata.version: "1.0.0"` on the marketplace manifest itself. For the four MCP plugins, `plugin.json` is authoritative and each declares `"version": "1.0.0"`.
- **Pitfalls observed**: skill-carving plugins intentionally have no plugin.json; this is the docs-sanctioned carve pattern but means an installer cannot read a plugin-level version — it has to rely on the containing marketplace's `metadata.version` (single coarse version covering all three carved plugins simultaneously). Compare to the life-sciences sibling repo (noted by the caller as also using `strict: false` carving) — this repo mirrors the same carving shape and metadata-only versioning rather than maintaining per-plugin version files.

## 3. Channel distribution

- **Channel mechanism**: no split. Users pin via `@ref` if at all; the marketplace ships a single stream.
- **Channel-pinning artifacts**: absent. No `stable` vs `latest` marketplaces, no dev-counter, no channel-suffixed tags.
- **Pitfalls observed**: the single `v1.0.0` tag and absence of a `CHANGELOG.md` mean consumers tracking `main` versus the tag cannot easily diff intervening skill changes.

## 4. Version control and release cadence

- **Default branch name**: `main`
- **Tag placement**: on `main` (single tag `v1.0.0` at sha `f778439`, on main history).
- **Release branching**: none — tag-on-main.
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: absent.
- **Pre-commit version bump**: no.
- **Pitfalls observed**: only one tag exists (`v1.0.0`, published 2026-01-09), yet main has continued to advance (latest commit 2026-01-16, a week after the release). No subsequent tag cut for those merges, so `main` drifts from the only released version with no user-visible channel to opt in to.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery for the skill-carving plugins (they have no plugin.json at all; skill registration happens via the marketplace-entry `skills` override). The four MCP plugins use inline `mcpServers` config objects in plugin.json (no external `.mcp.json`).
- **Components observed**:
    - skills — yes (3 skill directories: `clinical-trial-protocol-skill/`, `prior-auth-review-skill/`, `fhir-developer-skill/`, each with `SKILL.md` plus `references/`, some with `scripts/` and `assets/`)
    - commands — no
    - agents — no
    - hooks — no
    - .mcp.json — no (MCP configs are inline inside each MCP plugin's plugin.json)
    - .lsp.json — no
    - monitors — no
    - bin — no
    - output-styles — no
- **Agent frontmatter fields used**: not applicable (no agents)
- **Agent tools syntax**: not applicable
- **Pitfalls observed**: the three skill-carving plugins each own only a single skill. The carving could be replaced by per-plugin `plugin.json` files inside each skill directory; choosing carving instead centralizes plugin metadata in `marketplace.json` at the cost of not having a place to record per-plugin version history.

## 6. Dependency installation

- **Applicable**: partial — the `clinical-trial-protocol-skill` calls for Python with `scipy` and `numpy` (README "Requirements"), and ships `scripts/sample_size_calculator.py`. Other skills: no runtime deps. MCP plugins: remote HTTP MCP servers, no client-side install.
- **Dep manifest format**: none. `scripts/sample_size_calculator.py` is shipped but no `requirements.txt`, `pyproject.toml`, or hook-driven install is present. The README delegates to "Python with scipy and numpy" as a user-side prerequisite.
- **Install location**: not applicable (no managed install).
- **Install script location**: not applicable.
- **Change detection**: not applicable.
- **Retry-next-session invariant**: not applicable.
- **Failure signaling**: not applicable.
- **Runtime variant**: Python (unmanaged — user-provided environment).
- **Alternative approaches**: none — the script is a plain module invoked directly; no PEP 723 header, no `uv run --script`, no pointer file.
- **Version-mismatch handling**: none.
- **Pitfalls observed**: "Requirements: Python with scipy and numpy" is prose in README only; a user without those packages will hit a runtime `ImportError` inside the skill with no corrective guidance. This is the opposite of the dep-management sample repos that isolate runtime deps in a plugin venv.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — no `bin/` directories in any plugin, no CLI wrappers. Python scripts live under each skill's `scripts/` and are called by the skill itself, not exposed as user-runnable CLIs.
- **`bin/` files**: not applicable
- **Shebang convention**: not applicable
- **Runtime resolution**: not applicable
- **Venv handling (Python)**: not applicable
- **Platform support**: not applicable
- **Permissions**: not applicable
- **SessionStart relationship**: not applicable
- **Pitfalls observed**: none.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable
- **Pitfalls observed**: none — the skills are all content-driven and the MCP servers are remote HTTP endpoints with no user-supplied credentials surfaced at install time.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: not applicable
- **Failure posture**: not applicable
- **Top-level try/catch wrapping**: not applicable
- **Pitfalls observed**: none — no hooks of any kind in any plugin.

## 10. Session context loading

- **SessionStart used for context**: no
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: not applicable
- **SessionStart matcher**: not applicable
- **Pitfalls observed**: none.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — the only tag (`v1.0.0`) covers the whole marketplace, not an individual plugin.
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: none (no test directory, no test files anywhere in the tree)
- **Tests location**: not applicable
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: yes — 4 workflows in `.github/workflows/`
- **CI file(s)**: `claude-code-review.yml`, `claude-skill-review.yml`, `claude.yml`, `release.yml`
- **CI triggers**:
    - `claude-code-review.yml` — `pull_request: [opened, synchronize, ready_for_review, reopened]`
    - `claude-skill-review.yml` — same PR events plus `workflow_call` (reusable) with `CLAUDE_CODE_OAUTH_TOKEN` secret
    - `claude.yml` — `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review` — gated on `@claude` mention
    - `release.yml` — `push: tags: ['v*']`
- **CI does**: agent-driven review (no pytest, no linting, no validators). `claude-code-review.yml` installs `code-review@claude-code-plugins` from `https://github.com/anthropics/claude-code.git` and runs `/code-review:code-review`. `claude-skill-review.yml` detects changed `SKILL.md`-containing directories via git diff and runs one job per affected skill, installing `example-skills@anthropic-agent-skills` from `https://github.com/anthropics/skills.git` and invoking skill-creator to comment on the PR. `claude.yml` is a general `@claude` responder using `anthropics/claude-code-action@v1`.
- **Matrix**: `claude-skill-review.yml` uses a dynamic matrix (`matrix.skill: fromJson(needs.detect-skills.outputs.skills)`) computed from `find . -name SKILL.md`. Others are single-job.
- **Action pinning**: tag-pinned (`actions/checkout@v4`, `anthropics/claude-code-action@v1`, `softprops/action-gh-release@v1`). No SHA pinning.
- **Caching**: none declared.
- **Test runner invocation**: not applicable (no tests).
- **Pitfalls observed**: the skill-review workflow's `detect-skills` step runs `git diff --name-only origin/${{ github.base_ref }}...HEAD` after a `fetch-depth: 0` checkout — correct shape, but if a PR renames a skill directory the renamed-away skill is reviewed and the renamed-to skill may or may not be depending on how git diff reports rename thresholds. No validator ensures `marketplace.json` stays in sync when skill directories are added or removed.

## 14. Release automation

- **`release.yml` present**: yes
- **Release trigger**: `push: tags: ['v*']`
- **Automation shape**: skill-zip build + draft release. Iterates every directory matching `*-skill/`, zips its contents into `<skill_name>-<GITHUB_REF_NAME>.zip`, and attaches all such zips to a GitHub release.
- **Tag-sanity gates**: none — no verify-tag-on-main, no version-vs-tag assertion, no regex check.
- **Release creation mechanism**: `softprops/action-gh-release@v1`
- **Draft releases**: yes (`draft: true`, `prerelease: false`, `generate_release_notes: true`)
- **CHANGELOG parsing**: no — relies entirely on `generate_release_notes: true`. There is no `CHANGELOG.md` in the repo.
- **Pitfalls observed**: the packaging pattern `for skill_dir in *-skill/` depends on directory naming convention — the three current skill directories end in `-skill` and all three are released as zips. The four MCP plugin directories (`cms-coverage`, `npi-registry`, `pubmed`, `icd10-codes`) do not match `*-skill/` and are **not** packaged for release; consumers of those plugins must install from source via the marketplace flow. No version-vs-`plugin.json` cross-check: an MCP plugin's `plugin.json` `version` field could drift from the tag without the workflow objecting.

## 15. Marketplace validation

- **Validation workflow present**: no — no `validate.yml`, no pre-commit hook, no `claude plugin validate` invocation in CI.
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no
- **Hooks.json validation**: not applicable (no hooks)
- **Pitfalls observed**: marketplace.json has no structural validation gate — invalid JSON or a reference to a deleted skill directory would only surface at install time. The two review workflows are semantic reviewers (Claude-in-the-loop), not schema validators.

## 16. Documentation

- **`README.md` at repo root**: present (~50 lines)
- **`README.md` per plugin**: mixed — `clinical-trial-protocol-skill/README.md` and `prior-auth-review-skill/README.md` exist; `fhir-developer-skill/` has no README (SKILL.md only). None of the four MCP plugins has a README.
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: absent (repo root or per plugin)
- **`CLAUDE.md`**: absent
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`
- **LICENSE**: absent as a file (no `LICENSE`, no SPDX identifier). README prose: "Skills are provided under Anthropic's terms of service." GitHub's license detection returns null.
- **Badges / status indicators**: absent
- **Pitfalls observed**: no LICENSE file means GitHub's license picker shows "No license" and downstream package tooling cannot identify terms; the README prose is not machine-readable. Skills without any README rely entirely on SKILL.md frontmatter description for discoverability.

## 17. Novel axes

- **Skill-carving marketplace with single-skill carves** — three plugins each declare `source: "./"`, `strict: false`, and carve out a single skill directory via the marketplace-entry `skills` array. Distinct from the more common aggregator pattern where one `strict: false` entry carves multiple plugins from a multi-plugin monorepo. Here the carve enforces 1:1 plugin-to-skill mapping while allowing all three to share the repo root as their `source`, avoiding per-plugin `.claude-plugin/plugin.json` files.
- **Hybrid marketplace: skill-carving plugins + MCP-only plugins in one manifest** — the same `marketplace.json` mixes two structurally different plugin shapes (three skill plugins with `source: "./"` + `skills` override, four MCP plugins with `source: "./<dir>"` + their own `plugin.json` housing `mcpServers`). The pattern doc's `strict: false` carving notes may not account for this hybrid where only some entries carve while others follow default discovery.
- **Agent-in-the-loop CI instead of lint/validate CI** — three of four workflows install Claude Code plugins from sibling Anthropic marketplaces (`anthropics/claude-code.git`, `anthropics/skills.git`) and run semantic reviews (code-review, skill-creator) as the CI. The fourth (`release.yml`) is mechanical packaging. There is no pytest, no ruff, no pyright, no JSON-schema validator. Pattern-doc purpose 13 may need a category for "agent-driven CI review" as distinct from deterministic validation.
- **Dynamic matrix over `find SKILL.md`** — `claude-skill-review.yml` computes its matrix from `find . -name SKILL.md`, not from a declared list. Interesting pattern: the repo auto-adjusts to newly added skills without workflow edits, at the cost of no up-front validation that every SKILL.md-containing directory is registered in marketplace.json.
- **Packaging naming contract (`*-skill/` glob)** — the release workflow's artifact discovery is structural: `for skill_dir in *-skill/`. Skill directories must be named with the `-skill` suffix (all three are: `clinical-trial-protocol-skill`, `prior-auth-review-skill`, `fhir-developer-skill`). MCP plugin directories deliberately do not match and are silently excluded from release artifacts. This is an implicit naming convention that the pattern doc may want to capture as a release-artifact-discovery pattern alongside explicit file lists.
- **Remote HTTP MCP with inline `mcpServers` in plugin.json** — the four MCP plugins (three authored by deepsense.ai, one by Anthropic) use `"type": "http"` with a hosted URL. No process spawn, no command, no env vars. Clean contrast to MCP plugins that ship a local stdio server requiring dep install.
- **Marketplace-level `metadata.version` as sole version for carved plugins** — because the skill-carving plugins have no `plugin.json`, `metadata.version: "1.0.0"` in `marketplace.json` is the only machine-readable version for those three plugins. The MCP plugins maintain their own independent `version` in their `plugin.json`. This asymmetry may deserve a pattern-doc note under purpose 2 (version authority).

## 18. Gaps

- **Effective "Anthropic terms of service" content** — the README states skills are distributed under Anthropic's ToS, but without a LICENSE file or link, the exact terms are not determinable from the repo itself. Resolving: inspect `anthropic.com/terms` at the time of tag; outside the scope of a structural audit.
- **Life-sciences sibling comparison** — the caller described life-sciences as "also using `strict: false` skill carving". A dedicated life-sciences research file is not yet present in `research/marketplace-repos/` (only `anthropics--healthcare.md` exists alongside the template/index). Structural comparison would require fetching `anthropics/life-sciences` directly — deferred to the life-sciences agent's per-repo file when produced.
- **Whether skill-carving plugins are installable standalone** — without a `plugin.json` in each skill dir, only the marketplace-entry route can install them. Not independently reproduced; resolving: run `/plugin install clinical-trial-protocol@healthcare` end-to-end and inspect the resulting plugin cache. Outside WebFetch budget.
- **Whether the `nadine-anthropic-patch-1` merge (last commit) touched a skill, a manifest, or only docs** — not inspected at commit granularity; resolving: `gh api repos/anthropics/healthcare/commits/c382e94 --jq '.files[].filename'`. Skipped to conserve budget; does not affect purpose assignments.
- **CI-run secret scoping** — `claude-skill-review.yml` declares `workflow_call` with a required `CLAUDE_CODE_OAUTH_TOKEN` secret, implying it is callable from other workflows, but no caller exists in this repo. Possibly reused by `anthropics/` sibling repos. Resolving: cross-repo workflow call search via `gh api search` — deferred.
