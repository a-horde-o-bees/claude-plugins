# Pattern-Doc Corrections

Corrections surfaced by the 54-repo deep-research aggregation against `plugins/ocd/systems/patterns/templates/claude-marketplace.md`. Each entry records the current pattern-doc text, the evidence from the deep-research files, and a proposed edit.

## 1. Dependency installation → Failure signaling → ★ on "JSON `systemMessage` on stdout"

**Current text (pattern doc):**

```
#### Failure signaling

How install failure surfaces to the user.

| Path | Docs | Adoption |
|---|---|---|
| JSON `systemMessage` on stdout | ★ | Rare explicit observation |
| Silent stderr (default shell behavior) | | Common |

Docs recommend structured `systemMessage` so Claude Code can render the failure cleanly. Silent stderr leaves users with a generic "hook failed" message with no corrective action.
```

**Evidence:** The docs-plugins-reference worked example explicitly says the opposite:
`diff -q ... || (... && npm install) || rm -f "${CLAUDE_PLUGIN_DATA}/package.json"` with comment "**No JSON systemMessage output.** Pattern is silent retry via the `rm` invariant." The docs-prescribed pattern is the `rm`-on-failure retry invariant, not systemMessage emission. Sample-wide, only 1/20 dep-management repos (anthril) emits a JSON systemMessage on install failure; 1/20 more (CronusL-1141) emits `additionalContext` (not systemMessage) with a restart notice on success. Everyone else uses silent exit 0 or stderr-only.

**Proposed correction:** Remove the ★ from "JSON `systemMessage` on stdout" and add ★ to "Silent stderr". Rewrite the narrative below the table:

> Docs prescribe silent retry — the worked example's `rm -f` trailing clause restores the cached manifest to a state that the next session's `diff -q` will re-trigger. No JSON systemMessage is emitted by the docs-worked-example. Community overwhelmingly follows this (silent exit 0 + fail-open). Emitting a systemMessage is a valid extension but not the prescribed path.

## 2. Dependency installation → Install location → Adoption count

**Current text:**

```
| `${CLAUDE_PLUGIN_DATA}` — persistent across plugin updates | ★ | 17/20 |
| `${CLAUDE_PLUGIN_ROOT}` — alongside plugin source | | 3/20 |
| Ad-hoc runtime fetch (`npx`, `uvx`) — no persistent install | | 1/20 (hybrid) |
```

**Evidence:** Deep research finds install location is more varied than the 17/20 DATA count suggests. Actual breakdown across the 20-repo dep-management sample:
- `${CLAUDE_PLUGIN_DATA}` — ~12/20 (anthril, tretuttle, 123jimin-vibe, smcady, ZhuBit, NoelClay, jxw1102, Cairn, ekadetov, brunoborges, JordanCoin, damionrashford — for Node channels only)
- `${CLAUDE_PLUGIN_ROOT}` citing ESM — ~4/20 (Arcanon-hub, includeHasan, Chulf58, marioGusmao/codegraph hybrid — ESM-driven reason)
- Hybrid DATA + symlink back to ROOT — 2/20 (Lykhoyda, marioGusmao/codegraph)
- Global-npm install — 2/20 (iVintik, raphaelchristi)
- Ad-hoc runtime fetch (uv/npx) — 2/20 (damionrashford PEP 723 scripts, Vortiago uvx)
- Third-party in shared home-dir — 1/20 (BrandCast-Signage — `~/.root-framework` for `mcp-local-rag`)

**Proposed correction:** Replace the three-row table with a six-row breakdown reflecting the actual distribution, and add a narrative distinguishing ESM-driven ROOT installs (documented in plugin source code and planning docs at Arcanon-hub and includeHasan) from accidental ROOT placement.

## 3. Dependency installation → Change detection → "Existence only" adoption

**Current text:**

```
| Existence only — misses upgrades | | 1/20 |
```

**Evidence:** Existence-only is more widely used than the count suggests. Across the dep-management sample:
- raphaelchristi — `[ ! -f "$VENV_PY" ]` existence check for venv, `import langsmith` import check for package.
- brunoborges/ghx — `if [ -x "$INSTALL_DIR/ghx" ]` existence check; no version tracking.
- Chulf58/FORGE — mtime vs lockfile (a weak change-detection, not existence but close).
- iVintik — existence check on node_modules; `import docx` probe in SankaiAI is also existence-only.
- SankaiAI — `python -c "import docx"` existence probe.

