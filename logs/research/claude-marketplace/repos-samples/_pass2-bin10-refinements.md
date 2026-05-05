# Pass 2 Refinements — Bin 10

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Plugin-component registration` > `Hooks loaded out-of-band by an installer not the plugin manifest` — `affaan-m--everything-claude-code.md` — `plugin.json` enumerates `agents`, `skills`, and `commands` paths but omits any `hooks` entry; `hooks/hooks.json` is loaded by the repo's `install.sh`/`scripts/install-apply.js` installer at install time rather than referenced from the plugin manifest. Marketplace-flow installs that bypass the legacy installer may not pick up hooks at all. Distinct from `Hooks at well-known path without plugin.json reference` (which assumes Claude Code itself discovers them) — here a custom installer is the loader.

- `Hook timeout and async philosophy` > `Per-hook timeouts with explicit async fire-and-forget for telemetry` — `affaan-m--everything-claude-code.md` — Each hook entry in `hooks.json` carries an explicit `timeout` (5s for guards, 10s for governance/observation, 30s for `post:bash:dispatcher` and `post:quality-gate`) plus `async: true` on dispatcher and quality-gate hooks so the agent does not wait. Timeout per hook is sized to the hook's role: short for blocking guards, longer for observational pipelines, async for ones that should never delay the user.

- `Tool-use enforcement` > `Hook ID taxonomy with structured `{lifecycle}:{scope}:{purpose}` namespacing` — `affaan-m--everything-claude-code.md` — Hook entries use machine-parseable IDs like `pre:bash:dispatcher`, `pre:edit-write:gateguard-fact-force`, `post:edit:accumulator`, `post:bash:dispatcher`. The convention encodes lifecycle phase, matched scope, and purpose into a single deduplicatable identifier. Distinct from any consolidated path — most samples leave hooks unnamed or use ad-hoc strings. Worth surfacing because it makes hooks filterable and dedupable in tooling.

- `User configuration` > `Hidden env-var interface read by hooks without `userConfig` declaration` — `affaan-m--everything-claude-code.md` — Hooks read process env vars (`CLAUDE_PLUGIN_ROOT`, `CLAUDE_CODE_PACKAGE_MANAGER`, `ECC_GOVERNANCE_CAPTURE`) directly with no manifest declaration. Users who want to toggle hook behavior must read the hook source to learn the variable name. Distinct from existing `Env var read by script (hidden interface)` — but worth verifying whether the existing path covers the case of an opt-in flag like `ECC_GOVERNANCE_CAPTURE=1` whose only documentation is the hook source.

- `Plugin-component registration` > `Plugin name distinct from npm package name` — `affaan-m--everything-claude-code.md` — The Claude plugin name is `everything-claude-code` while the npm package is `ecc-universal`; the bin bootstrap chain re-implements both prefixes (`ecc`, `everything-claude-code`, `@ecc`, `marketplace/ecc`) when resolving plugin root. Identity bifurcation forces every consumer-side path to consider both spellings. Possibly fits under existing `Plugin name vs repo name drift` but the npm-vs-plugin-name divergence is a different mechanism.

- `Documentation surface` > ``PLUGIN_SCHEMA_NOTES.md` as reverse-engineered schema reference for consumers` — `affaan-m--everything-claude-code.md` — A `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` document captures observed validator rules (verbatim error strings, accepted vs rejected shapes) for downstream readers. Cross-references existing `Reverse-engineered validator notes as primary-source artifact` under `Marketplace validation`, but the artifact also serves as documentation — readers consulting the docs surface find it before they hit a validator.

- `Skill authoring conventions` > `Space-separated `allowed-tools` scalar` — `anthril--official-claude-plugins.md` — SKILL.md frontmatter declares `allowed-tools: Read Write Edit Grep Bash Agent` as a space-separated string scalar, distinct from the YAML-array form and the comma-separated form. Whether the runtime parses space-separated tokens as a tool list is unverified. Distinct from existing `allowed-tools` paths (permission-rule syntax / plain tool names / YAML array / mixed) which document other shapes — space-separated scalar form is observed but unmapped.

- `Skill authoring conventions` > `Body-line `ultrathink` directive (not frontmatter)` — `anthril--official-claude-plugins.md` — `ultrathink` appears as a standalone body line in some SKILL.md files (campaign-audit, dead-code-audit) rather than a frontmatter key, while sibling skills omit it entirely. Inconsistent placement convention within one marketplace.

- `Plugin-component registration` > `Skill-side sub-agent dispatch via `context: fork` + `agent:`` — `anthril--official-claude-plugins.md` — A skill's frontmatter declares both `context: fork` and `agent: <name>` to enter an isolated sub-agent context defined by the sibling `agents/<name>.md` file. Cross-references existing `context: fork invocation hint` under `Skill authoring conventions`, but the pairing of `context: fork` with `agent:` (where `agent:` names a sibling file) is the dispatch mechanism. May fit under existing path with description sharpening.

- `Tool-use enforcement` > `One-shot session flag-file marker for first-of-session check` — `anthril--official-claude-plugins.md` — `npm-package-audit/hooks/scripts/check-npm.sh` writes `/tmp/.npm-package-audit-check-done` to gate a runtime-prerequisite check to first invocation per session. Flag is never cleared, so mid-session changes (e.g., user installs npm) are not re-detected, and the global `/tmp/` path collides on multi-user systems. Distinct mechanism from the existing `PostToolUse Bash-matcher one-shot skill nudge` — that one is a nudge per Bash invocation; this one is a once-per-session prerequisite gate.

- `Tool-use enforcement` > `Hard-block PreToolUse on missing required text in Write payload` — `anthril--official-claude-plugins.md` — `skill-creator/hooks/scripts/pre-write-skill.sh` blocks SKILL.md `Write` operations missing `$ARGUMENTS` via `exit 2` and stderr error. Body of the script also fails-open if `jq` is not installed (graceful degradation on missing system tool). Distinct from the existing `Fact-forcing first-edit gate` (which is per-file first-edit) — this is per-write content validation. Possibly fits under existing `PreToolUse Edit/Write path validator` with description sharpening; the path validator described there checks paths, not content.

- `Documentation surface` > `Skill-count and line-count banner from welcome.sh on every SessionStart` — `anthril--official-claude-plugins.md` — Multiple plugins (`data-analysis`, `business-economics`, `knowledge-engineering`, `plan-completion-audit`, `skill-creator`) ship a `welcome.sh` SessionStart hook that emits a `systemMessage` JSON banner with skill count and line-count warnings. With no SessionStart matcher, the banner re-emits on every clear/compact, not just startup. May fit under existing `SessionStart welcome banner via systemMessage` with sharpening on the no-matcher repeat behavior.

- `Plugin-to-plugin coordination` > `Intra-plugin skill DAG navigation via Stop-hook tail-grep` — `anthril--official-claude-plugins.md` — `ppc-manager/hooks/scripts/suggest-next-skill.sh` tails `$CLAUDE_TRANSCRIPT` last 200 lines, matches the most recent skill name, and emits a `systemMessage` recommending the next skill in the encoded skill DAG. Cross-references existing `Skill chaining via Stop-hook tail-grep` — this is the same mechanism. Worth confirming the existing path's description covers the intra-plugin DAG specifically.

- `Documentation surface` > `Per-skill LICENSE.txt mixing repo and skill licenses` — `anthril--official-claude-plugins.md` — Repo-level code is MIT (root `LICENSE`); per-skill content under `skills/<name>/` ships its own `LICENSE.txt` (Apache 2.0). May fit under existing `Layered: repo-MIT, plugin-MIT, per-skill-Apache-2.0` license declaration. Same pattern observed.

- `Pre-commit and pre-push hooks (git)` > `Conftest sys.path shim instead of pyproject.toml config` — `anthril--official-claude-plugins.md` — pytest configuration lives in `conftest.py` (which inserts `scripts/` onto `sys.path`) instead of `[tool.pytest.ini_options]`. The Makefile + conftest.py together are the configuration. Possibly fits under `pytest with sys.path manipulation`; this entry is a stricter case where there's no pytest config file at all.

- `Marketplace validation` > `Lossy-aggregator field preservation policy` — `anthropics--claude-plugins-community.md` — Aggregator preserves only 5 fields per plugin entry (`name`, `description`, `source`, `homepage`, `category`); upstream `version`, `author`, `license`, `dependencies`, `tags`, `keywords`, `strict`, `skills` are dropped at the mirror layer and resurface only after install. Cross-references existing `Pure external aggregator manifest` under `Marketplace manifest layout` (which mentions the field-survival surface) but a dedicated path under validation may help — the validator/aggregator does not reject these fields, it discards them.

- `Plugin source binding` > `Single string relative source as defect signal in aggregator` — `anthropics--claude-plugins-community.md` — Among 1636 mirrored entries, one carries `"source": "./cowork-plugin-management"` pointing at a directory not in the repo. The stale relative source is undetectable to the aggregator's CI (no validation runs on the mirror). Distinct from existing `Relative source pointing to subdirectory` — there the directory exists; this is a defect signal where the directory does not.

- `Plugin source binding` > `Bare `owner/repo` slug vs full URL inconsistency in `git-subdir`` — `anthropics--claude-plugins-community.md` — Among 174 `git-subdir` entries, 165 use a bare `owner/repo` slug for `url` and 9 use a full `https://...` URL. Both forms appear accepted by the runtime per Anthropic docs, but the mix inside one manifest is a parsing surprise. May fit under existing `git-subdir into upstream` with description sharpening — the mixed form should be called out explicitly.

