# Marketplace Repos — Research Index

Per-repo structured findings captured during deep-research verification of the claude-marketplace pattern doc (`logs/research/claude-marketplace/consolidated.md`). Each file fills [_TEMPLATE.md](_TEMPLATE.md) — a purpose-oriented structure mirroring the pattern doc's 16 purpose sections, plus identification, novel-axes, and gaps.

These are the empirical source data for pattern-doc verification. A repo's presence here is a claim that its structure was directly inspected; the per-file content records what was observed. Gaps sections record what was not resolvable within the inspection budget.

Sample size: **54 unique repos** across three overlapping samples. Built in one deep-research pass after initial three-wave shallow survey (tasks 14/15/22) raised integrity concerns about pattern-doc adoption counts — particularly ★ annotations on paths that turned out to be docs-available but community-unadopted.

## How to use

- Point a reader at the per-repo file to see structural detail for that repo.
- Aggregation of adoption counts happens against these files, not against the shallower research in tasks 14/15/22.
- When using a specific fact from a repo (e.g., stars, last-commit, version), verify against GitHub first — quick-capture metadata may be approximate.
- Context resources ([../context-resources/](../context-resources/)) answer schema / docs-prescription questions; per-repo files record what each repo *did*.

## Sample composition

### Primary sample (18) — authoritative for most purposes

**Anthropic-owned (6):**

- [anthropics--claude-plugins-official](anthropics--claude-plugins-official.md) — official curated catalog; url+sha aggregator
- [anthropics--claude-plugins-community](anthropics--claude-plugins-community.md) — community catalog; mixed url+sha and git-subdir+ref
- [anthropics--knowledge-work-plugins](anthropics--knowledge-work-plugins.md) — relative sources; nested partner marketplace
- [anthropics--financial-services-plugins](anthropics--financial-services-plugins.md) — relative sources
- [anthropics--life-sciences](anthropics--life-sciences.md) — relative sources; strict: false skill carving
- [anthropics--healthcare](anthropics--healthcare.md) — relative sources; strict: false skill carving

**Community (12):**