**Proposed correction:** Change adoption from 1/20 to 3/20 (raphaelchristi, brunoborges, iVintik minimum; SankaiAI is a bin-wrapper not dep-management). Add to the pitfalls section: "existence-only detection does not catch upstream package upgrades, only missing installs — a minor version drift in the pinned package will silently not be picked up."

## 4. Version control and release cadence → Release branching → Chachamaru127 characterization

**Current text:**

```
| Tag on `main` directly; no release branches | | 13/14 |
| Dedicated `release/x.y` long-lived branches | | 1/14 |

Docs silent. Community norm is tag-on-main. Release branches are one-off precedent (`Chachamaru127/claude-code-harness`) — defensible when combined with a dev-counter scheme on main for cache invalidation (this repo's pattern).
```

**Evidence:** The Chachamaru127 research reveals the `release/*-arcana` branches are NOT the release-cut source. Branches are named release codenames (v4.0 "Hokage", v4.3 "Arcana") and sit BEHIND main — tags live on main (`release/v4.3.0-arcana` is 11 commits behind main; `v4.3.0` tag is 1 commit ahead of the release branch). The release branches appear to be prep/historical snapshots, not the branches where tags land.

**Proposed correction:** Reclassify Chachamaru127 as "tag-on-main." Remove the "1/14 release branches" row, or rename it to "release-prep/codename branches (tags still on main)" with Chachamaru127 as the sole adopter. Update the narrative: "Release branches in the `release/*` sense that own tags are 0/14. Chachamaru127 uses `release/vX.Y.0-<codename>` branches as historical snapshots but cuts tags on main."

## 5. Plugin-component registration → Reference style → Adoption counts

**Current text:**

```
| Default directory discovery (minimal `plugin.json`, components found under `skills/`, `agents/`, etc.) | ☆ | 12/21 |
| Inline configuration objects (`mcpServers: {…}` in `plugin.json`) | ☆ | 2/21 |
| External file reference (`"mcpServers": "./.mcp.json"`) | ☆ | 1/21 |
| Explicit default path arrays (`"skills": ["./skills/"]`) | ☆ | 1/21 |
```