- `Channel distribution` > `Sync-PR cadence with growing batch sizes` — `anthropics--claude-plugins-community.md` — Sync PRs (`sync/manual-YYYY-MM-DD`, `sync/auto-vendor`, `sync/batch-plus-197`) merge into main on a weekly batch cadence with growing batch sizes (214 → 500 → 814 → 1095 → 1636 over ~4 weeks). The cadence is the release surface; no tags, no version bumps. Cross-references existing `Sync-PR cadence with no tags` under `Tag and release lifecycle`, possibly with a sharpening on the growing-batch detail.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Marketplace manifest layout` > `Pure external aggregator manifest` — existing description names url/git-subdir/github but does not mention that an unguarded relative `./<name>` source can slip through validation when the aggregator has no validator wired in. Supporting sample: `anthropics--claude-plugins-community.md` (the `./cowork-plugin-management` defect entry). Sharpening: append a note that pure aggregators routinely have no manifest validation in CI, so relative-source entries pointing at non-existent directories are not caught at merge time.

- `Skill authoring conventions` > `context: fork invocation hint` — existing description says "May coexist with `agent: <name>` to drop into an isolated sub-agent context"; this is verbatim what `anthril` exhibits. Sharpening: the existing description already covers this, so the anthril sample maps cleanly. Confirming alignment, not requesting a change.

- `Tool-use enforcement` > `PostToolUse Bash-matcher one-shot skill nudge` — existing description focuses on a per-Bash-call nudge with skill suggestion. The anthril `npm-package-audit` `/tmp/`-based one-shot prerequisite check is a different mechanism (PreToolUse, not PostToolUse, and gates on prerequisite presence not skill suggestion). Sharpening: a separate path is more correct than sharpening this one — see proposed new path above.

- `Channel distribution` > `Single channel — tag-on-main with git-ref pinning` — existing description covers tag-on-main pinning generally; affaan-m's case adds the wrinkle that even with 162k stars and high PR velocity, no `release/*` staging branch exists between dev and release. Sharpening: optionally add a note that high-velocity repos sometimes still skip a staging-branch model and rely entirely on tag cadence as the stabilization layer.

- `Plugin-runtime root resolution` > `Centralized inline-bootstrap dispatcher` — existing description references the affaan-m pattern directly and is well-mapped. Sharpening: confirming alignment, not requesting a change. The 1.5KB inline `node -e` boilerplate, the six-fallback-chain (env var → `~/.claude` → six well-known plugin slug paths → versioned cache dirs), and SessionStart's `!`-character bash-history-expansion fragility are all already captured.

- `Marketplace validation` > `Multi-validator composition` — existing description references the affaan-m sample directly with all three novel validators (workflow-security, install-manifests, unicode-safety) named. Sharpening: confirming alignment, not requesting a change. The 10-validator chain, `continue-on-error: false`, and the per-component-type scope are well captured.

- `Marketplace validation` > `Reverse-engineered validator notes as primary-source artifact` — existing description references affaan-m's `PLUGIN_SCHEMA_NOTES.md` directly. Sharpening: confirming alignment.

- `Release automation` > `Tag-triggered release with multi-gate sanity (npm)` — existing description references affaan-m's release.yml directly (three gates, tag format regex, plugin-manifest.test.js, npm publish idempotency, GitHub release with body_path + generate_release_notes). Sharpening: confirming alignment.

- `Cross-ecosystem distribution` > `Cross-ecosystem multi-harness distribution` — existing description references affaan-m's pattern (parallel manifests for Codex, OpenCode, Cursor, Gemini, version-locked via release script, validate-install-manifests.js cross-validation). Sharpening: confirming alignment.

- `Cross-ecosystem distribution` > `Dual-distribution: marketplace + npm` — existing description references affaan-m's `ecc-universal` npm package directly. Sharpening: confirming alignment.

- `Documentation surface` > `Multi-document agent-context layer` — existing description lists the 14+ markdown files and locale variants directly from affaan-m. Sharpening: confirming alignment.

- `Marketplace manifest layout` > `Top-level metadata wrapper variants` — existing description covers the four shape variants. Anthril's manifest is the "Flat top-level fields only" variant: top-level `name`, `description`, `owner.{name, email}`, `plugins`, `$schema` only — no `metadata` wrapper, no `metadata.pluginRoot`, no `version`. Sharpening: confirming alignment with the flat top-level fields shape.

- `Marketplace validation` > `JSON-parse plus version-sync only` — existing description references anthril's `validate-marketplace.yml` directly (`node -e "JSON.parse(...)"` + `check-versions.mjs`). Sharpening: confirming alignment.

- `Bin entry mechanism` > `Pointer-file shim invoked via `.mcp.json`` — existing description references anthril's ppc-manager directly: `bin/python_shim.sh` + `bin/python_shim.ps1`, reads `${CLAUDE_PLUGIN_DATA}/python_path.txt`, exec the pointed Python interpreter, .mcp.json invokes via `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh`. Even covers the PowerShell sibling not being wired through .mcp.json. Sharpening: confirming alignment.

- `Dependency installation` > `SessionStart-driven Python venv with hash gating` — existing description covers anthril's `ensure-venv.sh`/`ensure-venv.ps1`, ~180s timeout, requirements.stamp/sha256 hash, JSON systemMessage on failure, `install.log` redirection. Sharpening: confirming alignment.

- `Locale and content-style enforcement` > `Australian English mandate with lint check` — existing description references anthril's CLAUDE.md mandate and `tests/lint/test_australian_english.py`. Sharpening: confirming alignment.

- `Tag and release lifecycle` > `Single lifetime tag with drift` — existing description covers anthril's pattern (single `v1.0.0` tag while plugins ship 1.0.1/1.1.0). Sharpening: confirming alignment.

- `Channel distribution` > `Sync-PR cadence with no tags` — existing description references anthropics's pattern directly (`sync/manual-YYYY-MM-DD`, `sync/auto-vendor`, growing batch sizes 214→500→814→1095→1636). Sharpening: confirming alignment.

- `Tag and release lifecycle` > `No tags at all` — existing description covers anthropics's pattern (zero tags ever; chore: sync chain; aggregator has no independent release identity). Sharpening: confirming alignment.

- `CI workflow shape` > `Single PR-gatekeeper workflow` — existing description references anthropics's `close-external-prs.yml` directly. Sharpening: confirming alignment.

- `CI workflow shape` > `Organizational PR bouncer` — existing description references the same `close-external-prs.yml` mechanism. Sharpening: confirming alignment.

- `Documentation surface` > `Minimal consumer-facing README only` — existing description references anthropics's pattern (~1.4 KB README, anti-contribution route). Sharpening: confirming alignment.

- `Community health files` > `Anti-contribution with auto-close gatekeeper` — existing description covers anthropics's permission-check + auto-close + redirect-comment pattern. Sharpening: confirming alignment.

- `Per-plugin discoverability metadata` > `Description-only with sparse opt-in category` — existing description references "≈3% in one mirror" with capitalization inconsistency (`development` vs `Developer Tools`). That maps anthropics directly (45/1636 = 2.75%, multiple capitalization variants). Sharpening: confirming alignment.

- `Plugin source binding` > `git-subdir into upstream` — existing description mentions the bare-slug-vs-https inconsistency in passing ("`url` is mixed in practice — bare `owner/repo` slug or full `https://`"). Sharpening: confirming alignment; the existing description is sufficient.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — every fact in the three samples mapped to an existing role, with the proposed new paths being intra-role refinements.)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none — no existing path needed splitting based on this bin's evidence.)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- The affaan-m `package.json.files:` list shipping the entire plugin payload as an npm package is captured in `Cross-ecosystem distribution > Dual-distribution: marketplace + npm`. Whether this is also a distinct *Distribution exclusion* concern (since `.claudeignore` doesn't filter npm publish surface either) is a borderline call; it sits cleanly under cross-ecosystem distribution rather than splitting across two roles.

- The anthril gap between *intent* (CLAUDE.md says `userConfig` should be present, `test_manifests.py` asserts it) and *reality* (the 10 plugin.json files have only name/version/description/author) is documentation drift, not a separate role. It maps under `User configuration > userConfig declared but not wired through manifest substitution` for the inverse case (declared but unwired), but here the case is *not declared* despite being asserted. Whether to surface this drift specifically depends on how thoroughly the consolidated tracks "documented intent that the file does not realize." The anthril sample documents this as the single biggest observed defect; flagging here in case the reconciler wants to add a path like `userConfig asserted by tests but missing from manifest`.

- The anthropics sample's *intentional* lack of validation (the "internal review pipeline" handles it before merge) is captured under `Marketplace validation > No validation` and under the relevant cross-aggregator notes. The pattern that the public-facing marketplace has no recovery path if the internal pipeline misses something is mentioned in the existing `No validation` description. Confirming alignment.

- The affaan-m repo declares three reusable workflows (`reusable-test.yml`, `reusable-release.yml`, `reusable-validate.yml`) that exist but are not consumed by the primary workflows (`ci.yml`, `release.yml`) — the workflow bodies are duplicated and have already drifted (`REF_NAME` vs `inputs.tag`). This is a concrete anti-pattern mid-migration. Could fit under `CI workflow shape` as a new path (`Reusable workflows declared but not consumed`) but feels narrow; surfacing here in case the reconciler decides it warrants a path or a more general "in-progress migration creates drift surfaces" note.