- [AgentBuildersApp--eight-eyes](AgentBuildersApp--eight-eyes.md)
- [BULDEE--ai-craftsman-superpowers](BULDEE--ai-craftsman-superpowers.md) — 30 semver tags; 14-event hooks config
- [BaseInfinity--sdlc-wizard](BaseInfinity--sdlc-wizard.md) — 8 workflows; deep-gated release.yml
- [Chachamaru127--claude-code-harness](Chachamaru127--claude-code-harness.md) — only repo using release/* branches
- [CodeAlive-AI--codealive-skills](CodeAlive-AI--codealive-skills.md) — pytest with coverage; SHA-pinned actions
- [CronusL-1141--AI-company](CronusL-1141--AI-company.md) — master default; 12-event hooks (in primary + dep-management)
- [Kanevry--session-orchestrator](Kanevry--session-orchestrator.md) — pre-release tag suffixes; fail-closed enforcement pattern
- [Vortiago--mcp-outline](Vortiago--mcp-outline.md) — most sophisticated release pipeline (OIDC PyPI + MCP registry)
- [affaan-m--everything-claude-code](affaan-m--everything-claude-code.md) — reusable workflows; per-plugin nested tests
- [IgorGanapolsky--ThumbGate](IgorGanapolsky--ThumbGate.md) — npm source type (outlier); 36 workflows
- [REPOZY--superpowers-optimized](REPOZY--superpowers-optimized.md) — only repo with dev branch; SessionStart sub-event matchers
- [HiH-DimaN--idea-to-deploy](HiH-DimaN--idea-to-deploy.md) — github source type; uses $schema

### Dependency-management sample (19 new beyond primary) — authoritative for purpose 6

- [anthril--official-claude-plugins](anthril--official-claude-plugins.md) — Python venv, stamp file + diff -q; pointer-file bin pattern
- [Arcanon-hub--arcanon](Arcanon-hub--arcanon.md) — Node/npm, sentinel diff -q; installs into ROOT (ESM)
- [ekadetov--llm-wiki](ekadetov--llm-wiki.md) — Node/npm, version file + diff -q
- [marioGusmao--mg-plugins](marioGusmao--mg-plugins.md) — Node/npm, diff -q + Node ABI tracking
- [thecodeartificerX--codetographer](thecodeartificerX--codetographer.md) — Node/npm, copy-then-install
- [tretuttle--AI-Stuff](tretuttle--AI-Stuff.md) — Node + Playwright Chromium, sha256 + install marker
- [NoelClay--academic-research-mcp-plugin](NoelClay--academic-research-mcp-plugin.md) — Python venv + Node, diff -q both
- [123jimin-vibe--plugin-prompt-engineer](123jimin-vibe--plugin-prompt-engineer.md) — Python venv, version file
- [includeHasan--prospect-studio](includeHasan--prospect-studio.md) — Node/npm, sha256; installs into ROOT (ESM)
- [damionrashford--trader-os](damionrashford--trader-os.md) — Node via bun/npm; monitors reference; PEP 723
- [Chulf58--FORGE](Chulf58--FORGE.md) — Node, mtime vs lockfile; installs into ROOT
- [smcady--Cairn](smcady--Cairn.md) — Python venv, diff -q + plugin-root movement + venv existence
- [JordanCoin--pdf-to-text](JordanCoin--pdf-to-text.md) — WASM binary download, version file
- [ZhuBit--cowork-semantic-search](ZhuBit--cowork-semantic-search.md) — Python venv, sha256
- [raphaelchristi--harness-evolver](raphaelchristi--harness-evolver.md) — Python venv, existence-only
- [brunoborges--ghx](brunoborges--ghx.md) — Go binaries into DATA, existence-only
- [jxw1102--flipper-claude-buddy](jxw1102--flipper-claude-buddy.md) — Python venv, md5 hash
- [BrandCast-Signage--root](BrandCast-Signage--root.md) — Node/npm mixed: third-party `~/.root-framework` + plugin's own into DATA
- [Lykhoyda--rn-dev-agent](Lykhoyda--rn-dev-agent.md) — Node/npm into DATA + symlink back to ROOT

### Bin-wrapper sub-sample (17 new beyond above) — authoritative for purpose 7

- [SkinnnyJay--wiki-llm](SkinnnyJay--wiki-llm.md)
- [mdproctor--cc-praxis](mdproctor--cc-praxis.md)
- [ChanMeng666--claude-code-audio-hooks](ChanMeng666--claude-code-audio-hooks.md)
- [Emasoft--token-reporter-plugin](Emasoft--token-reporter-plugin.md)
- [K-dash--typemux-cc](K-dash--typemux-cc.md)
- [heliohq--ship](heliohq--ship.md)
- [iVintik--codeharness](iVintik--codeharness.md)
- [hwuiwon--autotune](hwuiwon--autotune.md)
- [stellarlinkco--myclaude](stellarlinkco--myclaude.md)
- [ShaheerKhawaja--ProductionOS](ShaheerKhawaja--ProductionOS.md)
- [a3lem--my-claude-plugins](a3lem--my-claude-plugins.md)
- [777genius--claude-notifications-go](777genius--claude-notifications-go.md)
- [robertnowell--marketing-pipeline](robertnowell--marketing-pipeline.md)
- [SankaiAI--ats-optimized-resume-agent-skill](SankaiAI--ats-optimized-resume-agent-skill.md)
- [jmylchreest--aide](jmylchreest--aide.md)
- [lukasmalkmus--moneymoney](lukasmalkmus--moneymoney.md)
- [skullninja--coco-workflow](skullninja--coco-workflow.md)

## Cross-sample themes

Aggregation of all 54 per-repo research files, organized by purpose. "Primary" = 18-repo primary sample. "Dep-mgmt" = 20-repo dep-management sample (CronusL-1141 appears in both primary and dep-mgmt). "Bin-wrap" = 23-repo bin-wrapper sub-sample (anthril, damionrashford, brunoborges, Lykhoyda, JordanCoin, Chulf58 also in dep-mgmt).

### Purpose 1 — Marketplace discoverability

**Adoption matrix (all repos, N=54 minus 2 aggregator-only that don't register categories):**

| Path | Observed count | Representative repos |
|---|---|---|
| Single `.claude-plugin/marketplace.json` at repo root | ~50/54 | Most repos |
| Multiple `marketplace.json` files at different paths | 4/54 | AgentBuildersApp (+`.github/plugin/`), CronusL-1141 (+nested `plugin/`), anthropics/knowledge-work-plugins (+nested `partner-built/brand-voice/`), brunoborges (dual `.claude-plugin/` + `.github/plugin/`) |
| No marketplace.json (plugin-only repo) | 4/54 | thecodeartificerX, NoelClay, 123jimin-vibe, Emasoft, ZhuBit (count varies; ~5/54 if included) |

**Marketplace-level metadata (N=50 with marketplace.json):**

| Path | Count | Notable |
|---|---|---|
| `metadata: {…}` wrapper | ~22/50 | Most Anthropic (healthcare, life-sciences), BULDEE, CodeAlive, Kanevry, 777genius, hwuiwon, damionrashford, lukasmalkmus, Chulf58 |
| Top-level `description` (no wrapper) | ~15/50 | anthropics/claude-plugins-official, anthropics/claude-plugins-community, anthropics/knowledge-work-plugins, anthropics/financial-services-plugins, Vortiago, raphaelchristi, ship, prospect-studio |
| No marketplace-level description | ~13/50 | smcady, ekadetov, includeHasan (no metadata), robertnowell (top-level desc but no wrapper), a3lem-style minimal cases |

**`metadata.pluginRoot`:** 0/54 adopt. (knowledge-work-plugins' nested brand-voice marketplace uses `pluginRoot: "."` — that's nested, not root; still 0 in the primary manifest.)

**Per-plugin discoverability (N=54):**

| Path | Count |
|---|---|
| `category` only (on marketplace entry) | ~10/54 |
| `category + tags` | ~9/54 |
| `keywords` only (in plugin.json) | ~14/54 |
| `category + keywords` | ~6/54 |
| `category + tags + keywords` | ~8/54 |
| No discoverability metadata at all | ~7/54 |

**`$schema` reference:** 6/54 adopt — anthropics/claude-plugins-official, HiH-DimaN/idea-to-deploy, hwuiwon/autotune, Chulf58/FORGE (unclear), ShaheerKhawaja/ProductionOS (absent per research but close to), a3lem/my-claude-plugins, jmylchreest/aide, lukasmalkmus/moneymoney absent. Still a minority — ~11%.

**Docs alignment:** docs-silent on count; allow all three of `category`, `tags`, `keywords` as optional plugin entry fields. No path is ★ or ☆.

**Corrections to pattern doc:** Pattern doc says `category + tags` is ~5/21 and `keywords only` is ~7/21 — those numbers were from the earlier 21-sample; extended to 54, proportions are similar but absolute counts now read differently. Pattern doc's `$schema` adopter count of "2/21" is under-counted; actual is ~6/54 (~11%) including HiH-DimaN, hwuiwon/autotune, lukasmalkmus/moneymoney, and others. The "`tags: community-managed` emerging convention" observation holds — 777genius and HiH-DimaN both use provenance-flavored tag values.

**Notable outliers:**
- AgentBuildersApp ships duplicate manifests at `.claude-plugin/marketplace.json` AND `.github/plugin/marketplace.json` — intentional for Copilot CLI parallel discovery.
- anthropics/knowledge-work-plugins ships a nested marketplace.json inside `partner-built/brand-voice/` — dual-addressable plugin (inline in the aggregator AND self-contained upstream).
- thecodeartificerX, NoelClay, ZhuBit are "plugin-only repos with no marketplace manifest" — meant to be referenced from an external marketplace.

**Pitfalls observed across the sample:**
- Placeholder `owner.email: "your-email@example.com"` (SankaiAI) — missed fill-in before publish.
- Marketplace-entry description duplicated from plugin.json with no sync mechanism — drift risk across ~15+ repos.
- Reserved-name collisions: 0/54 observed (all authors avoided the blocklist).
- `keywords` in plugin.json vs `tags` on marketplace entry: same semantic used twice, often overlapping (autotune, 777genius, CodeAlive, SkinnnyJay, BULDEE — widespread duplication).

### Purpose 2 — Plugin source binding

**Source format (N=54, only counting repos with a marketplace manifest, ~50):**

| Path | Count | Repos |
|---|---|---|
| Relative string (`"./dir"` or `"./"`) | ~40/50 | Overwhelmingly dominant |
| `url` + `sha` | 4/50 | anthropics/claude-plugins-official (72 entries mix), anthropics/claude-plugins-community (1461 entries), knowledge-work-plugins (18), Chulf58/FORGE (1 — self-url) |
| `git-subdir` | 3/50 | anthropics/claude-plugins-official (24 entries), anthropics/claude-plugins-community (174), knowledge-work-plugins (2), jxw1102/flipper-claude-buddy (1) |
| `github` object | 2/50 | HiH-DimaN/idea-to-deploy, brunoborges/ghx (via aggregator `agent-plugins`), anthropics/claude-plugins-official (1 — stagehand), SankaiAI |
| `npm` object | 1/50 | IgorGanapolsky/ThumbGate |

**`strict` field (N=54):**

| Path | Count | Notable |
|---|---|---|
| Default implicit true (no field) | ~44/54 | Dominant |
| `strict: false` explicit | ~8/54 | anthropics/healthcare (3 skill-carving entries), life-sciences (5), claude-plugins-official (14 — all LSP plugins + 2 others), CodeAlive, damionrashford (false), affaan-m (false), ShaheerKhawaja (false), ChanMeng666 (absent but should be) |
| `strict: true` explicit | ~2/54 | Chachamaru127 |

**Version authority (N=54):**

| Path | Count |
|---|---|
| `plugin.json` only | ~22/54 |
| Marketplace entry only | ~5/54 |
| Both (drift risk, version duplicated) | ~20/54 |
| Neither (no version anywhere) | ~7/54 |

**Docs alignment:** docs prescribe "for relative sources, set version in marketplace entry; for all other sources, set version in plugin.json." Reality: ~20/54 write version to BOTH regardless of source. This pattern-doc conflict holds.

**Corrections to pattern doc:**
- Pattern doc's "relative string 14/18" holds. Extended to 54: overwhelmingly dominant (~40/50).
- Pattern doc records "Both (duplicated) 1/14 observed drift" — extending to 54, version-duplication drift is NOT rare. Multiple repos show live drift at the time of research: AgentBuildersApp (4.2.0 marketplace vs 5.0.0-alpha plugin.json), anthril (missing versions in marketplace entries), Arcanon-hub, marioGusmao (router-plugin 0.1.0 vs 1.0.8), ShaheerKhawaja (five-way drift), Chulf58 (marketplace 1.0.0 vs plugin 0.5.1), raphaelchristi (marketplace 6.1.0 vs plugin 6.4.2), stellarlinkco (5.6.1 vs 6.7.0 vs tag v6.8.2). **Drift is the norm, not the exception, when both locations carry the field.**

**Notable outliers:**
- IgorGanapolsky/ThumbGate — only `npm` source observed.
- HiH-DimaN/idea-to-deploy — pure `github` object.
- Chulf58/FORGE — `url` source pointing at its own repo (self-hosting via URL rather than relative path).

**Pitfalls observed across the sample:**
- Multi-location version drift is the modal failure (at least 9 repos observed with live drift at research time).
- `strict: false` used without `skills` override (CodeAlive) — appears vestigial/hedging.
- `source: "."` vs `"./"` — some validators (includeHasan observed in commit history) reject bare `"."`.

### Purpose 3 — Channel distribution

**Channel mechanism (N=54):**

| Path | Count |
|---|---|
| No split — users pin via `@ref` | 54/54 |
| Docs-prescribed two-marketplace pattern | 0/54 |

**Corrections to pattern doc:** Pattern doc says "0/18 implement the docs stable/latest pattern; all 18 use `@ref` pinning." Extended to 54: still **0/54**. The docs-vs-adoption conflict is preserved and amplified across a larger sample.

**Notable outliers / alternative patterns observed:**
- Kanevry/session-orchestrator has pre-release tag suffixes (`-alpha`, `-beta`, `-rc`) on main — closest thing to channel discipline via semver suffixes.
- Chachamaru127 has `release/*-arcana` branches but tags live on main (branches behind main, not channels).
- Vortiago/mcp-outline uses `-rc` semver to route TestPyPI vs PyPI publish — closest to docs pattern, but PyPI-level not marketplace-level.
- BaseInfinity has `release-please`-style `release.yml` gating verify-tag-on-main + verify-tag=package.version — rigorous but still single-channel.
- 777genius maintains a floating `snapshot` release tag (rewritten on every main push) + versioned releases — effectively two channels via asset URLs but through GitHub Releases, not marketplace manifests.

**Pitfalls observed across the sample:** every author bypasses the docs pattern because plugin-name collisions between channels (each plugin.json has same `name` unless authors ship separate plugin files) make the docs pattern awkward.

### Purpose 4 — Version control and release cadence

**Default branch (N=54):**

| Path | Count |
|---|---|
| `main` | ~48/54 |
| `master` | 6/54 — CronusL-1141, ChanMeng666, tretuttle/AI-Stuff, stellarlinkco/myclaude, iVintik/codeharness, Emasoft (one of them; spot-check) |

**Tag placement (N=54, excluding aggregators and no-tag repos):**

| Path | Count |
|---|---|
| Tags on main/master | ~30/54 |
| Tags on release branches | 1/54 — Chachamaru127 (release-codename branches behind main; tags still on main per detailed research — so truly tags on main) |
| No tags at all | ~20/54 |

**Release branching (N=54):**

| Path | Count |
|---|---|
| Tag-on-main, no release branches | ~50/54 |
| Dedicated `release/*` long-lived branches | 1/54 — Chachamaru127 (but branches behind main; tags on main) |
| Short-lived `release/*` for PR validation | 1/54 — HiH-DimaN |

**Pre-release suffixes (N=54 that tag):**

| Path | Count |
|---|---|
| Plain semver only | ~25/34 |
| `-alpha`/`-beta`/`-rc` observed | ~6/34 — AgentBuildersApp (alpha), Kanevry (alpha/beta/rc), 777genius ("snapshot"-like), ShaheerKhawaja (beta) |
| Non-SemVer conventions (`-SNAPSHOT`, `-dev`, etc.) | mdproctor (-SNAPSHOT), jmylchreest (-dev for non-release binary stamps) |

**Dev-counter scheme (like this repo's `0.0.z`):**
- Absent in all 54 repos.
- This repo (`claude-plugins`) is the only known adopter of that discipline; no sampled repo mirrors it.

**Pre-commit version bump:**
- Chachamaru127 — git hook enforcing `VERSION`/`plugin.json` sync (not auto-bump, drift-detect).
- Emasoft — ancestry-verified pre-push gate (`scripts/pre-push` rejects main pushes unless `scripts/publish.py` is an ancestor process).
- affaan-m, Lykhoyda, ThumbGate — pre-commit-style sync-version scripts.
- 777genius — no bump automation but `install-hooks.sh` via `"prepare"`.
- BULDEE — manual `scripts/bump-version.sh` touching 6 files.

**Corrections to pattern doc:** Pattern doc says `main` 16/18 and `master` 2/18. Extended to 54: `main` ~48/54 (89%), `master` 6/54 (11%) — same ratio. Confirmed.

**Pitfalls observed across the sample:**
- Tags trail `plugin.json` version (autotune v0.3.0 plugin.json but only v0.1.0 tag; ShaheerKhawaja's five-way version drift).
- CI tests run on push-to-main but cycle-commit bot workflows (robertnowell) burn CI minutes needlessly.
- Most repos ship with zero tag-sanity gate between `plugin.json.version` and the tag.

### Purpose 5 — Plugin-component registration

**Reference style (N=54):**

| Path | Count |
|---|---|
| Default directory discovery (minimal plugin.json) | ~35/54 |
| Explicit path arrays (e.g., `"skills": "./skills/"`) | ~12/54 |
| Inline config objects (`mcpServers: {…}`) | ~8/54 |
| External file reference (e.g., `mcpServers: "./.mcp.json"`) | ~3/54 — includeHasan (`.mcp.json` at root not plugin), CronusL-1141, mg-plugins (codegraph) |
| Mixed (some inline, some file-ref) | ~4/54 |

**Agent frontmatter fields observed across sample:** `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`, `color`, `subagent_type`, `stakes`, `permissionMode`, `allowed-prompts`.

**Agent tools syntax (N=54 with agents):**

| Path | Count |
|---|---|
| Plain tool names (comma-separated string or YAML list) | ~32/35 |
| Permission-rule syntax (e.g., `Bash(uv run *)`) | 2/35 — damionrashford/trader-os, skullninja/coco-workflow (in skill allowed-tools) |
| Mixed | ~1/35 — Arcanon-hub (neither, it has no agents) |

**Non-standard frontmatter observed:**
- `isolation: worktree` — AgentBuildersApp, BULDEE, REPOZY, damionrashford, NoelClay, Lykhoyda, skullninja. Multiple.
- `memory: project` / `memory: user` — BULDEE, Chachamaru127, damionrashford, Lykhoyda.
- `background: true` — AgentBuildersApp, damionrashford.
- `effort: high/xhigh` — Chachamaru127 (xhigh — CC 2.1.111+), BULDEE, damionrashford, HiH-DimaN.
- `stakes: low/medium/high` — ShaheerKhawaja (borrowed from HumanLayer).
- `subagent_type: <plugin>:<name>` — ShaheerKhawaja.
- `user-invocable: false` — knowledge-work-plugins/productivity (Cowork-specific).
- `context: fork` — HiH-DimaN/idea-to-deploy's `/autopilot` skill, anthril's campaign-audit skill.
- `permissionMode: acceptEdits` — raphaelchristi (proposer agent).
- `disable-model-invocation: true` — HiH-DimaN (on /deploy, /migrate, /autopilot).

**Corrections to pattern doc:** Pattern doc says "Default discovery 12/21, Inline 2/21, External file 1/21, Explicit 1/21." Extended to 54, default discovery is still dominant (~35/54 ~65%), but explicit-path arrays are more common than the original count suggests (~12/54 ~22%). Pattern-doc counts should be updated.

**Pitfalls observed across the sample:**
- Mixed Claude/Cursor/Codex plugin manifests coexist in the same repo (REPOZY, ship, jmylchreest/aide, SkinnnyJay, stellarlinkco) — all need parallel sync.
- Leftover scaffolding (`hooks/hooks.json` empty, `commands/.gitkeep`) — financial-services-plugins (empty hooks across 5 plugins), damionrashford.

### Purpose 6 — Dependency installation

**Install location (N=20 dep-management):**

| Path | Count | Repos |
|---|---|---|
| `${CLAUDE_PLUGIN_DATA}` | ~12/20 | anthril, tretuttle, 123jimin-vibe, smcady, ZhuBit, NoelClay, jxw1102, Cairn, Lykhoyda (primary), ekadetov, brunoborges, JordanCoin |
| `${CLAUDE_PLUGIN_ROOT}` (cites ESM) | ~4/20 | Arcanon-hub, includeHasan, Chulf58, marioGusmao (codegraph has ROOT + data-dir symlink hybrid) |
| Hybrid DATA + ROOT symlink | 2/20 | Lykhoyda (DATA with symlink back to ROOT), marioGusmao/codegraph (DATA install + symlink back to ROOT) |
| Ad-hoc runtime fetch (npx/uvx) | 2/20 | damionrashford (uv run --script + channels), mcp-outline (uvx mcp-outline) |
| `${CLAUDE_PLUGIN_ROOT}` + no data | 1/20 | BrandCast-Signage/root (first-party MCP into ROOT) |
| Shared home-dir `~/.root-framework` | 1/20 | BrandCast-Signage (third-party MCP only) |
| Global-npm install | 2/20 | iVintik/codeharness (npm install -g), raphaelchristi |

**Docs alignment:** `${CLAUDE_PLUGIN_DATA}` is docs-prescribed (★ in pattern doc). Extended count still favors DATA — ~12/20 (60%). The ROOT-due-to-ESM rationale is well-documented in Arcanon-hub and prospect-studio planning docs. Not a violation — a documented alternative.

**Change detection (N=20):**

| Path | Count | Repos |
|---|---|---|
| `diff -q` | ~8/20 | anthril, Arcanon-hub, NoelClay, Cairn, damionrashford, BrandCast-Signage, codegraph, BaseInfinity (via Python yaml-load) |
| sha256 | ~4/20 | tretuttle, includeHasan, ZhuBit, ghx (install-hash via shasum) |
| md5 | 1/20 | jxw1102/flipper-claude-buddy |
| Version file stamp | ~5/20 | 123jimin-vibe, ekadetov, JordanCoin, Lykhoyda, ShaheerKhawaja |
| Existence only | ~2/20 | raphaelchristi, brunoborges, ghx (binary-only) |
| mtime vs lockfile | 1/20 | Chulf58/FORGE |
| Plugin-version-as-stamp | 2/20 | 123jimin-vibe, Lykhoyda |
| Hash over source + manifest | 1/20 | robertnowell/marketing-pipeline (hashes `pipeline/**/*.py + pyproject.toml + *.md`) |
| Content-copy equality | 1/20 | thecodeartificerX (copy-then-install ordering — order bug) |

**Retry-next-session invariant:**
- `rm` on failure — Arcanon-hub (`rm -rf node_modules + rm -f sentinel`), NoelClay (`rm $REQ_DST`), BrandCast-Signage, jxw1102 (marker).
- Write-on-success only (implicit retry via missing stamp) — anthril (cp after success), ekadetov (stamp written post-install), 123jimin-vibe, Cairn, includeHasan, tretuttle, damionrashford.
- No cleanup at all — raphaelchristi, CronusL-1141's auto-install path (swallows errors), Chulf58 (rm nodeModules on failure).
- Neither (does not retry) — raphaelchristi's existence-only path.

**Failure signaling (N=20):**

| Path | Count |
|---|---|
| Silent / `exit 0` / `\|\| true` | ~9/20 |
| stderr human-readable + exit 0 | ~8/20 |
| `set -euo pipefail` halts + stderr | ~3/20 |
| JSON `systemMessage` on stdout | 1/20 — anthril (plus CronusL auto_install.py emits additionalContext for restart notice) |
| `hookSpecificOutput.additionalContext` on success | 2/20 — CronusL (restart message), NoelClay (with persona) |

**CRITICAL CORRECTION:** Pattern doc marks "JSON `systemMessage` on stdout ★" as a docs-prescribed path. **This is wrong.** The docs-plugins-reference worked example uses silent `rm` + retry with NO JSON systemMessage (`"No JSON systemMessage output. Pattern is silent retry via the rm invariant."`). Only 1/20 sampled repos emits a JSON systemMessage on install failure (anthril). The ★ should not be on that row.

**Runtime variant:**

| Variant | Adoption | Representative repos |
|---|---|---|
| Python venv (pip) | ~8/20 | anthril, 123jimin-vibe, Cairn, ZhuBit, NoelClay, jxw1102, raphaelchristi, robertnowell |
| Python uv | 1/20 | damionrashford (PEP 723 inline) |
| Node via npm | ~9/20 | Arcanon-hub, ekadetov, marioGusmao, thecodeartificerX, Chulf58, BrandCast-Signage, Lykhoyda, tretuttle, includeHasan, NoelClay (in part) |
| Node via bun | ~1/20 | damionrashford (Node channel via bun with npm fallback) |
| Prebuilt binary download (Go/Rust/Swift) | ~4/20 | brunoborges (Go), 777genius (Go), JordanCoin (WASM), ghx, K-dash/typemux-cc (Rust), Chachamaru127 (Go — but committed in-tree) |
| Mixed (multiple languages) | ~2/20 | NoelClay (Python + Node), tretuttle (Node + Playwright Chromium) |
| Node ABI tracking | 1/20 | marioGusmao/codegraph — novel |

**Docs alignment:** `diff -q` pattern is ★ — adoption ~8/20 (40%). Not universal; sha256 and version-stamp variants are equally legitimate alternatives. Pattern doc's implicit recommendation of `diff -q` overstates its prevalence.

**Notable outliers / novel patterns:**
- **PEP 723 inline metadata** (`#!/usr/bin/env -S uv run --script`) — damionrashford/trader-os uses it across 3 plugins, totaling ~20+ scripts. Zero other repos adopt it.
- **Node ABI tracking** — marioGusmao/codegraph detects Node ABI changes (via `.node-abi` marker of `process.versions.modules`) and runs `npm rebuild <native-modules>` independently of full reinstall. Unique.
- **ESM-driven install-into-ROOT rationale** — Arcanon-hub documented the reason in `.planning/` docs (`59-CONTEXT.md`); includeHasan's `install-deps.sh` carries the same rationale inline. Both chose ROOT over DATA explicitly for Node's `import` walk-up semantics.
- **Pointer-file pattern** — anthril writes `${DATA}/python_path.txt`; `bin/python_shim.sh` reads it. Only observed instance.
- **Committed pre-built binaries** — Chachamaru127 commits 3 × 11MB Go binaries in `bin/`. Unique; no sample adopts this over hook-based download.
- **Self-generated package.json** — ekadetov writes `{"private":true}` into `${DATA}/package.json` on first run. Declares deps inline in the install script.