**Evidence:** Extended to 54 repos, the distribution is:
- Default directory discovery — ~35/54
- Explicit path arrays — ~12/54 (more common than 1/21 suggests; BrandCast-Signage, ekadetov-Cairn-style, Chachamaru127's explicit paths, marioGusmao, ai-stuff partial, moneymoney, aide, rn-dev-agent, trader-os)
- Inline config objects — ~8/54 (anthropics/life-sciences MCP inline, Chachamaru127 lspServers inline, rn-dev-agent, FORGE, damionrashford monitors, audio-hooks userConfig)
- External file reference — ~3/54 (CronusL-1141, mg-plugins/codegraph, knowledge-work-plugins')

**Proposed correction:** Update counts: default discovery ~35/54, explicit arrays ~12/54, inline ~8/54, external-file ~3/54. Pattern doc's "only 1/21 uses explicit arrays" substantially understates reality.

## 6. Live monitoring and notifications → Lifecycle scope → Chachamaru127 addition

**Current text:**

```
| `when: always` — start at session boot, run until session end | ☆ | 1/21 |
| `when: on-skill-invoke:<skill-name>` — start on skill use | ☆ | 0/21 |
| No monitors | | 20/21 |
```

And the preamble: "Sampled observation: 1/21 (damionrashford/trader-os) ships monitors..."

**Evidence:** Deep research finds Chachamaru127/claude-code-harness also ships a `monitors/monitors.json` with one entry (`harness-session-monitor`, `when: always`) — see file path `monitors/monitors.json`. README explicitly calls this out under v2.1.105+ requirements.

**Proposed correction:** Update adoption from 1/21 to 2/54 for "when: always." Update the preamble: "Sampled observation: 2/54 (damionrashford/trader-os with 5 monitors across 2 plugins, Chachamaru127/claude-code-harness with 1 monitor) ship monitors."

## 7. Documentation → `CLAUDE.md` adoption count

**Current text:**

```
| `CLAUDE.md` (agent procedures) | | ~3/18 (observed in BULDEE, Kanevry, this project) |
```

**Evidence:** Extended to 54, CLAUDE.md is far more prevalent:
- At repo root: BULDEE, Kanevry, BaseInfinity, CronusL-1141, damionrashford, AgentBuildersApp, smcady's absence is the exception (gitignored per their discipline), anthropics/financial-services-plugins (stale), SkinnnyJay, REPOZY (absent deliberately), Chachamaru127, HiH-DimaN, stellarlinkco (at `memorys/CLAUDE.md`), Chulf58, autotune, ship (AGENTS.md instead), ProductionOS, codetographer, coco-workflow, moneymoney, aide (absent, ARCHITECTURE.md only), iVintik, Emasoft (absent), jmylchreest (absent), 777genius (absent), wikillm (at SkinnnyJay — yes present).

Count conservatively ~22-24/54.

**Proposed correction:** Update to "~22/54 (adoption has matured substantially since the 18-repo snapshot; CLAUDE.md is now nearly universal for active plugins)." Remove the three-repo example list and replace with a few representative cases.

## 8. Version authority → "Both (duplicated)" rarity claim

**Current text:**

```
| Both (duplicated) | | 1/14 (observed drift: `5.0.0-alpha` vs `4.2.0`) |
```

And: "Version duplication silently drifts. Plugin-reference documents 'plugin manifest always wins silently' when both locations carry the field. One sample repo demonstrates the drift failure in production (tagged `5.0.0-alpha` but `plugin.json` stayed at `4.2.0`)."

**Evidence:** "Both (duplicated)" is not rare. Extended research finds **live drift in at least 9 repos** at research time:
- AgentBuildersApp — 4.2.0 in marketplace.json vs 5.0.0-alpha in plugin.json (the cited case)
- anthril/official-claude-plugins — missing versions in marketplace entries while plugin.json has them
- Arcanon-hub — three 0.1.0 copies (ok) but historical drift in 0.1.0 bump
- marioGusmao/mg-plugins — router-plugin has `version: 0.1.0` in package.json vs 1.0.8 in plugin.json/marketplace
- ShaheerKhawaja/ProductionOS — five-way drift (VERSION, plugin.json, marketplace.json, package.json, .codex-plugin/plugin.json)
- Chulf58/FORGE — marketplace 1.0.0 vs plugin 0.5.1
- raphaelchristi/harness-evolver — marketplace entry 6.1.0 vs plugin.json 6.4.2 vs tag v6.4.2
- stellarlinkco/myclaude — marketplace 5.6.1 vs package.json 6.7.0 vs tag v6.8.2
- CronusL-1141 — root marketplace 0.6.0 vs nested+plugin 1.3.4
- damionrashford — marketplace metadata 0.4.0 vs per-plugin entries 0.1.0

**Proposed correction:** Update adoption from "1/14" to "~9-10/54 with live drift at research time; duplication itself is common — structural invariant enforcement is the exception." Rewrite pitfall: "Version duplication across 2-5 files is common (observed in ~20/54 repos). Drift at any given moment was observed in ~9/54 — nearly half the duplicators had mismatched values at the time of research. Enforcement mechanisms (pre-commit scripts, CI checks) exist in only ~6 repos; manual discipline is the norm."

## 9. Testing and CI → `claude plugin validate` adoption

**Current text:**

```
| `claude plugin validate` CLI invocation | 0/13 |

**Docs vs adoption conflict.** ★ Docs recommend `claude plugin validate` as the validation command. 0/13 wire it into CI.
```

And in purpose 15: "★ Docs recommend the CLI; Anthropic's own engineering doesn't use it in CI. 0/18."

**Evidence:** Extended to 54 repos with CI (~30), still **0/30** invoke `claude plugin validate` in CI. Docs-vs-adoption conflict is preserved and amplified.

**Proposed correction:** Update counts from 0/13 and 0/18 to 0/30 and 0/54 respectively. Text otherwise accurate. Strengthen the hypothesis: "The 0/30 CI adoption alongside 0/54 preserve-as-a-documentation-note adoption suggests the CLI is used only manually by plugin authors during local development. The docs pattern is a documented practice, not an enforced one."

## 10. Marketplace validation → Anthropic's own practice

**Current text:**

```
**Docs vs adoption conflict.** Anthropic's own `claude-plugins-official` uses bun+zod (`validate-marketplace.ts`), not the CLI.
```

**Evidence:** Deep research finds `validate-marketplace.ts` uses bun + plain TypeScript (no zod). The "zod" claim is incorrect — the validator script at ~65 lines does manual shape checks without a schema library.

**Proposed correction:** Change "bun+zod" to "bun + plain TypeScript (no zod)." The underlying point (Anthropic doesn't use their own CLI) stands; just correct the validator stack description.

## 11. Plugin source binding → `strict: false` usage — add healthcare + life-sciences as carving reference

**Current text:**

```
Setting `strict: false` lets one physical plugin source directory appear as multiple marketplace entries with different skill selections. Anthropic's `life-sciences` and `healthcare` use this to expose five or three subskills respectively as separate catalog entries — each `strict: false` entry carries its own `skills: ["./skill-name"]` list.
```

**Evidence:** Research confirms. No correction needed — this is accurate.

**Proposed addition:** Add the novel hybrid use observed in anthropics/healthcare (mixed skill-carving + MCP-only plugins in one manifest) as a pattern variant. Also add that healthcare's skill-carving plugins have no `plugin.json` at all — metadata lives only in marketplace entry + `metadata.version`. This is novel and worth documenting as "metadata-only-plugin" variant.

## 12. Bin-wrapped CLI distribution → Shebang conventions

**Current text:**

```
| `#!/usr/bin/env bash` | 12/23 |
| `#!/bin/bash` | 4/23 |
| `#!/usr/bin/env python3` | 3/23 |
| `#!/usr/bin/env node` | 3/23 |
| `#!/usr/bin/env -S uv run --script` (PEP 723 inline metadata) | 1/23 (3 files) |
| `#!/bin/sh` or `#!/usr/bin/env sh` | 2/23 |
| `#!/usr/bin/env bun` | 1/23 |
```

**Evidence:** Counts broadly hold with minor variations across the expanded sample. Adding:
- 777genius/claude-notifications-go uses `/bin/sh` POSIX hot path deliberately (not bash) — Debian/Ubuntu `/bin/sh` = `dash` distinction.
- Chachamaru127's `bin/harness` uses `/bin/sh` POSIX shim.
- jmylchreest/aide's `env bun` (1/23) — now has more context: also used by `scripts/aide-hud.ts` etc. so the bun commitment extends beyond bin/.

**Proposed correction:** Update `/bin/sh` count to 2/23 (777genius + Chachamaru127) — already accurate. Add a narrative note that `/bin/sh` choice is sometimes deliberate (to avoid bashisms on Debian/Ubuntu), observed explicitly in both 777genius's wrapper header comment and Chachamaru127's harness shim.

## 13. User configuration → Schema richness sample size

**Current text:**

```
Small sample (3/21 directly observed with non-trivial `userConfig`) — not enough for a cluster analysis, but all three observed instances use the richer shape when fields are more than trivial tokens.
```

**Evidence:** Extended to 54, ~14 repos have non-trivial userConfig. All observed use typed schemas (type, title, description, optional default).

**Proposed correction:** Update "3/21" to "~14/54." Narrative can stay: typed schemas are used when the field count is non-trivial.

## 14. Pitfalls: `sensitive: true` anti-pattern multi-repo evidence

**Current text (under User configuration pitfalls):**

```
**Describing a value as "secret" in the `description` without setting `sensitive: true`.** Observed directly in damionrashford/trader-os: `CDP_WEBHOOK_SECRET`, `TRADING_ALERTS_SECRET`, `POLYMARKET_WEBHOOK_SECRET` all have the word "Secret" in their `description` but none set `sensitive: true`.
```

**Evidence:** The anti-pattern is systematic in damionrashford (7 secret-named fields without the flag across 3 plugins). Also observed: ChanMeng666/audio-hooks's `webhook_url` is unmarked (could carry Slack/Discord webhook secret); anthropics/knowledge-work-plugins partner-built plugins use `${ENV_VAR}` substitution instead of userConfig for secrets.

**Proposed correction:** Expand: "Observed in damionrashford (7 fields across 3 plugins) and ChanMeng666 (webhook_url)." The pattern may be more widespread than the primary sample suggested.

## 15. Pattern doc references-section sample counts

**Current text (References section):**

```
### Primary sample (18)
### Dependency-management sample (20)
### Bin-wrapper sub-sample (23)
```

**Evidence:** The per-repo research covers 54 total unique repos (with overlaps). Primary sample counts are still 18 by the filter criteria. The dep-management sample contains 20 entries; the bin-wrapper sub-sample contains 23. These counts are intact.

**Proposed correction:** No change to the sample boundaries — the numbers still hold. But the pattern doc should be clearer that adoption tables cite the relevant sub-sample denominator, and the _INDEX.md sample-composition section now makes this explicit via the 54 = 18 + 19 + 17 (with overlaps) breakdown.

## 16. Plugin-component registration → Non-standard frontmatter observations

**Current text (under Plugin-component registration):**

```
`hooks`, `mcpServers`, `permissionMode` are **not** supported in plugin-shipped agent frontmatter — these are stripped for security. ... The `tools:` list accepts the same permission-rule syntax as settings.json `permissions.allow` — `Bash(uv run *)`, `Bash(jq *)` — restricting an agent's shell access to a whitelist with glob patterns. Observed in damionrashford/trader-os's quant-analyst agent.
```

**Evidence:** Extended research confirms permission-rule syntax in agent tools is rare — only damionrashford and skullninja/coco-workflow (in skill allowed-tools) use it. BULDEE's CHANGELOG explicitly notes `permissionMode` is stripped. Non-standard frontmatter observed across the sample:
- `memory: project/user` — BULDEE, Chachamaru127, damionrashford, Lykhoyda
- `background: true` — AgentBuildersApp, damionrashford
- `isolation: worktree` — 7+ repos
- `effort: xhigh` — Chachamaru127 (CC 2.1.111+)
- `stakes: low/medium/high` — ShaheerKhawaja (HumanLayer-borrowed)
- `subagent_type: <plugin>:<name>` — ShaheerKhawaja
- `user-invocable: false` — knowledge-work-plugins/productivity (Cowork-specific)
- `context: fork` — HiH-DimaN, anthril
- `permissionMode: acceptEdits` — raphaelchristi (confirmed it works despite docs saying stripped — or CC behavior changed; verify)
- `allowed-prompts` — a3lem (undocumented)
- `disable-model-invocation: true` — HiH-DimaN

**Proposed correction:** Expand the Plugin-component registration section with a sub-subsection **"Non-canonical agent frontmatter fields observed in the wild"** listing these. Flag that some (e.g., `allowed-prompts`, `context: fork`) may be silently ignored and some may require specific Claude Code versions. Also clarify whether `permissionMode: acceptEdits` is actually honored — docs say it's stripped for security, but raphaelchristi's plugin relies on it for proposer agent. This warrants verification.

## 17. Marketplace discoverability → `$schema` reference adoption

**Current text:**

```
| `"$schema": "https://anthropic.com/claude-code/marketplace.schema.json"` | | 2/21 |
| No `$schema` | | 19/21 |
```

**Evidence:** Extended research finds ~6/54 adopt `$schema` (anthropics/claude-plugins-official, HiH-DimaN/idea-to-deploy, hwuiwon/autotune, a3lem/my-claude-plugins, lukasmalkmus/moneymoney, jmylchreest/aide). Note: anthropics/claude-plugins-official is the likely source of the emission — their own tooling produces the schema URL.

**Proposed correction:** Update from 2/21 to ~6/54 (~11%). Narrative holds — still a minority, still high-signal repos. Update the "both adopters are high-signal" to "all six adopters are high-signal or Anthropic-aligned repos."

---

## Summary — top priority edits

In order of impact:

1. **Remove ★ from "JSON `systemMessage` on stdout"** in Dependency installation → Failure signaling (correction 1). Replace with narrative citing docs-worked-example's `rm`-retry invariant.
2. **Update version-duplication drift rarity** (correction 8). "Both (duplicated)" is not 1/14, it's ~20/54 with live drift in ~9/54 at research time.
3. **Correct Chachamaru127 release-branch characterization** (correction 4). Release branches don't own tags; tags live on main. Chachamaru127's release codename branches are historical snapshots.
4. **Update install-location counts** (correction 2). DATA is ~12/20 not 17/20; ROOT-due-to-ESM has a larger share with documented rationale.
5. **Add Chachamaru127 to monitors.json adopters** (correction 6). 2/54 not 1/54.
6. **Update "bun+zod" to "bun + plain TS"** (correction 10). Anthropic validator doesn't use zod.
7. **Expand existence-only change detection count** (correction 3). 3/20 not 1/20.
8. **Revise explicit-path-arrays adoption** (correction 5). 12/54 not 1/21.
9. **Update CLAUDE.md root-adoption count** (correction 7). ~22/54 not ~3/18.
10. **Expand `sensitive: true` anti-pattern with additional evidence** (correction 14). Damionrashford is not isolated.
11. **Update `$schema` adoption count** (correction 17). 6/54 not 2/21.
12. **Document non-canonical agent frontmatter fields with verification flags** (correction 16). Multiple novel fields observed in the wild.