**Corrections to pattern doc:**
- "JSON `systemMessage` ★" row: remove ★ (see above).
- "existence-only 1/20" pitfall: actually more like 3/20 (raphaelchristi, brunoborges, ghx).
- "Node ABI tracking" deserves a named callout — it's only observed in one repo but it's a genuine novel axis.

**Pitfalls observed across the sample:**
- Silent-on-failure install hooks hide network / toolchain breakage.
- `source .venv/bin/activate` in bin wrapper (robertnowell, anthril's install-deps.sh in some paths) — anti-pattern. Direct exec preferred.
- Copy-then-install ordering (thecodeartificerX) — leaves broken cache looking fresh.
- Unauthenticated GitHub API polls for release metadata (777genius, typemux-cc, JordanCoin, stellarlinkco) — rate-limit exposed.

### Purpose 7 — Bin-wrapped CLI distribution

**Runtime resolution (N=23 bin-wrapper):**

| Path | Count | Repos |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback | ~14/23 | ChanMeng666, Emasoft, heliohq, SkinnnyJay, autotune, ProductionOS, 777genius, SankaiAI, moneymoney, aide (with AIDE_PLUGIN_ROOT priority), lukasmalkmus, jmylchreest, token-report, coco-workflow (script-rel only), audio-hooks |
| `${CLAUDE_PLUGIN_ROOT}` required, no fallback | 2-3/23 | typemux-cc, codeharness (iVintik) |
| Script-relative only | ~4-5/23 | coco-workflow (explicit zero env-var), mdproctor/cc-praxis, BULDEE (script-relative with `$(cd … && pwd)`) |
| Pointer file written by hook | 1/23 | anthril (python_shim reads python_path.txt) |
| User-PATH first, then plugin-managed | 1/23 | lukasmalkmus/moneymoney (3-tier: user → cached → download) |
| Standalone / npm-style (not Claude-native) | ~2/23 | stellarlinkco (npm CLI installer), ShaheerKhawaja (npx productionos) |
| Hybrid env-var cascade | 1/23 | ship (SHIP_PLUGIN_ROOT → CLAUDE_PLUGIN_ROOT → fallback) |

**Shebang convention:**

| Shebang | Count |
|---|---|
| `env bash` | ~14/23 |
| `/bin/bash` | ~3/23 (ChanMeng666, BULDEE, ShaheerKhawaja) |
| `env python3` | ~3/23 (a3lem/inject-rules, ChanMeng666/audio-hooks.py, Emasoft/token-report.py) |
| `env node` | ~2/23 (iVintik, SankaiAI) |
| `env bun` | 1/23 (jmylchreest/aide) |
| `env -S uv run --script` (PEP 723) | 1/23 (damionrashford, 3 files) |
| `/bin/sh` (POSIX) | 2/23 (777genius hook-wrapper, Chachamaru127 harness shim) |

**Venv handling (Python wrappers, N=~8):**
- Direct `exec "$VENV/bin/python"` — anthril (via pointer file), robertnowell (via `source activate` + exec — degenerate)
- `uv run --script` ephemeral — damionrashford
- `source .venv/bin/activate` + exec — robertnowell (anti-pattern, documented in this research)
- No venv, system python3 — SkinnnyJay, a3lem, ChanMeng666, Emasoft, mdproctor, SankaiAI (pip-install-at-first-run)
- Pointer file written by hook — anthril

**Platform support:**

| Path | Count |
|---|---|
| nix-only | ~17/23 |
| bash + `.cmd` pair | 3/23 — ChanMeng666 (audio-hooks), Chulf58 (forge-mcp-server), Emasoft (implied), SankaiAI (resume-skill) |
| bash + `.ps1` pair | 1/23 — anthril |
| OS-detecting runtime logic | 3/23 — brunoborges/ghx, 777genius (install.sh + install.bat), lukasmalkmus (Darwin-only runtime with multi-arch fallback) |
| Windows-only (.cmd-generated at SessionStart) | 1/23 — Chulf58/FORGE |

**Novel axes:**
- **Orphaned bin-wrapper** — K-dash/typemux-cc ships `bin/typemux-cc-wrapper.sh` that's never invoked (plugin.json points past it at the downloaded binary directly).
- **Absolute-path symlinks in bin/** — a3lem committed symlinks target `/Users/adriaan/Code/projects/...` (breaks on any other machine).
- **Script-relative only, deliberate** — coco-workflow. Comment: "Resolves tracker.sh relative to itself so callers don't need CLAUDE_PLUGIN_ROOT." Paired with a PreToolUse hook that hard-blocks any regression to env-var form.
- **Self-installer as bin** — ShaheerKhawaja/ProductionOS and stellarlinkco ship Node installers that bootstrap the plugin via npm.
- **User-PATH-first binary resolution** — lukasmalkmus/moneymoney prefers a user's cargo/brew install over the plugin-managed copy.
- **Bash-wrapper-over-Python with interpreter probing** — ChanMeng666/audio-hooks probes `python3 → python → py` and runs a smoke `import sys` before exec.

**Corrections to pattern doc:**
- Pattern doc says "`${CLAUDE_PLUGIN_ROOT}` with script-relative fallback 14/23" — extended research confirms this is the modal pattern.
- Pattern doc says "committed as mode 100644 (non-executable) 4/20" — audio-hooks and others confirm this; worth amplifying as a real pitfall.
- `source activate` anti-pattern is explicit in pattern doc; robertnowell is a concrete live example now documented.

**Pitfalls observed across the sample:**
- `${CLAUDE_PLUGIN_ROOT}` only set for hook/MCP subprocesses, NOT for skill-invoked bash — coco-workflow, ship, autotune, and a3lem all hit this. Workaround: bin-wrapper as discovery utility (ship: `bin/ship-plugin-root`).
- Windows git `core.symlinks=false` breaks committed symlinks — 777genius handles it explicitly via stub-detection; a3lem doesn't.
- `bin/` sometimes committed with mode 100644 (non-executable) — relies on `bash <path>` invocation; fragile.
- `python` vs `python3` on Linux — SankaiAI hardcodes `python` (brittle).

### Purpose 8 — User configuration

**`userConfig` adoption (N=54):**

| Path | Count |
|---|---|
| Present with at least one field | ~14/54 |
| Absent | ~40/54 |

Representative `userConfig` adopters: BULDEE (7 fields including `sensitive: true` for `sentry_token`), damionrashford (15-18 fields per plugin — but all `sensitive: true` missing despite "SECRET" in description), Arcanon-hub (4 fields, correct `sensitive: true` on `api_token`), NoelClay (2 fields), includeHasan (8 fields, 5 correctly `sensitive: true`), ThumbGate (no userConfig), 777genius (no), SkinnnyJay (3 fields, all `sensitive: true`), CodeAlive (no, uses OS keychain), jxw1102 (3 non-secret fields), Lykhoyda (3 fields), ChanMeng666/audio-hooks (4 fields, no `sensitive` flags), ShaheerKhawaja (no — uses `~/.productionos/config/settings.json`), anthril (declared in tests but absent in live plugin.json), Emasoft (3 non-secret numeric fields).

**`sensitive: true` correctness:**
- Correctly applied — SkinnnyJay (all 3 secret fields), BULDEE (`sentry_token` correctly, `sentry_org`/`sentry_project` correctly not flagged), includeHasan (5/8 correctly), Arcanon-hub (`api_token` correctly), NoelClay (`semantic_scholar_api_key`).
- **Anti-pattern observed** — damionrashford (7 fields with "SECRET" in description but no `sensitive: true`), ChanMeng666 (`webhook_url` could carry secrets but unmarked).

**Schema richness:** most `userConfig` adopters use typed schemas (`type`, `title`, `description`, optional `default`). Only a minority use bare `{description, sensitive}`.

**Reference in config substitution:**
- `${user_config.KEY}` substitution in `.mcp.json` env blocks — anthril, damionrashford, Arcanon-hub partial, includeHasan, BULDEE (via `CLAUDE_PLUGIN_OPTION_*`), SkinnnyJay.
- `CLAUDE_PLUGIN_OPTION_<KEY>` env var pattern — BULDEE (`agent-ddd-verifier.sh` reads `CLAUDE_PLUGIN_OPTION_agent_hooks`), damionrashford (inside hook scripts), jxw1102, includeHasan.

**Docs alignment:** docs prescribe `sensitive: true` for secrets; damionrashford's 7-field anti-pattern is the documented counter-example in pattern doc. Extended research confirms this is not isolated (ChanMeng666 and others show similar gaps).

**Corrections to pattern doc:**
- Pattern doc says "3/21 directly observed with non-trivial `userConfig`" — extended research finds ~14/54 (~26%), substantially higher than the earlier count.
- The `sensitive: true` anti-pattern is real across multiple repos, not just damionrashford.

**Pitfalls observed:**
- `userConfig` declared but never consumed — Arcanon-hub declares `api_token` etc. but no `.mcp.json` substitution wires it; worker code reads from a separate credential chain.
- Pinterest fields declared in robertnowell's `userConfig` but not bridged in SessionStart hook's env export — partial implementation defect.
- OS-keychain-via-CLI as alternative — CodeAlive uses macOS Keychain + `security`/`secret-tool`/`cmdkey` rather than `userConfig`. Deliberate: shares across agents on the machine.
- `type: "directory"` observed in includeHasan — non-default type, docs-silent on allowed types.

### Purpose 9 — Tool-use enforcement

**Hook-event adoption (N=54, with many plugins using multiple events):**

PreToolUse present: ~20/54
PostToolUse present: ~18/54
PermissionRequest/PermissionDenied: ~4/54 (CronusL-1141 has `PermissionDenied`, jxw1102 has `PermissionRequest` for Flipper hardware gating, Chachamaru127 has both, FORGE has neither)

**Failure posture:**

| Path | Count |
|---|---|
| Fail-open (exit 0 always; `\|\| true` patterns) | ~35/40 |
| Fail-closed (exit 2 + permissionDecision: deny) | ~5/40 with selective paths — Kanevry (security hooks), BULDEE (write-check hook), FORGE (bash-guard, workflow-guard), Arcanon-hub (file-guard), HiH-DimaN (check-commit-completeness) |
| Mixed per-hook with documented conventions | ~6/40 — AgentBuildersApp (per-hook failure mode in spec/enforcement.yaml: hard_gate vs recovery vs observability), Kanevry (centralized emitAllow/emitDeny helpers), Chachamaru127 (agent-hook with type: agent and Haiku prompts) |

**Output convention:**

| Path | Count |
|---|---|
| stderr human-readable + exit code | ~15/40 |
| stdout JSON (hookSpecificOutput.*) | ~15/40 |
| Both (human stderr + JSON stdout belt-and-suspenders) | ~8/40 — BULDEE (v3.4.4 bug fix), FORGE (bash-guard dual), Arcanon-hub (file-guard), Kanevry |
| Silent (no output unless issue) | ~5/40 |

**Novel patterns observed:**
- **Agent-hook (`type: agent`)** — Chachamaru127 embeds Haiku agent prompts in `hooks.json` for secret/TODO review. Rare.
- **Conditional `if:` sub-matcher** — BULDEE uses `if: "Bash(git push*)"` inside a PreToolUse `matcher: "Bash"` hook; Chachamaru127 uses `if:` allowlist on PermissionRequest for Bash commands.
- **Compensating revert on PostToolUse** — AgentBuildersApp reverts writes that escape PreToolUse via `git checkout`/delete on PostToolUse. Defense-in-depth.
- **Permission-denial classifier hook** — CronusL-1141 calls `POST /api/hooks/diagnose_denial` to classify denials into retry strategies.
- **Prompt-type PreToolUse (natural language policy)** — skullninja/coco-workflow uses `type: "prompt"` for Bash hook with ~3KB prose rule list; Claude evaluates against the list. Novel.
- **Hook schema extensions** — `PostToolUseFailure`, `SubagentStart`, `TaskCompleted`, `TaskCreated`, `Elicitation`, `TeammateIdle`, `WorktreeCreate`, `StopFailure`, `InstructionsLoaded`, `CwdChanged`, `FileChanged`, `ConfigChange` observed on Chachamaru127 (18 events), BULDEE (14), damionrashford, Emasoft (9 events), jxw1102 (15 events). Many of these are undocumented in current plugin reference docs.

**Non-`command` hook types:**

| Hook type | Count |
|---|---|
| `command` (shell) | ~52/54 with any hook |
| `agent` (Haiku-agent prompts) | 1/54 — Chachamaru127 |
| `prompt` (natural language policy) | 1/54 — coco-workflow |
| `http` | 0/54 |

**Docs alignment:** ☆ docs list four hook types (`command`, `http`, `prompt`, `agent`). Extended: 2/54 repos use non-command types. Still rare.

**Corrections to pattern doc:**
- Pattern doc says "21/21 use `command` exclusively" — extended to 54, that's 52/54. Still overwhelmingly dominant; two exceptions now known.
- BULDEE's "stderr human + stdout JSON" convention is more widespread than the pattern doc implies — it's become de-facto standard.

### Purpose 10 — Session context loading

**SessionStart used for context (emits `hookSpecificOutput.additionalContext`):**

| Use | Count | Notable repos |
|---|---|---|
| SessionStart emits context | ~18/54 | anthropics/claude-plugins-official (explanatory-output-style, learning-output-style), AgentBuildersApp (mission summary), BULDEE (session profile), damionrashford (readiness checks), Chachamaru127 (via hook agent), REPOZY (routing + release notes), Arcanon-hub (diagnostic), jmylchreest/aide, ShaheerKhawaja (banner), autotune (no, it's file-based), CronusL (plugin briefing with Chinese localization) |
| SessionStart dep-install only | ~15/54 | smcady, NoelClay, 123jimin-vibe, robertnowell, jxw1102 (daemon), ekadetov, Cairn, etc. |
| No SessionStart | ~21/54 | Most Anthropic skill/MCP-only plugins, others |

**UserPromptSubmit for context (N=54):**

| Use | Count |
|---|---|
| Emits context | ~8/54 — HiH-DimaN (3 hooks: diagnostic, pre-flight, check-skills), Cairn (memory retrieval), BULDEE (bias-detector — warning not context), CronusL (context_tracker), REPOZY (skill-activator), jmylchreest/aide (skill-injector with trigger fuzzy-match) |
| Absent | ~46/54 |

**SessionStart matcher:**

| Matcher | Count |
|---|---|
| No matcher (fires on all sub-events) | ~35/54 |
| `startup` only | 1/54 — CodeAlive |
| `startup\|clear\|compact` | 1/54 — REPOZY (only sampled repo using this specific triad) |
| `startup\|resume\|clear\|compact` | ~3/54 — AgentBuildersApp, thecodeartificerX, Chulf58 |
| `startup\|resume` | 2/54 — Chachamaru127, marioGusmao (kdoc) |
| `*` | ~4/54 — affaan-m, Lykhoyda, iVintik, ChanMeng666 (via 4-sub-event split — distinct) |

**Docs alignment:** REPOZY's `"matcher": "startup|clear|compact"` is what pattern doc uses as the reference example — confirmed.

**Corrections to pattern doc:** Pattern doc states "REPOZY is the clearest observed reference" — still accurate. Extended research shows it remains the only one using this specific matcher set.

**Pitfalls observed across the sample:**
- Bare-stdout JSON vs `hookSpecificOutput.additionalContext` wrapping — Cairn and a3lem emit `{"additionalContext": ...}` without the `hookSpecificOutput` wrapper; others wrap correctly.
- Per-session-sub-event repeated context injection (compact fires banner again) — CronusL, ShaheerKhawaja, many others.
- `CLAUDE_ENV_FILE` accumulation — robertnowell appends on every SessionStart, potentially leaking.

### Purpose 11 — Live monitoring and notifications

**`monitors.json` adoption (N=54):**

| Path | Count | Notable |
|---|---|---|
| Present | 2/54 | damionrashford/trader-os (5 monitors across 2 plugins), Chachamaru127/claude-code-harness (1 monitor — `harness-session-monitor`) |
| Absent | 52/54 | Dominant |

**Docs alignment:** Pattern doc says "1/21 adopt monitors." Extended to 54: **2/54** — now includes Chachamaru127. Still rare.

**Corrections to pattern doc:** Add Chachamaru127 to the monitors-adopter list. The sole-reference claim ("damionrashford/trader-os is the reference implementation") is now inaccurate — Chachamaru127 has a simpler one-monitor usage (`when: always` reusing same `hook` subcommand surface as hooks.json). Two distinct patterns now observed.

**Novel alternatives to monitors.json:**
- **GitHub Actions cron as plugin scheduler** — BaseInfinity/sdlc-wizard (weekly-update, monthly-research, api-watcher), Emasoft (notify-marketplace.yml), robertnowell/marketing-pipeline (daily.yml × 5 fires/day).
- **Stop-event hooks as notification channel** — ChanMeng666 uses Stop hooks for desktop audio; hwuiwon/autotune uses Stop for statusLine refresh; jxw1102 uses Stop for Flipper display.
- **statusLine integration** — autotune, ChanMeng666, Chachamaru127 write statusline scripts.

### Purpose 12 — Plugin-to-plugin dependencies

**`dependencies` field adoption (N=54):** **0/54** explicitly observed. Feature (Claude Code v2.1.110+) is too new to have percolated.

**`{plugin-name}--v{version}` tag format:** 0/54 observed.

**Inferred dependencies (docs-only, not declared):**
- damionrashford: `trading-core` depended on by `polymarket-plugin` and `coinbase-agent-kit` — documentation only.
- BrandCast-Signage/root: `mcp-root-board` vs `mcp-local-rag` ownership-based install split — prose convention.
- stellarlinkco: `WRAPPER_REQUIRED_MODULES = new Set(["do", "omo"])` encoded in installer, not in manifests.

**Corrections to pattern doc:** Pattern doc says "effectively 0/21 verified." Extended to 54: still 0. No change needed; still an un-exercised feature across the sample.

### Purpose 13 — Testing and CI

**Test framework (N=54):**

| Framework | Count |
|---|---|
| pytest | ~10/54 (anthropics/claude-plugins-community has close-external-prs.yml only which isn't testing; CodeAlive, CronusL-1141, Vortiago, ZhuBit, robertnowell, smcady, NoelClay partial, Kanevry pre-v3, SkinnnyJay) |
| unittest | 1/54 — AgentBuildersApp |
| bash scripts | ~10/54 — BULDEE, HiH-DimaN, Chachamaru127, Chulf58, ship, tretuttle, coco-workflow |
| Jest/vitest/node:test | ~10/54 — affaan-m (node:test), iVintik (node:test + vitest), Kanevry (vitest), BrandCast-Signage/root (jest), ThumbGate (node:test), robertnowell, ProductionOS (bun test), aide (vitest + go test + integration bash), marioGusmao (vitest/node:test declared) |
| Go test + multiple | 3-4/54 — brunoborges, typemux-cc, Chachamaru127, aide |
| Cargo test | 1/54 — typemux-cc (primary) |
| None | ~20/54 |

**Tests location (N=~25 with tests):**

| Path | Count |
|---|---|
| `tests/` at repo root | ~15/25 |
| Inside plugin directory | ~6/25 — CodeAlive, AI-Stuff/browser-capture, damionrashford, autotune (none but inline), ThumbGate (Node tests) |
| Per-plugin `tests/plugins/<name>/` | 1/25 — affaan-m/everything-claude-code |
| Co-located (Go-style) | 3/25 — Chachamaru127, brunoborges, typemux-cc |

**Pytest config location (N=~10 with pytest):**

| Path | Count |
|---|---|
| `[tool.pytest.ini_options]` in pyproject.toml | ~6/10 |
| `pytest.ini` (dedicated file) | 2/10 — SkinnnyJay, mdproctor |
| None | ~2/10 — CodeAlive, Cairn, 123jimin-vibe |

**CI present (N=54):**

| Status | Count |
|---|---|
| Yes | ~30/54 |
| No | ~24/54 |

**CI trigger surface (N=30 with CI):**

| Trigger combination | Count |
|---|---|
| `push: main` + `pull_request: main` | ~20/30 |
| `push` any branch + `pull_request` | ~3/30 |
| `pull_request` only | 2/30 — anthropics/claude-plugins-official, anthropics/knowledge-work-plugins (close-external-prs) |
| `tags: v*` (release only) | ~8/30 (mostly in combination with above) |
| `schedule` (cron) | ~6/30 — anthropics/claude-plugins-official (bump-shas), BaseInfinity (3 shepherds), ThumbGate (many cron workflows), Vortiago (codeql), robertnowell (daily), jmylchreest/aide |
| `workflow_dispatch` | ~10/30 |
| Push-to-non-main-branch-only (release-rc style) | 1/30 — BaseInfinity fixture-smoke on `release/*` |

**Docs-vs-adoption:** Pattern doc says "`claude plugin validate` 0/13" — extended research finds 0/30 of CI-running repos invoke it. Confirmed.

**Matrix strategies (N=30 CI):**

| Matrix | Count |
|---|---|
| No matrix | ~15/30 |
| Python-version | 3/30 — Vortiago (3.10-3.13), AgentBuildersApp (3.10-3.12 × 3 OS), ChanMeng666 (3.9/3.12/3.13 × 3 OS) |
| OS × language | ~6/30 — Chachamaru127, AgentBuildersApp, affaan-m, Kanevry (3 OS), typemux-cc, 777genius |
| Wider (OS × lang × PM) | 2/30 — affaan-m (OS × Node × PM, 33 lanes), BULDEE |

**Action pinning:**

| Path | Count |
|---|---|
| Major-tag pinning (`@v4`) | ~23/30 |
| SHA-pinning with tag comment | ~4/30 — anthropics/claude-plugins-official, CodeAlive, Kanevry, affaan-m, Vortiago (mixed), Emasoft (partial) |
| Mixed | ~3/30 |

**Caching:**

| Path | Count |
|---|---|
| Built-in setup-X cache | ~15/30 |
| `actions/cache` standalone | ~3/30 |
| No caching | ~12/30 |

**Test runner invocation:**

| Path | Count |
|---|---|
| Direct `pytest` / `go test` / `cargo test` etc. | ~20/30 |
| Bash wrapper (`scripts/test.sh` or equivalent) | 2/30 — Chachamaru127 (`tests/run-tests.sh`) |
| `npm test` / node-script | ~5/30 |
| `uv run pytest` | 1/30 — Vortiago |
| Custom test runner (bun test) | 2/30 — ProductionOS, aide |

**Corrections to pattern doc:**
- Pattern doc "`claude plugin validate` 0/13" — extended to 30, still 0. Docs-vs-adoption conflict preserved.
- Matrix strategies — pattern doc says "6/13 no matrix." Extended to 30 CI-running repos, ~15/30. Proportion holds.

**Pitfalls observed across the sample:**
- Release-trigger workflow that runs tests after the release already published (777genius `test-binaries` post-tag) — not a gate.
- Tolerant CI (`|| true` on test step) — CronusL.
- CI running on every bot-cycle commit (robertnowell) — burns minutes.
- CI covering only Go binary, not the Python/JS hooks (Lykhoyda, aide, brunoborges).

### Purpose 14 — Release automation

**`release.yml` present (N=54):**

| Path | Count |
|---|---|
| Yes (tag-triggered release workflow) | ~15/54 |
| No | ~39/54 |

**Release trigger (N=15):**

| Path | Count |
|---|---|
| `push: tags: ['v*']` | ~10/15 |
| Multi-trigger (tags + release:published + workflow_dispatch) | ~3/15 — ThumbGate, iVintik, Vortiago |
| `release: [published]` only | 1/15 — iVintik |
| `push: main` + tag detection (branch-is-trigger) | 1/15 — ThumbGate (publish-npm.yml) |

**Automation shape (N=15):**

| Path | Count |
|---|---|
| GitHub Release w/ generate_release_notes | ~8/15 |
| Binary build + attach (Rust/Go cross-compile) | ~4/15 — typemux-cc, brunoborges, 777genius, lukasmalkmus, Chachamaru127, jmylchreest/aide |
| npm publish (with `--provenance` + OIDC) | ~5/15 — BaseInfinity, iVintik, ThumbGate, aide, stellarlinkco (manual) |
| PyPI OIDC trusted publishing | 1/15 — Vortiago |
| MCP Registry publish | 2/15 — Vortiago, ThumbGate |
| Homebrew tap formula generation | 1/15 — brunoborges |
| Skill-zip build + draft release | 2/15 — anthropics/healthcare, anthropics/life-sciences (identical) |
| Manual (no workflow) | ~39/54 overall — most repos |

**Tag-sanity gates:**

| Path | Count |
|---|---|
| No gate — accept any `v*` push | ~8/15 |
| Verify tag on main (`git merge-base --is-ancestor`) | 2/15 — BaseInfinity, Emasoft |
| Verify tag matches package/plugin version | ~3/15 — BaseInfinity (package.json), iVintik (package.json + plugin.json sync), affaan-m (3-check gate) |
| Tag-format regex (`^v\d+\.\d+\.\d+$`) | 1/15 — affaan-m |
| Deep gates (all 3+) | 2/15 — BaseInfinity, affaan-m |

**GitHub release creation mechanism:**

| Path | Count |
|---|---|
| `softprops/action-gh-release` | ~6/15 |
| `gh release create` | ~5/15 |
| `taiki-e/create-gh-release-action` | 1/15 — lukasmalkmus |
| CHANGELOG.md parsing (awk) | 1/15 — Chachamaru127 |
| Draft release | 2/15 — anthropics/healthcare, anthropics/life-sciences |

**Docs alignment:** Pattern doc gates + generation sources still accurate.

**Corrections to pattern doc:**
- Pattern doc's "Anthropic release workflows do no gating whatsoever" — confirmed; healthcare + life-sciences release workflows do no tag-sanity checking.
- Pattern doc's "Only Chachamaru threads CHANGELOG content through release workflow" — confirmed.
- Pattern doc "0/6 use dedicated changelog generators" — extended: still 0/15. Multiple repos use `git-cliff` separately (Chachamaru127, Emasoft) but not inside the release workflow itself.

### Purpose 15 — Marketplace validation

**Validation workflow present (N=54):**

| Path | Count |
|---|---|
| Dedicated validator workflow | ~4/54 — anthropics/claude-plugins-official (bun+zod), Chachamaru127 (bash+Go tests), anthril (jq parse), coco-workflow (none, via allowlist only) |
| Inside CI (validate step) | ~10/54 |
| No validation | ~40/54 |
| `claude plugin validate` CLI invocation | **0/54** |

**Validator type (N=~14):**

| Type | Count |
|---|---|
| bun+TS (no zod) | 1 — anthropics/claude-plugins-official |
| bun+zod | 0 |
| node custom | ~3 — affaan-m, iVintik, lukasmalkmus |
| Python inline scripts | ~2 — BULDEE, anthropics/claude-plugins-official (validate-frontmatter.ts is TS) |
| jq + bash | ~3 — anthril, mg-plugins, Arcanon-hub |
| Pre-commit hook | 1 — Chachamaru127 (via `.githooks/pre-commit`) |
| Skill-agent-driven review | 2 — anthropics/healthcare, anthropics/life-sciences (Claude-in-CI reviews) |

**Docs-vs-adoption conflict (re-confirmed):**
- Pattern doc: "★ Docs recommend `claude plugin validate`; 0/13 wire it into CI." Extended to 54: **still 0**. Anthropic's own `claude-plugins-official` uses bun+TS, not the CLI. Confirmed.

**Corrections to pattern doc:** No change needed; docs-vs-adoption conflict is preserved at larger sample.

### Purpose 16 — Documentation

**`README.md` at repo root:** ~54/54 — universal.

**`CHANGELOG.md` at repo root (N=54):**

| Path | Count |
|---|---|
| Present | ~27/54 |
| Absent | ~27/54 |

**CHANGELOG format when present (N=~27):**

| Format | Count |
|---|---|
| Keep a Changelog (explicit) | ~17/27 — BULDEE, BaseInfinity, CronusL, Kanevry, 777genius, Chachamaru127, mcp-outline (absent actually), Chulf58, BrandCast, raphaelchristi, ZhuBit (no), prospect-studio, Emasoft, coco-workflow (no CHANGELOG), stellarlinkco |
| Custom format | ~8/27 |
| Keep a Changelog-like but loose | ~2/27 |

**`architecture.md` at repo root:**

| Path | Count |
|---|---|
| Present (ARCHITECTURE.md or architecture.md) | ~12/54 |
| In `docs/` subdirectory | ~5/54 |
| Embedded in CLAUDE.md or README | ~15/54 |
| Absent | ~22/54 |

**`CLAUDE.md`:**

| Path | Count |
|---|---|
| At repo root | ~22/54 |
| Per plugin | ~2/54 — anthropics (financial-services's root CLAUDE.md is stale template; knowledge-work's partner-built/slack), damionrashford's root CLAUDE.md also. |
| AGENTS.md instead or also | ~6/54 — knowledge-work-plugins/zoom-plugin, BaseInfinity, ship, stellarlinkco, Chachamaru127 (implicit), aide |

**Per-plugin README (N=multi-plugin repos):**

| Path | Count |
|---|---|
| Per-plugin README present (in multi-plugin repos) | ~7/multi-plugin subset |
| Mixed | ~5 |
| Absent | several single-plugin repos where root README serves |

**Community health files (SECURITY, CONTRIBUTING, CODE_OF_CONDUCT combined):**

| Path | Count |
|---|---|
| All three | ~6/54 — BULDEE, BaseInfinity, Kanevry, damionrashford, ThumbGate (partial), ship (partial) |
| Some | ~12/54 |
| None | ~36/54 |

**LICENSE:**

| Path | Count |
|---|---|
| Present at root with SPDX-recognized content | ~45/54 |
| Declared in plugin.json only, no file | ~6/54 — JordanCoin ("UNLICENSED" in plugin.json vs MIT in README), NoelClay (MIT declared, no file), prospect-studio, FORGE, robertnowell, anthropics/healthcare (per-skill LICENSE.txt) |
| Per-plugin LICENSE (no root) | ~2/54 — anthropics/claude-plugins-official, anthropics/life-sciences |

**Badges / status indicators:** ~20/54 present (widely variable).

**Docs alignment:** Pattern doc CHANGELOG adoption says 9/18 (50%). Extended to 54: ~27/54 (50%). Holds.

**Corrections to pattern doc:** Pattern doc CLAUDE.md observation says "observed in BULDEE, Kanevry, this project" — extended research shows ~22/54 with CLAUDE.md, substantially higher than the 3-repo count suggested.

**Pitfalls observed:**
- License-declared-but-no-file: JordanCoin, NoelClay, prospect-studio, FORGE, robertnowell — GitHub license API returns null.
- CHANGELOG version-drift vs plugin.json — anthril, ShaheerKhawaja, multiple.
- AGENTS.md vs CLAUDE.md duplication (lukasmalkmus, aide): same content in two files.

### Novel axes — cross-sample clusters

Clusters of novel axes (§17 in per-repo files) appearing across 3+ repos:

#### 1. Multi-ecosystem single-source plugin (Claude Code + Cursor + Codex + OpenCode + Gemini)

**Repos (5+):** ship, jmylchreest/aide, REPOZY/superpowers-optimized, SkinnnyJay/wiki-llm, ShaheerKhawaja/ProductionOS, stellarlinkco/myclaude, Chachamaru127 (cross-runtime skill mirrors), brunoborges/ghx (dual `.claude-plugin/` + `.github/plugin/` at aggregator), affaan-m (17 version-bearing files across ecosystems).

**Propose:** new purpose section **"Multi-harness distribution"** — how one repo serves multiple AI-coding-assistant ecosystems from a single source tree. Sub-axes: parallel manifest files, content mirroring (skills/ + codex-skills/ + opencode/), per-harness hook-event schema differences, runtime-dispatched output schemas (ship's CURSOR_PLUGIN_ROOT branching).

#### 2. Self-describing CLI via `manifest` subcommand

**Repos (2):** ChanMeng666/claude-code-audio-hooks (`audio-hooks manifest`), autotune (`explain`, `status`, `dashboard` as introspection).

**Propose:** expand §5 or new sub-axis **"Machine-readable plugin capability manifest"** — CLI emits its own capability/hook/config schema as JSON, agent reads it rather than inferring from SKILL.md. Smaller cluster but interesting novel pattern.

#### 3. Hook-event version floors declared only in prose

**Repos (6+):** Emasoft (v2.1.91+ for bin/ feature, v2.1.108+ for plugin, 6 per-hook event floors), BULDEE (v1.0.33+, v3.4.1 added PostToolUseFailure), damionrashford (v2.1.80+, v2.1.105+), BaseInfinity (v2.1.69+, v2.1.105+, v2.1.111+), Chachamaru127 (v2.1.105+), ProductionOS (implicit via startup|resume|clear|compact matcher).

**Propose:** new pitfalls subsection **"Version floors are documentation-only"** — no machine-readable `requires` / `engines.claudeCode` field; plugin installs silently and hook events silently don't fire on older hosts.

#### 4. Shepherd pattern — scheduled GH Actions as plugin-adjacent monitor substitute

**Repos (5+):** BaseInfinity (weekly-update, monthly-research, weekly-api-update — 3 shepherds), ThumbGate (20+ autonomous cron workflows), robertnowell (daily.yml 5 fires/day), anthropics/claude-plugins-official (bump-plugin-shas.yml), Vortiago (codeql weekly), 777genius (rotate-stripe-webhook-secret, social-* workflows).

**Propose:** new sub-axis of purpose 11 (monitoring) **"GitHub Actions cron as scheduler substitute"** — authors route "periodic tasks" through CI rather than plugin monitors.json. Trade-off: durable scheduling without local background processes, at cost of being repo-owner-only.

#### 5. Version-field sprawl across N files requiring manual sync

**Repos (10+):** BULDEE (6 files), ShaheerKhawaja (5 files including VERSION), affaan-m (17 files), damionrashford (3-way: marketplace metadata / per-plugin / plugin.json), Chachamaru127 (3 files), Emasoft (2+ with CPV validation), aide (4 files), skullninja (2 files), 777genius (3 files), iVintik (2 files), mdproctor (3 files for SNAPSHOT convention).

**Propose:** new pitfalls subsection **"N-way version sync as a procedural contract"** — most multi-manifest plugins lack CI enforcement of version field equality, relying on manual bump-script discipline.

#### 6. Config-file in user workspace (not userConfig)

**Repos (6+):** ShaheerKhawaja (`~/.productionos/settings.json`), BrandCast-Signage/root (`root.config.json` in consumer project), CodeAlive (OS keychain), anthropics/financial-services-plugins (`.claude/<plugin>.local.md.example`), Lykhoyda (project `.env.local`), coco-workflow (`.coco/config.yaml`), a3lem (env-var with AUTO_MEMORY_DIR).

**Propose:** expand §8 with sub-axis **"File-convention user config (bypasses plugin userConfig)"** — authors deliberately sidestep plugin userConfig for persistence-across-plugin-updates or cross-tool sharing.

#### 7. Hook-driven dep install + bin-wrapper fallback (lazy-install-on-first-run)

**Repos (5):** brunoborges/ghx (bin shim lazy-installs Go binary), 777genius (wrapper lazy-downloads on every hook), typemux-cc (install.sh on SessionStart), iVintik (SessionStart auto-npm-install-global), Emasoft (bin/token-report uses `uv run --with tiktoken` per-invocation), robertnowell (bin wrapper errors with remediation if venv absent).

**Propose:** Clarify §6 — distinguish "SessionStart install" from "bin-wrapper install" vs "hybrid". Three distinct patterns currently conflated.

#### 8. Scoped-to-repo plugin enforcement (hooks gate on plugin-state file)

**Repos (3):** HiH-DimaN/idea-to-deploy (all hooks gate on `.claude-plugin/plugin.json` at repo root; `.methodology-self-extend-override` as documented bypass), skullninja/coco-workflow (hooks gate on `.coco/state/`), ShaheerKhawaja (hooks gate on `.productionos/` state file).

**Propose:** new pattern — **"self-scoping hooks that no-op outside methodology repos"** — a plugin-level convention for installing hooks globally but gating their activation on project-local state.

---

Closing note on size: where a §17 pattern appeared in 1-2 repos only (e.g., "`subagent_type` namespace convention" only in ShaheerKhawaja; "stakes field" only in ShaheerKhawaja; "Node ABI tracking" only in marioGusmao; "release-codename branches" only in Chachamaru127), it is documented per-repo and flagged here but does not yet warrant a new pattern-doc purpose section. Those live as candidates for future waves.
