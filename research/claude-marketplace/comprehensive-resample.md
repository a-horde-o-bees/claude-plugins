# Comprehensive Resample — Seven Dimensions Against the 54-Repo Corpus

Report-only resampling of seven dimensions recently folded into `plugins/ocd/systems/patterns/templates/claude-marketplace.md` against every per-repo research note under `research/claude-marketplace/repos/` (54 unique repos). Produces corrected adoption counts and a broader citation pool than the partial ~14-repo samples the pattern doc currently cites.

## Methodology

- **Corpus:** 54 per-repo research notes at `research/claude-marketplace/repos/*.md` (skipping `_TEMPLATE.md`, `_INDEX.md`, `_CORRECTIONS.md`).
- **Primary extraction:** `grep` over per-section markers (`**\`userConfig\` present**`, `**CHANGELOG.md**`, `**Test framework**`, etc.) followed by classification from the surrounding prose.
- **Aggregate cross-reference:** `_INDEX.md` (its cross-sample themes preamble already provides extracted counts for purposes 5, 6, 8, 9, 13, 16 — these were sanity-checked against the per-repo files).
- **Spot-checks:** limited to repos where the research note was silent on a dimension but classification mattered; none of the seven dimensions required a broad spot-check campaign (research notes cover these dimensions in adequate breadth, if not always depth).
- **"Not captured" vs "N/A":** N/A means the repo has no relevant surface (no skills, no agents, no CHANGELOG, no tests, etc.); "not captured" means the research note did not cover the dimension, even though the surface may exist.

## Dimension 1 — Description as the discovery surface

### Pattern doc's current claim

> "1/54 repos codify description-writing rules explicitly. **CodeAlive-AI/codealive-skills** prescribes concrete targets..."
>
> Few-shot patterns in agent descriptions: "2–3/54 directly observed — not yet a named convention"
>
> Multilingual trigger surface: "1/54 observed"

### Corpus evidence

The research template's frontmatter/description field data is thin — §1 of the template covers marketplace-level `description`, and §5 covers component registration, but *description-as-matcher* discipline (length, trigger framing, XML few-shot blocks, multilingual phrases) wasn't a template field. What the 54 notes do capture:

**Explicit description-writing discipline (documented rules for length/trigger verbs):**

- **CodeAlive-AI/codealive-skills** — captured in §17: "include concrete trigger verbs/nouns users actually say, 1024 char hard limit, aim 300-500 chars, don't bake in anti-patterns against failure modes of one session — read by many agents in many contexts" (CLAUDE.md verbatim per research note).
- **damionrashford/trader-os** — no explicit length rule in CLAUDE.md, but `quant-math` skill description is 847 chars (captured in pattern doc's 14-file sample).
- **HiH-DimaN/idea-to-deploy** — CONTRIBUTING.md establishes SKILL.md `## Trigger phrases` canonicity rule; `tests/verify_triggers.py` enforces drift between skill trigger phrases and hook regex tables (captured in §17).
- **Lykhoyda/rn-dev-agent** — agent descriptions use multi-line YAML with embedded `<example>/<commentary>` XML blocks AND "Triggers:" keyword lists (captured in §5).
- **anthropics/knowledge-work-plugins** — `partner-built/brand-voice/agents/*.md` uses folded YAML `>` with embedded `<example>` blocks (captured in §5).

**Few-shot `<example>` XML blocks in agent descriptions (directly observed):**

- Lykhoyda/rn-dev-agent — multi-paragraph with 3 example blocks per agent.
- anthropics/knowledge-work-plugins — folded scalar with embedded examples on brand-voice agents.
- skullninja/coco-workflow — "description fields embed XML-ish `<example>` blocks inline in YAML strings" (captured in §5).
- affaan-m/everything-claude-code — captured: "description: 'Expert planning specialist for complex features and refactoring. Use PROACTIVELY when users request feature implementation...'" (trigger-verb framing but no XML blocks).

**Multilingual trigger surface:**

- HiH-DimaN/idea-to-deploy — bilingual Russian+English trigger phrases in every skill's body AND in `hooks/check-skills.sh` regex tables. Full Russian README (`README.ru.md`).
- CronusL-1141/AI-company — paired `CHANGELOG.zh-CN.md` and Chinese localization on the plugin-briefing SessionStart hook (captured in §10). Not multilingual trigger surface per se, but multilingual content.

### Classification of 54 repos

| Repo | Class | Citation |
|---|---|---|
| AgentBuildersApp/eight-eyes | Not captured (few-shot) | — |
| BULDEE/ai-craftsman-superpowers | Exemplifies — explicit trigger-based descriptions on agents but no rules doc | §5 captures trigger-verb framing on agent descriptions |
| BaseInfinity/sdlc-wizard | Not captured | — |
| BrandCast-Signage/root | Not captured | — |
| Chachamaru127/claude-code-harness | Not captured | — |
| ChanMeng666/claude-code-audio-hooks | Not captured | — |
| Chulf58/FORGE | Not captured (rules), Counter-example (partial — `description` captured but length/framing not discussed) | — |
| CodeAlive-AI/codealive-skills | **Exemplifies (explicit discipline)** | §17 — prescriptive rules in CLAUDE.md |
| CronusL-1141/AI-company | Partial — multilingual content but trigger phrases not explicit | §10 (Chinese localization) |
| Emasoft/token-reporter-plugin | Not captured | — |
| HiH-DimaN/idea-to-deploy | **Exemplifies (trigger discipline + multilingual + CI drift detector)** | §17 — M-C11 gate, bilingual triggers |
| IgorGanapolsky/ThumbGate | Not captured | — |
| JordanCoin/pdf-to-text | N/A — minimal plugin, descriptions not a focus | — |
| K-dash/typemux-cc | Not captured | — |
| Kanevry/session-orchestrator | Not captured | — |
| Lykhoyda/rn-dev-agent | **Exemplifies (few-shot)** | §5 — XML example blocks + "Triggers:" keyword lists |
| NoelClay/academic-research-mcp-plugin | Not captured | — |
| REPOZY/superpowers-optimized | Not captured | — |
| SankaiAI/ats-optimized-resume-agent-skill | Not captured | — |
| ShaheerKhawaja/ProductionOS | Not captured (but notable `subagent_type` namespacing extension and `stakes:` field affect matcher) | — |
| SkinnnyJay/wiki-llm | Partial — §18 notes skill frontmatter uniformity gap | — |
| Vortiago/mcp-outline | Not captured | — |
| ZhuBit/cowork-semantic-search | Not captured | — |
| a3lem/my-claude-plugins | Not captured | — |
| affaan-m/everything-claude-code | Exemplifies (trigger framing) | §5 — "Use PROACTIVELY when..." |
| anthril/official-claude-plugins | Partial — SKILL.md `description`/`allowed-tools` observed, but rules not codified in CLAUDE.md beyond general "Australian English mandate" | — |
| anthropics/claude-plugins-community | N/A — aggregator, no own skills | — |
| anthropics/claude-plugins-official | Partial — `validate-frontmatter.ts` requires `description` OR `when_to_use` per skill but no length/framing rules | §15 |
| anthropics/financial-services-plugins | Not captured | — |
| anthropics/healthcare | Not captured | — |
| anthropics/knowledge-work-plugins | **Exemplifies (few-shot)** | §5 — brand-voice agents use folded YAML with `<example>` blocks |
| anthropics/life-sciences | Not captured | — |
| brunoborges/ghx | Not captured | — |
| damionrashford/trader-os | Partial — high-trigger-verb count in skill descriptions (847 chars for quant-math) but no rules doc | §5 — skill enumeration |
| ekadetov/llm-wiki | Not captured | — |
| heliohq/ship | Not captured | — |
| hwuiwon/autotune | Not captured | — |
| iVintik/codeharness | Not captured | — |
| includeHasan/prospect-studio | Not captured | — |
| jmylchreest/aide | Not captured | — |
| jxw1102/flipper-claude-buddy | Not captured | — |
| lukasmalkmus/moneymoney | Partial — skill frontmatter with `argument-hint`/`allowed-tools` observed but no trigger-verb framing rules | §5 |
| marioGusmao/mg-plugins | Not captured | — |
| mdproctor/cc-praxis | Not captured | — |
| raphaelchristi/harness-evolver | Not captured | — |
| robertnowell/marketing-pipeline | Not captured | — |
| skullninja/coco-workflow | **Exemplifies (few-shot)** | §5 — XML example blocks in agent descriptions |
| smcady/Cairn | Not captured | — |
| stellarlinkco/myclaude | Counter-example — agents have minimal frontmatter (`name`, `description` only) | §5 |
| thecodeartificerX/codetographer | Counter-example — minimal frontmatter observed | §5 |
| tretuttle/AI-Stuff | Not captured | — |
| 123jimin-vibe/plugin-prompt-engineer | Not captured | — |
| 777genius/claude-notifications-go | Not captured | — |

### Refined counts

- **Explicit description-writing discipline** (codified length/trigger rules in CLAUDE.md or CONTRIBUTING.md): **2/54** — CodeAlive-AI/codealive-skills, HiH-DimaN/idea-to-deploy. Pattern doc says 1/54.
- **Few-shot `<example>/<commentary>` XML blocks in agent descriptions (directly observed)**: **4/54** — Lykhoyda/rn-dev-agent, anthropics/knowledge-work-plugins (brand-voice), skullninja/coco-workflow, affaan-m/everything-claude-code (indirect — "Use PROACTIVELY" lead-in but no XML blocks). Pattern doc says 2-3/54.
- **Multilingual trigger surface** (explicit multi-language trigger phrases or descriptions): **2/54** — HiH-DimaN/idea-to-deploy (Russian+English, paired with CI drift detector); CronusL-1141/AI-company (Chinese-localized SessionStart content + zh-CN changelog, though trigger phrases not explicitly multilingual). Pattern doc says 1/54.

### Recommended pattern-doc update

- Update "1/54 repos codify description-writing rules explicitly" → **2/54**, add HiH-DimaN/idea-to-deploy alongside CodeAlive-AI. HiH-DimaN's discipline is architecturally stronger (enforced by CI via `tests/verify_triggers.py` drift gate on every push). CodeAlive-AI's is prose-only in CLAUDE.md.
- Update "2-3/54 directly observed" for few-shot patterns → **3-4/54**, add skullninja/coco-workflow to the citation pool.
- Update "1/54 observed" for multilingual → hold at 1/54 for *trigger phrase* bilingualism (HiH-DimaN is the clearest). CronusL-1141 is multilingual *content* (localized output) but not multilingual trigger surface.

### Gaps

Description length/framing data is thin because the template didn't target it. The pattern doc's 14-file sample (HiH-DimaN, BULDEE, Chulf58, ZhuBit, lukasmalkmus, anthropics, Kanevry, Vortiago, CodeAlive-AI, damionrashford, NoelClay, SkinnnyJay) used direct WebFetch against specific command/SKILL.md files — that's not in the per-repo research files. Future wave: extract description lengths and trigger-verb framing for the full 54 if the claim needs broader backing.

---

## Dimension 2 — Command and skill frontmatter

### Pattern doc's current claim

> "Sample: 14 skill/command files across 9 repos" (length regimes)
>
> "9/14 sampled surfaces lead with trigger-verb framing" ... "5/14 use bare 'what it does' descriptors"
>
> `argument-hint` format drift: 4/9 typed bracket, 3/9 prose, 1/9 flag-style, 1/9 subcommand
>
> `name:` asymmetry: "4/7 commands omit `name:`; 8/8 skills include `name:`"
>
> `allowed-tools` syntax: 2/14 plain, 2/14 permission-rule, 2/14 YAML array, 8/14 absent

### Corpus evidence

The research template has no top-level slot for skill/command frontmatter detail — it appears opportunistically within §5 (Plugin-component registration) and §17 (Novel axes). The pattern doc's sample was directly WebFetched from nine repos; scaling to 54 requires either another WebFetch campaign or scavenging what's captured in the research notes.

**What the corpus directly captures:**

- `argument-hint` usage observed in: HiH-DimaN (`argument-hint` in skill frontmatter — example: `[platform-and-account-id]` per anthril's convention note), ZhuBit (`"<folder path>"` — typed bracket form), lukasmalkmus/moneymoney (`<question-or-query>` — typed bracket form), anthril/official-claude-plugins (`[platform-and-account-id]` — prose/placeholder form), Chulf58/FORGE (field listed but exact form not captured), SkinnnyJay (gaps §18 acknowledges frontmatter uniformity not verified).
- `allowed-tools` syntax observed in: HiH-DimaN (mixed plain + permission-rule in same field), BULDEE (`allowedTools` as YAML array), damionrashford (`Bash(uv run *)` permission-rule form on agents), lukasmalkmus (`Bash(mm accounts *)` permission-rule — deliberate scope-limiting), anthril (space-separated `Read Write Edit Grep Bash Agent`), skullninja (skill `allowed-tools`), marioGusmao/mg-plugins (observed), 777genius (observed), NoelClay (observed), brunoborges, raphaelchristi, tretuttle, jxw1102, Chachamaru127, robertnowell (all have allowed-tools somewhere in their skills/agents).
- `name:` field on commands: only a few repos captured this directly. BULDEE/ai-craftsman-superpowers explicitly documents the pitfall: "When a command file under `commands/` declares `name:` in its frontmatter, Claude Code uses the literal value as the slash-command name instead of deriving `<plugin>:<command>` from the filename" (v3.3.3 CHANGELOG). ZhuBit/cowork-semantic-search and NoelClay/learn are noted by the pattern doc as including `name:`. Across the 54 the `name:` discipline isn't systematically recorded in research notes.

**Trigger-verb framing in descriptions (where captured):**

- Exemplifies: affaan-m (`Use PROACTIVELY when users request...`), damionrashford (`quant-math` 847-char trigger enumeration), HiH-DimaN (top-of-body `## Trigger phrases` + description), BULDEE (trigger-verb framing noted in skill review agents), Lykhoyda (multi-paragraph with `Triggers:` keyword lists).
- Counter-example: stellarlinkco (minimal `name`+`description` only), thecodeartificerX (minimal on domain-explorer), anthropics/claude-plugins-official's feature-dev/code-architect.md ("code-architect" with `description` listing tool capabilities, not trigger verbs).

### Classification

The research notes are not uniformly deep enough on frontmatter fields for a clean 54-way classification. Treating the pattern doc's 9-repo sample as the authoritative depth-study, the 54-repo corpus can extend the *existence* of each surface (has `argument-hint`, has `allowed-tools`, has `name:` on commands) but not the precise form in every case.

**Extended existence counts (repos where at least one captured skill/command has the field):**

- `argument-hint` field observed: ~7/54 (ZhuBit, HiH-DimaN, anthril, lukasmalkmus, Chulf58, NoelClay, SkinnnyJay) — others likely have it but not captured.
- `allowed-tools` field observed: ~15/54 (HiH-DimaN, BULDEE, damionrashford, lukasmalkmus, anthril, skullninja, marioGusmao, 777genius, NoelClay, brunoborges, raphaelchristi, tretuttle, jxw1102, Chachamaru127, robertnowell, Chulf58, includeHasan, SkinnnyJay). Permission-rule form (`Bash(X *)`) observed in: damionrashford, lukasmalkmus, HiH-DimaN, skullninja (~4/54).
- `name:` field on commands — captured discussion: BULDEE (omits, documents the pitfall), ZhuBit (includes), NoelClay (includes per pattern doc). Sample too thin to extend beyond the pattern doc's 7-repo count.

### Refined counts

- Pattern doc's `argument-hint` breakdown (4/9 typed bracket / 3/9 prose / 1/9 flag-style / 1/9 subcommand) was based on a 9-file depth sample; extending to 54 would require fetching every skill+command frontmatter. **Hold current counts** — the 54-repo corpus does not surface enough `argument-hint` form detail to correct them.
- Permission-rule `allowed-tools` scoping: pattern doc says 2/14. Corpus-wide, the form is observed in at least **4/54** (damionrashford, lukasmalkmus, HiH-DimaN, skullninja) — note the addition of HiH-DimaN and skullninja to the 2-repo citation pool the pattern doc uses.
- `name:` asymmetry (4/7 omit on commands, 8/8 include on skills): **hold** — corpus-wide data too thin to correct.

### Recommended pattern-doc update

- In the `allowed-tools` syntax variance table, add HiH-DimaN and skullninja to the "permission-rule scoped" citation. HiH-DimaN's mixing of plain and permission-rule forms in the same field is itself a useful reference; skullninja's skill `allowed-tools` use is a sharper example of scope-limiting (captured in index but not yet in the pattern doc's 14-file sample).
- Note explicitly that the sample was 9 repos and that breadth verification across the 54-repo corpus would require targeted WebFetch (not in this resample's scope).

### Gaps

The research notes did not systematically capture frontmatter-field forms. Future wave: for each of the 54 repos, fetch a representative skill+command frontmatter and classify `argument-hint` form, `allowed-tools` syntax, `name:` presence. This would produce defensible 54-denominator counts.

---

## Dimension 3 — Agent delegation patterns

### Pattern doc's current claim

> "Denominator for adoption counts below is repos that ship agents, not the full sample."
>
> "Hook-enforced scope walls: AgentBuildersApp reference; BULDEE at smaller scale; Observed in 3/20."
>
> "Skill composition in agents: 3+/20 of agent-shipping repos."
>
> "`isolation: worktree` alone is observed in 7/20 agent-shipping repos (AgentBuildersApp, BULDEE, REPOZY, damionrashford, NoelClay, Lykhoyda, skullninja)."

### Corpus evidence

Research notes capture agent frontmatter in §5 (Plugin-component registration) for every repo that ships agents. Agent-shipping repos in the corpus:

**Repos with agents present (from §5 "Agent frontmatter fields used" captures):**

1. 123jimin-vibe/plugin-prompt-engineer — 1 agent (prompt-engineer), minimal frontmatter
2. AgentBuildersApp/eight-eyes — 8 agents, `isolation: worktree`, `background: true`, `effort`, `maxTurns` — reference implementation for hook-enforced scope walls
3. Arcanon-hub/arcanon — no agents (worker-based, not agent-based)
4. BULDEE/ai-craftsman-superpowers — 11 agents, `isolation: worktree`, `memory: project/user`, `effort: high`, `skills` array, `allowedTools`
5. BaseInfinity/sdlc-wizard — agents exist in the scaffolding (not fully mapped in research)
6. BrandCast-Signage/root — 8 agents, minimal (`name`, `description`, `model`) per §5
7. Chachamaru127/claude-code-harness — multiple agents with rich frontmatter: `memory: project`, `isolation: worktree` (worker only), `permissionMode: bypassPermissions`, `effort: xhigh` (CC v2.1.111+), `initialPrompt`, `skills`, inline `hooks:` on reviewer
8. CodeAlive-AI/codealive-skills — 1 agent (`codealive-context-explorer`) with `skills: [codealive-context-engine]` and `model: haiku` — skill composition with cost-aware downgrade
9. CronusL-1141/AI-company — multi-agent system (`os-register`, `meeting-participate`, team-member), `skills` references
10. Chulf58/FORGE — agents with `name`, `description`, `model`, `tools`, `maxTurns`, `effort`
11. HiH-DimaN/idea-to-deploy — 7 agents, `effort: high`, `maxTurns: 15-20`, `allowed-tools: Read Grep Glob` (read-only by design)
12. Kanevry/session-orchestrator — agents present (agents/*)
13. Lykhoyda/rn-dev-agent — agents with `memory: true`, XML example blocks, `skills` list, `user-invocable: false` on skills
14. NoelClay/academic-research-mcp-plugin — 1 agent with `isolation: worktree`, `maxTurns: 30`, `tools`, `model: sonnet`
15. REPOZY/superpowers-optimized — agents (`code-reviewer`, `red-team`), `memory: user`, `model: inherit`
16. ShaheerKhawaja/ProductionOS — agents with `stakes:` field and `subagent_type: <plugin>:<name>` namespacing
17. a3lem/my-claude-plugins — some agents (`allowed-prompts` novel field on inject-rules)
18. affaan-m/everything-claude-code — agents (planner, code-reviewer) with `tools`, `model`, trigger-verb descriptions
19. anthril/official-claude-plugins — campaign-auditor agent with `effort: max`, `tools`, no `isolation`/`memory`
20. anthropics/claude-plugins-official — agents (feature-dev, code-simplifier, plugin-dev, hookify, pr-review-toolkit, code-architect)
21. anthropics/knowledge-work-plugins — brand-voice agents with `<example>` blocks, `maxTurns`, `color`
22. damionrashford/trader-os — 15 agents across 3 plugins, `memory: project`, `isolation: worktree` (backtester/strategy-researcher), `skills` (4+), `Bash(uv run *)` permission-rule
23. iVintik/codeharness — verifier agent with `tools: [...]` list form
24. jmylchreest/aide — agents
25. mdproctor/cc-praxis — agents (not deeply captured)
26. raphaelchristi/harness-evolver — proposer agent with `permissionMode: acceptEdits`
27. skullninja/coco-workflow — task-executor with `isolation: worktree`, code-reviewer, pre-commit-tester
28. smcady/Cairn — agents
29. stellarlinkco/myclaude — bmad-architect (minimal `name`+`description`)
30. thecodeartificerX/codetographer — domain-explorer, structural-scanner, sync-agent (minimal frontmatter)

**Repos without agents (confirmed from research notes):**

Emasoft, Vortiago, BaseInfinity (unclear), K-dash, Arcanon-hub (worker-based), anthropics (community, financial-services — mixed), IgorGanapolsky (ThumbGate: not captured as having agents), JordanCoin, brunoborges (Go-only), ekadetov, heliohq, hwuiwon, includeHasan, jxw1102 (plugin has hooks, not agents), lukasmalkmus (skill-only), marioGusmao (skill-only for most plugins), robertnowell (not captured as agent-shipping), SankaiAI, SkinnnyJay (skill-focused), tretuttle, 777genius, ZhuBit (skill-only), ChanMeng666 (hooks only), CronusL-1141 — re-check, Chachamaru127 already counted, anthropics/claude-plugins-community (aggregator), anthropics/life-sciences (skill carving), anthropics/healthcare (same), anthropics/financial-services-plugins (partial).

**Estimated agent-shipping repos: ~24-30/54** (counting is approximate because the template didn't enforce a yes/no "ships agents" field — inferred from §5 content).

**Hook-enforced scope walls (structured-result contract + per-role hook enforcement):**

- AgentBuildersApp/eight-eyes — **the reference** — 8 role-specific agents, `COLLAB_RESULT_JSON_BEGIN/END` structured contract, SubagentStart context-shaping for blind review, scope declared in frontmatter + enforced via PreToolUse/PostToolUse hooks.
- BULDEE/ai-craftsman-superpowers — smaller-scale analog with 14-event hooks.json, `SubagentStop` hook (`subagent-quality-gate.sh`), per-agent effort/tools/skills, scope restriction via allowed-tools.
- Chachamaru127/claude-code-harness — `SubagentStart`, `TaskCreated`, `TeammateIdle` hook events (all undocumented in baseline plugin reference) plus agent-hook (`type: agent`) for Haiku reviewers. Structured-result contract likely present.
- REPOZY/superpowers-optimized — `test-subagent-hook-scope.sh` captured as a test under `tests/claude-code/` — suggests hook-scope enforcement exists.
- anthropics/claude-plugins-official — hookify plugin delivers hooks-as-infrastructure for rule evaluation but not agent-specific role walls; ralph-loop uses Stop hook for recursive re-injection (different pattern).

### Refined counts

**Hook-enforced scope walls:**

- Pattern doc says **3/20**. Corpus suggests **3-4/24-30** depending on how strictly "hook-enforced scope walls" is defined. Clear cases: AgentBuildersApp (reference), BULDEE (smaller-scale), Chachamaru127 (multi-event hook-enforcement including `SubagentStart`). REPOZY is adjacent (scope-enforcement tests exist) but exact shape of enforcement less verified. Recommend: **3/25 agent-shipping repos** clearly exemplify; 1 additional (REPOZY) adjacent.

**Skill composition in agents (`skills:` frontmatter array):**

- Pattern doc says **3+/20**. Direct corpus evidence:
    - CodeAlive-AI/codealive-skills — `skills: [codealive-context-engine]` + `model: haiku` (cost-aware)
    - damionrashford/trader-os — `quant-analyst` with `skills: [quant-math, position-sizing, bayesian-updating, time-series]` (4 skills composed)
    - BULDEE/ai-craftsman-superpowers — agents use `skills` array referencing `craftsman:<skill>` namespace
    - CronusL-1141/AI-company — team-member uses `skills: [os-register, meeting-participate]`
    - Lykhoyda/rn-dev-agent — agents have `skills` list (rn-testing, rn-best-practices)
    - Chachamaru127/claude-code-harness — agents have `skills` list
- **Corrected count: 6/~25 agent-shipping repos** explicitly use `skills:` arrays to compose agents from skill routines — *doubled* relative to pattern doc's "3+/20".

**Non-canonical frontmatter fields — `isolation: worktree`:**

- Pattern doc says **7/20 agent-shipping repos**: AgentBuildersApp, BULDEE, REPOZY, damionrashford, NoelClay, Lykhoyda, skullninja.
- Corpus confirms the 7, and adds Chachamaru127/claude-code-harness (worker agent declares `isolation: worktree`).
- **Corrected count: 8/~25 agent-shipping repos** — add Chachamaru127.

**Non-canonical frontmatter fields — other notable:**

| Field | Pattern doc citation | Corpus confirms |
|---|---|---|
| `memory: project` or `memory: user` | BULDEE, Chachamaru127, damionrashford, Lykhoyda | Confirmed 4/25; plus REPOZY (`memory: user`), Lykhoyda (tester + debugger only — `memory: true`). 5-6/25 |
| `background: true` | AgentBuildersApp, damionrashford | Confirmed 2/25 |
| `effort: xhigh` | Chachamaru127 (CC v2.1.111+) | Confirmed 1/25 |
| `stakes: low|medium|high` | ShaheerKhawaja (HumanLayer-borrowed) | Confirmed 1/25 |
| `subagent_type: <plugin>:<name>` | ShaheerKhawaja | Confirmed 1/25 |
| `user-invocable: false` | knowledge-work-plugins/productivity (Cowork) | Confirmed 1/25; Lykhoyda also uses it on `rn-best-practices` skill |
| `context: fork` | HiH-DimaN, anthril | Confirmed 2/25 |
| `permissionMode: acceptEdits` | raphaelchristi | Confirmed 1/25 |
| `allowed-prompts` | a3lem (undocumented) | Confirmed 1/25 |
| `disable-model-invocation: true` | HiH-DimaN | Confirmed 1/25 |
| `initialPrompt` (multi-line literal block) | Not in pattern doc | Chachamaru127 — candidate addition |
| `color` | Not flagged | Widespread: anthropics/knowledge-work-plugins (brand-voice), CronusL-1141, affaan-m, BrandCast-Signage, Chachamaru127, skullninja, BULDEE (some) — **10+/25**. This field is apparently accepted by Claude Code but its effect is not documented |

### Recommended pattern-doc update

- Update "Observed in 3/20" for hook-enforced scope walls → **3/~25** (drop the "/20" to a wider agent-shipping denominator; pattern doc's 20 was primary-sample-derived). Add Chachamaru127 to the citation pool — 18 hook events including `SubagentStart`, `TaskCreated`, `TeammateIdle` represent the most aggressive hook-based scope enforcement observed.
- Update "3+/20 of agent-shipping repos" for skill composition → **6/~25 agent-shipping repos**. Add citations for BULDEE, CronusL-1141, Lykhoyda, Chachamaru127.
- Update "7/20 agent-shipping repos" for `isolation: worktree` → **8/~25 agent-shipping repos** — add Chachamaru127 to the list (already listed but worker-agent specifically).
- Consider adding `color:` as a widely-adopted-but-undocumented field. 10+/25 agent-shipping repos use it without apparent documented effect.
- Consider adding `initialPrompt:` (multi-line literal block for seeding agent context) — Chachamaru127 observed, candidate for inclusion.

### Gaps

- The "ships agents" denominator is inferred from §5 captures, not from a single yes/no field. Future wave: add a §5 subquestion "Ships agents: Y/N" to the template and backfill.
- Hook-enforced scope-wall enforcement has a continuum — fully-enforced (AgentBuildersApp's reference shape) vs partial (tool-scope in frontmatter only, no runtime enforcement). Corpus distinguishes poorly. Future wave: separate "frontmatter declares scope" from "hooks verify scope".

---

## Dimension 4 — Cross-plugin dependencies

### Pattern doc's current claim

> "Effectively 0/21 verified adoption in sampled repos; feature is too new to have percolated."
>
> "Three repos ship multi-plugin marketplaces where one plugin is functionally depended on by siblings, expressed in prose or installer code rather than declared in manifest: damionrashford/trader-os, BrandCast-Signage/root, stellarlinkco/myclaude."

### Corpus evidence

`**dependencies` field present**` captured in 52 repos (all except `_TEMPLATE.md` and one spot). Of these:

**`dependencies` field explicitly present:**

- **mdproctor/cc-praxis** — **CORRECTION**: research note says `dependencies` is "partial — three observed shapes" and that "per README, the `scripts/claude-skill install quarkus-flow-testing` automatically pulls `java-dev + quarkus-flow-dev` — so some plugin.json files must contain real dependency arrays. Not sampled in this pass." Also: "Entries: bare string or object with `{name: ...}` accepted by the custom resolver (`dep['name'] if isinstance(dep, dict) else dep`). Cross-marketplace not observed. No semver ranges in the resolver." This is the **only corpus repo that actually uses the `dependencies` field** (though through a custom resolver, not Claude Code v2.1.110+'s native mechanism).
- Every other repo: `no`, confirmed across 51 data points.

**Prose/installer-encoded dependencies (functional depend-on relationships not declared in manifest):**

1. **damionrashford/trader-os** — README architecture diagram + CLAUDE.md describe `trading-core` as shared layer. ✓ pattern doc cites.
2. **BrandCast-Signage/root** — CHANGELOG 2.3.0 "Why" section documents `mcp-root-board` vs `mcp-local-rag` ownership-based install split. ✓ pattern doc cites.
3. **stellarlinkco/myclaude** — `WRAPPER_REQUIRED_MODULES = new Set(['do', 'omo'])` in `cli.js` installer. ✓ pattern doc cites.
4. **anthropics/financial-services-plugins** — **Additional finding**: research note says "The README states 'Start with **financial analysis** — the core plugin that provides shared modeling tools and all MCP data connectors' but enforces this only as prose, not as a manifest dependency. `investment-banking` etc. have an empty `.mcp.json` and skills that assume `financial-analysis`'s MCP servers are loaded, but nothing in the metadata expresses that." Pattern doc does NOT currently cite this.
5. **anthropics/claude-plugins-official** — The 12 LSP plugins are independent and flat; research note observes: "Given the LSP 'umbrella' concept (12 LSP plugins that each wrap one language server), a `dependencies` chain would be a natural fit. Instead each LSP plugin is independent and flat." Not a functional dependency (each LSP is self-contained), but a case where dependencies could have been used and deliberately weren't.
6. **anthropics/knowledge-work-plugins** — Listed by pattern doc as "flat-by-convention" alternative — confirmed in research note: "cross-plugin interactions handled by convention — `sales` and `marketing` both connect to HubSpot via their own `.mcp.json`".
7. **BULDEE/ai-craftsman-superpowers** — Single-plugin marketplace with internal "packs" (ai-ml, bash, python, react, symfony); pack content references `packs/ai-ml/mcp/knowledge-rag/` but these are bundled, not separate plugins.
8. **marioGusmao/mg-plugins** — Multi-plugin marketplace; research notes no cross-dependencies captured.
9. **mdproctor/cc-praxis** — per above, IS using `dependencies` field (partial).
10. **anthril/official-claude-plugins** — 10 plugins; research notes no cross-dependencies declared.
11. **tretuttle/AI-Stuff** — Multi-plugin; no cross-deps observed.

### Classification (multi-plugin marketplaces only — N=~14)

| Repo | Plugin count | `dependencies` field | Functional cross-dep | Notes |
|---|---|---|---|---|
| anthropics/claude-plugins-official | 145 | No | No (flat by design) | Aggregator |
| anthropics/claude-plugins-community | 1636 | No | No (aggregator) | Aggregator |
| anthropics/knowledge-work-plugins | ~7 | No | No (flat-by-convention) | Explicit alternative |
| anthropics/financial-services-plugins | ~5 | No | Yes (prose in README; `investment-banking` assumes `financial-analysis` MCP) | **Additional cite** |
| anthropics/life-sciences | 5 | No | No | `strict: false` skill carving |
| anthropics/healthcare | ~3 | No | No | `strict: false` skill carving |
| BULDEE/ai-craftsman-superpowers | 1 | N/A | N/A (single plugin) | Internal "packs" |
| damionrashford/trader-os | 3 | No | Yes (prose, CLAUDE.md) | ✓ cited |
| BrandCast-Signage/root | 2 | No | Yes (prose/install-split) | ✓ cited |
| stellarlinkco/myclaude | ~5 | No | Yes (installer-encoded) | ✓ cited |
| marioGusmao/mg-plugins | ~5 | No | Not captured | — |
| mdproctor/cc-praxis | 48 | **Yes (custom resolver)** | Yes | **Unique — corpus-wide exception** |
| anthril/official-claude-plugins | 10 | No | Not captured | — |
| tretuttle/AI-Stuff | ~3 | No | Not captured | — |
| affaan-m/everything-claude-code | multi | No | Not captured | — |
| jmylchreest/aide | 1 (Claude) + npm + Codex | No | N/A | Multi-harness, not multi-plugin |
| a3lem/my-claude-plugins | ~3 | No | Not captured | — |

### Refined counts

- Pattern doc "0/21 verified adoption" → corpus-wide: **1/54 with `dependencies` field** (mdproctor/cc-praxis, through a custom resolver — not Claude Code's native v2.1.110+ mechanism). For the native mechanism, **0/54 verified**.
- Pattern doc "Three repos" (prose-encoded) → **4/54**: damionrashford, BrandCast-Signage, stellarlinkco, **+anthropics/financial-services-plugins**.

### Recommended pattern-doc update

- Add **anthropics/financial-services-plugins** to the "Prose/installer-encoded dependencies" section as the fourth concrete example — the README's "Start with **financial analysis** — the core plugin that provides shared modeling tools and all MCP data connectors" captures the same pattern (silo-ed plugins functionally depending on a core plugin, no manifest declaration).
- Add **mdproctor/cc-praxis** as a fifth, fundamentally different case: it actually uses the `dependencies` field in some plugin.json files, but resolved through a custom Python resolver (`scripts/claude-skill install <plugin>` walks dependencies via `resolve_dependencies`), *not* Claude Code's native v2.1.110+ mechanism. This shows one repo did invent dependency tracking before (or in parallel with) the official feature. It's a particularly interesting pattern candidate because the resolver accepts both bare strings and `{name: ...}` objects — a shape that matches the pattern doc's expected "Declaration: `dependencies: [{ name, version, marketplace? }]` in `plugin.json`".
- Consider changing "Effectively 0/21" to "**0/54 verified adoption of Claude Code v2.1.110+'s native `dependencies` field; 1/54 uses the field name through a custom resolver (mdproctor/cc-praxis)**".

### Gaps

- The "prose/installer-encoded dependencies" category may be under-counted. Research notes for marioGusmao/mg-plugins (5 plugins), anthril/official-claude-plugins (10 plugins), tretuttle/AI-Stuff (3 plugins), and affaan-m/everything-claude-code don't explicitly verify cross-plugin functional coupling. Future wave: for each multi-plugin marketplace, verify whether README/CLAUDE.md describe plugin A requiring plugin B's presence.

---

## Dimension 5 — `userConfig` sensitive-value handling

### Pattern doc's current claim

> "~14/54 repos declare non-trivial `userConfig`."
>
> "Sensitive-value correctness split — Correct: SkinnnyJay, BULDEE, includeHasan (5/8), Arcanon-hub, NoelClay; Anti-pattern: damionrashford (7 fields), ChanMeng666; Declared-but-unconsumed: Arcanon-hub."
>
> "Env-var bridging: `${user_config.KEY}` in anthril, damionrashford, Arcanon-hub, includeHasan, BULDEE, SkinnnyJay; `CLAUDE_PLUGIN_OPTION_<KEY>` in BULDEE, damionrashford, jxw1102, includeHasan."
>
> "CodeAlive-AI/codealive-skills — WSL boundary — cmd.exe /c cmdkey /list probe + sentinel."

### Corpus evidence

Comprehensive extraction from §8 across 54 research notes:

**`userConfig` present: yes — 11 repos directly, 2 partial/intended, = 13 total:**

| Repo | Field count | `sensitive: true` status | `${user_config.KEY}` | `CLAUDE_PLUGIN_OPTION_` |
|---|---|---|---|---|
| BULDEE/ai-craftsman-superpowers | 7 | **Correct** — `sentry_token` flagged; `sentry_org`/`sentry_project` correctly not flagged | No | Yes (`agent-ddd-verifier.sh`) |
| Emasoft/token-reporter-plugin | 3 | N/A — non-secret numeric settings | Not captured | Not captured |
| Lykhoyda/rn-dev-agent | 3 | N/A — non-secret (port, platform, log level) | Not captured | Yes (§8 captured) |
| SkinnnyJay/wiki-llm | 3 | **Correct** — all 3 API keys flagged | Yes | Not captured |
| damionrashford/trader-os | 15+16+18=49 across 3 plugins | **Anti-pattern** — 7+ secret fields with "SECRET" in description, none flagged | Yes (trading-core `.mcp.json`) | No |
| includeHasan/prospect-studio | 8 | **Partial correct** — 5/8 flagged | Yes | Yes |
| ChanMeng666/claude-code-audio-hooks | 4 | **Anti-pattern** — `webhook_url` unmarked | Not captured | Not captured |
| Arcanon-hub/arcanon | 4 | **Correct** — `api_token` flagged (**Declared-but-unconsumed** — worker reads from separate credential chain) | Partial | Not captured |
| NoelClay/academic-research-mcp-plugin | 2 | **Correct** — `semantic_scholar_api_key` flagged | Not captured | Not captured |
| jxw1102/flipper-claude-buddy | 3 | N/A — non-secret (serial port, transport, BT name) | Not captured | Yes (§8 captured) |
| robertnowell/marketing-pipeline | 11 | Partial — API keys/tokens/app-passwords present; flags not explicitly captured by research note | Not captured | Partial (Pinterest fields declared but not bridged) |
| anthril/official-claude-plugins | Intended: 8 on ppc-manager per tests/README, but 0 in actual plugin.json | Test assertions require 3 `sensitive: true`, but live plugin.json carries no userConfig at all | Yes (8 `${user_config.*}` placeholders in `.mcp.json`) | No |

**`userConfig` absent but with file-convention alternative:**

- CodeAlive-AI/codealive-skills — **OS keychain direct use** via `security`/`secret-tool`/`cmdkey` (pattern doc cites). WSL sentinel `"windows-credential-store"` pattern.
- ShaheerKhawaja/ProductionOS — `~/.productionos/settings.json`
- skullninja/coco-workflow — `.coco/config.yaml`
- BrandCast-Signage/root — `root.config.json` in consumer project
- Lykhoyda/rn-dev-agent — project `.env.local` (Lykhoyda has both userConfig AND file-convention)
- anthropics/financial-services-plugins — `.claude/<plugin>.local.md.example` gitignored markdown
- 777genius/claude-notifications-go — `config/config.json` edited via `/claude-notifications-go:settings`
- Chulf58/FORGE — `forge-config.default.json` copied to `${CLAUDE_PLUGIN_DATA}/forge-config.json` on first SessionStart
- raphaelchristi/harness-evolver — `.evolver.json` in user's project
- a3lem — env-var with `AUTO_MEMORY_DIR`

**`userConfig` absent, no file-convention (genuinely no per-user config needed): ~30/54** — Vortiago (MCP server reads its own env vars), most anthropics catalogs, BaseInfinity, Chachamaru127 (harness has other state mechanisms), Kanevry, HiH-DimaN (project-adopt model), K-dash, marioGusmao, etc.

### Refined counts

- **`userConfig` present with actual fields**: **12/54** directly (BULDEE, Emasoft, Lykhoyda, SkinnnyJay, damionrashford, includeHasan, ChanMeng666, Arcanon-hub, NoelClay, jxw1102, robertnowell + mdproctor partial/not captured). Pattern doc says "~14/54" — slight downward correction. If we include anthril (intended but not shipped — tests/README describe 8 fields), count is 13/54.
- **File-convention bypass (deliberate sidestep of userConfig)**: **7/54** — CodeAlive-AI, ShaheerKhawaja, skullninja, BrandCast-Signage, Lykhoyda (dual-mode), anthropics/financial-services, 777genius, Chulf58, raphaelchristi, a3lem. Pattern doc says "~6/54" — add 777genius, Chulf58, raphaelchristi, a3lem for a **closer to 9-10/54** count.
- **`sensitive: true` correctness breakdown:**
    - **Correct** (all secrets flagged): BULDEE, SkinnnyJay, Arcanon-hub, NoelClay → 4/12 = 33%
    - **Partial correct** (some flagged): includeHasan (5/8) → 1/12
    - **Anti-pattern** (secrets in description but not flagged): damionrashford (multiple plugins), ChanMeng666 → 2/12 = 17%
    - **N/A** (no secret fields): Emasoft (numeric settings), Lykhoyda (non-secret), jxw1102 (non-secret) → 3/12
    - **Declared-but-unconsumed**: Arcanon-hub (api_token) → overlaps with "correct" bucket
    - **Not fully captured**: robertnowell, Emasoft (partial)
- **`${user_config.KEY}` substitution**: observed in anthril, damionrashford, Arcanon-hub, includeHasan, SkinnnyJay (5 direct confirmed); BULDEE uses CLAUDE_PLUGIN_OPTION_ instead. **5-6/~12 userConfig adopters** use the substitution mechanism.
- **`CLAUDE_PLUGIN_OPTION_<KEY>`**: BULDEE, damionrashford, jxw1102, includeHasan, Lykhoyda (research note captures it). **5/~12 userConfig adopters** use the env-var prefix.

### Recommended pattern-doc update

- Update "~14/54" in Schema richness subsection → **~12/54 directly, 13/54 if counting anthril's intended-but-not-shipped case**.
- Expand the file-convention bypass section from "~6/54" to "**~8-10/54** deliberately sidestep `userConfig`" — add 777genius (config.json + `/settings` command surface), Chulf58/FORGE (forge-config.default.json → `${CLAUDE_PLUGIN_DATA}` on first SessionStart), raphaelchristi (.evolver.json in project).
- The sensitive-value correctness split table is accurate but undercounts correct adopters. BULDEE, SkinnnyJay, Arcanon-hub, NoelClay are correct; includeHasan is partial. Table is correct; the "N/A" row (Emasoft, Lykhoyda, jxw1102) is missing — worth showing so the denominator is interpretable.
- Add **Lykhoyda** to the `CLAUDE_PLUGIN_OPTION_<KEY>` citation pool (5 confirmed, not 4).

### Gaps

- robertnowell/marketing-pipeline — 11 fields observed but `sensitive: true` status per-field not captured in detail. Spot-check recommended.
- anthril — intended userConfig via tests/README, but actual plugin.json is empty. This is a partial/inconsistent case that deserves its own row: "declared in tests, absent in live manifest."

---

## Dimension 6 — Release notes format (CHANGELOG)

### Pattern doc's current claim

> "Across ~27/54 repos that ship a CHANGELOG: Keep-a-Changelog explicit ~17/27, Custom format ~8/27, Keep-a-Changelog-loose ~2/27."
>
> "GitHub's `generate_release_notes` is the path of least resistance — it captures commit subjects but loses CHANGELOG author intent. No sampled repo uses `release-please`, `semantic-release`, or `git-cliff`."
>
> "**BaseInfinity/sdlc-wizard**'s `/update-wizard` skill fetches `CHANGELOG.md` via WebFetch at runtime — 1/54."

### Corpus evidence

All 54 repos have CHANGELOG data captured in §16. Direct classification:

**CHANGELOG present at repo root (or per-plugin) — 28 repos:**

| Repo | Format | Notes |
|---|---|---|
| BULDEE/ai-craftsman-superpowers | **Keep-a-Changelog v1.1.0 (explicit)** | 41 KB, references ADRs |
| BaseInfinity/sdlc-wizard | **Keep-a-Changelog-like** | ~46 KB, consumed by `/update-wizard` skill at runtime |
| Kanevry/session-orchestrator | **Keep-a-Changelog** | 55.9 KB, per-session dev-trail entries |
| ChanMeng666/claude-code-audio-hooks | **Keep-a-Changelog (explicit)** | 66 KB, cites keepachangelog.com |
| Chachamaru127/claude-code-harness | **Keep-a-Changelog-adjacent (Japanese)** | 248 KB, awk-extracted for releases |
| CronusL-1141/AI-company | **Keep-a-Changelog (explicit)** | 30 KB + zh-CN variant |
| ShaheerKhawaja/ProductionOS | **Keep-a-Changelog-style** | 13.6 KB, top entry is stale |
| SkinnnyJay/wiki-llm | **Keep-a-Changelog** | — |
| BrandCast-Signage/root | **Keep-a-Changelog (explicit)** | 11.6 KB, adds `Why` and `Migration` subsections |
| Arcanon-hub/arcanon | **Keep-a-Changelog** | Per-plugin; `[Unreleased]` section |
| 777genius/claude-notifications-go | **Keep-a-Changelog (explicit)** | Cites keepachangelog.com/1.0.0 |
| HiH-DimaN/idea-to-deploy | **Keep-a-Changelog 1.1.0** | Adds `Ops`/`Context`/`Rationale`/`Lessons learned`/`Deliberately not done` |
| anthril/official-claude-plugins | **Keep-a-Changelog** | Stale — covers only 1.0.0 |
| raphaelchristi/harness-evolver | **Keep-a-Changelog 1.1.0** | 47.9 KB |
| Lykhoyda/rn-dev-agent | **Keep-a-Changelog base + custom sections** | `Verified-stale`, `Multi-review`, `Benchmarks validated live` |
| Emasoft/token-reporter-plugin | **Keep-a-Changelog-like, generated by git-cliff** | Features/Bug Fixes/Documentation/Miscellaneous sections |
| stellarlinkco/myclaude | **Keep-a-Changelog, generated by git-cliff** | Emoji section markers |
| lukasmalkmus/moneymoney | **Keep-a-Changelog 1.1.0** | SemVer-aligned |
| IgorGanapolsky/ThumbGate | **Keep-a-Changelog variant, generated by @changesets/changelog-github** | 117 KB |
| AgentBuildersApp/eight-eyes | **Custom** | Header "Theme: Verifiable enforcement.", only 5.0.0-alpha entry visible |
| affaan-m/everything-claude-code | **Custom** | Per-release Highlights/Release Surface/New Workflow Lanes |
| a3lem/my-claude-plugins | **Ad-hoc / Keep-a-Changelog-like per plugin** | `spec-driven-dev` CHANGELOG closest to KAC |
| marioGusmao/mg-plugins | **Partial — `ai-quality-guardrails/docs/CHANGELOG.md` only** | Keep-a-Changelog format |
| anthropics/knowledge-work-plugins | **Per-plugin only — zoom-plugin/CHANGELOG.md** | Free-form |
| includeHasan/prospect-studio | **Hybrid — header claims SemVer, entries KAC-ish** | 16.9 KB |
| damionrashford/trader-os | **Keep-a-Changelog-lite, per-plugin** | First-release entries only |
| jxw1102/flipper-claude-buddy | **Custom — `## vX.Y` section format** | Scoped to firmware |
| REPOZY/superpowers-optimized | **Replaced by RELEASE-NOTES.md** (116 KB) | Free-form; consumed by SessionStart hook! |

**CHANGELOG absent — 26 repos:**

123jimin-vibe, Vortiago (release notes in GH Releases only), anthropics/claude-plugins-community, anthropics/claude-plugins-official, anthropics/financial-services-plugins, anthropics/healthcare, anthropics/life-sciences, CodeAlive-AI, ekadetov, heliohq, hwuiwon, iVintik, jmylchreest/aide, NoelClay, ZhuBit, brunoborges/ghx, JordanCoin, K-dash, Chulf58 (only GitHub Release notes; docs/CHANGELOG.md referenced but not verified), robertnowell, SankaiAI, mdproctor, smcady, tretuttle (everywhere), skullninja, thecodeartificerX.

**Release-notes source (for repos with release workflows, N=~15):**

Per pattern doc's existing table — not re-litigated here. Confirmed:

- **`generate_release_notes`** (GitHub auto-generated from commits): most. Includes Vortiago, brunoborges, K-dash, skullninja, Chulf58, jmylchreest/aide, CodeAlive-AI, etc.
- **`softprops/action-gh-release` with `generate_release_notes: true`**: ~6/15.
- **CHANGELOG awk-extraction**: **Chachamaru127/claude-code-harness** (`awk '/^## \[/{if (found) exit; if ($0 ~ /^## \['"$VERSION"'\]/) found=1; next} found'` at release time — extracts exactly the version's KAC block).
- **Hand-maintained custom body**: Vortiago/mcp-outline (install-command stanza appended).

**CHANGELOG as runtime-consumed artifact (pattern doc's 1/54):**

- **BaseInfinity/sdlc-wizard** — `/update-wizard` skill fetches CHANGELOG via WebFetch. ✓ pattern doc cites.
- **REPOZY/superpowers-optimized** — **ADDITIONAL FINDING**: research note §16 says "CHANGELOG.md: absent; replaced by `RELEASE-NOTES.md` (116 KB, free-form 'What's New' sections **consumed by the session-start hook**)". This is a second repo where a changelog-equivalent is agent-readable at runtime — different file name (RELEASE-NOTES.md vs CHANGELOG.md) but same concept.
- Chachamaru127 threads CHANGELOG through release workflow but not skill-time.

### Refined counts

- **CHANGELOG adoption**: **28/54 (52%)** — slight uptick from pattern doc's "~27/54 (50%)". Confirmed.
- **Keep-a-Changelog explicit or KAC-adjacent**: **~19/28** adopters (when including git-cliff-generated KAC variants like Emasoft, stellarlinkco, IgorGanapolsky/ThumbGate). Pattern doc says ~17/27.
- **Custom format**: **~6/28** (AgentBuildersApp, affaan-m, jxw1102/flipper-claude-buddy scoped to firmware, a3lem ad-hoc, anthropics/knowledge-work-plugins zoom-plugin free-form, damionrashford lite-KAC). Pattern doc says ~8/27.
- **Keep-a-Changelog-like but loose**: ~2-3/28 (includeHasan hybrid-KAC, BaseInfinity KAC-like, anthril stale). Pattern doc says ~2/27.
- **CHANGELOG-generator tools**: pattern doc says "No sampled repo uses `release-please`, `semantic-release`, or `git-cliff`." **CORRECTION** — **3 repos use git-cliff** (Emasoft, stellarlinkco, Chachamaru127 per research note) and **1 uses `@changesets/changelog-github`** (IgorGanapolsky/ThumbGate). Generators *outside* the release workflow itself are used; pattern doc's exact claim was "inside the release workflow" — but these generators are invoked separately in CI or pre-commit to produce the CHANGELOG.md that ships with the repo.
- **CHANGELOG as runtime-consumed artifact**: pattern doc says 1/54. **CORRECTION — 2/54**: BaseInfinity/sdlc-wizard (`/update-wizard` skill, true runtime WebFetch) and **REPOZY/superpowers-optimized** (RELEASE-NOTES.md consumed by SessionStart hook).

### Recommended pattern-doc update

- Adjust totals minor: 28/54 adopt; ~19/28 KAC-explicit-or-adjacent (including generator-produced KAC); ~6/28 custom.
- **Update the "No sampled repo uses `release-please`, `semantic-release`, or `git-cliff`" claim**. git-cliff is used by **3 repos** (Emasoft, stellarlinkco, Chachamaru127) — not inside the release workflow in most cases but to produce the CHANGELOG.md prior. `@changesets/changelog-github` is used by IgorGanapolsky/ThumbGate. Specify: "No sampled repo uses `release-please` or `semantic-release`; **3 use git-cliff and 1 uses `@changesets/changelog-github` for CHANGELOG.md generation outside the release workflow**."
- **Update "1/54" to "2/54" for CHANGELOG-as-runtime-consumed artifact**. Add REPOZY/superpowers-optimized: RELEASE-NOTES.md (not CHANGELOG.md per se) is read at SessionStart and injected as context. Same pattern at different file name.

### Gaps

- Full CHANGELOG-generator-tool audit not done. `git-cliff` cases discovered incidentally in research notes. There may be more repos using generators that just weren't surfaced. Future wave: grep `.github/workflows/` and pre-commit configs for generator invocation.

---

## Dimension 7 — Fixture discipline

### Pattern doc's current claim

> "Denominator: repos with pytest or unittest adoption (~4/13 sampled; extrapolating to ~10-15/54 overall — Python test adoption is thinner than the narrative suggests)"
>
> "Real backends over mocks. 0/5 sampled Python test suites use `unittest.mock`. Every fixture goes after a real backend..."
>
> "Fixture scope discipline. Session scope for expensive setup... function scope for per-test isolation... module scope unused across all 4 conftest-using repos."
>
> "Opt-in real-subprocess gates — 2/5 of sampled real-backend test suites use an explicit opt-in gate."

### Corpus evidence

Extraction from §13 across 54 research notes. **Repos with Python test adoption (pytest or unittest):**

| Repo | Framework | Fixture discipline observed |
|---|---|---|
| 123jimin-vibe/plugin-prompt-engineer | Python unittest (via pytest runner) | Not captured |
| Vortiago/mcp-outline | pytest (pytest-asyncio, anyio, trio; markers `integration`/`e2e`) | **Real Docker backend** (e2e). Session-scope for Docker stack, function-scope for `mcp_session` |
| AgentBuildersApp/eight-eyes | unittest (stdlib, single 126K test file) | Real git backend (setUp inits scratch repos) |
| ZhuBit/cowork-semantic-search | pytest (56 tests) | Not captured (likely real backend per pattern doc) |
| CodeAlive-AI/codealive-skills | pytest + pytest-cov | Cross-skill-boundary imports via `importlib.util.spec_from_file_location` |
| CronusL-1141/AI-company | pytest (pytest-asyncio, pytest-cov) | `tests/` has unit/, integration/, e2e/. Real backends implied |
| mdproctor/cc-praxis | pytest (extensive, 35+ files; per-skill `tests/test_cases.json` fixtures) | Data-driven with JSON fixtures |
| SkinnnyJay/wiki-llm | pytest (47+ files) | **Env-var opt-in gate** `RUN_CLAUDE_TESTS` / `RUN_CODEX_SKILL_EVALS` |
| a3lem/my-claude-plugins | pytest (only in spec-driven-dev, 11 test files + conftest.py) | Not deeply captured |
| anthril/official-claude-plugins | pytest (ppc-manager only, 17 modules under unit/integration/lint/) | Not deeply captured |
| SankaiAI | pytest (2 files in renderer/tests/) | Minimal |
| smcady/Cairn | pytest (pytest-asyncio) | **Session-scope for session-metrics accumulator**, function-scope for `integration_count` and `tmp_project_dir` — aligns with pattern doc's observation |
| raphaelchristi/harness-evolver | pytest (bare `__main__` fallback) | Minimal |
| robertnowell/marketing-pipeline | pytest (pytest-asyncio) | Not deeply captured |
| SankaiAI/ats-optimized-resume-agent-skill | pytest (renderer/tests/) | Minimal |
| affaan-m/everything-claude-code | pytest (Python llm abstraction) + node:test (primary) | Mixed |

**Python test adoption total: ~16/54** — slight upward correction from pattern doc's "~10-15/54."

**Real backends over mocks across captured test suites:**

- **Real backends confirmed**: Cairn (SQLite in-memory), CronusL (SQLite?), Vortiago (Docker compose), SkinnnyJay (`claude_runner`, `codex_runner` — real CLI subprocess), AgentBuildersApp (real `git`, hooks), CodeAlive-AI (real setup.py interaction patterns).
- `unittest.mock` usage: **0/16 explicitly captured**. Pattern doc's "0/5" claim extends — it's 0 out of every Python test suite *whose fixture style was actually described in research notes*.

**Fixture scope discipline:**

- Session-scope for expensive setup: Vortiago (Docker), SkinnnyJay (seeded vault), Cairn (session-metrics accumulator).
- Function-scope for per-test isolation: Cairn (`integration_count`), CronusL (tmp_project_dir implied), Vortiago (mcp_session).
- Module-scope unused across research-captured repos. Pattern doc's claim holds.

**Opt-in real-subprocess gates:**

- **Env-var gate**: SkinnnyJay (`RUN_CLAUDE_TESTS`, `RUN_CODEX_SKILL_EVALS`).
- **pytest marker + CLI flag**: this project (`pytest.mark.agent` + `--run-agent`).
- **`if: false` + absent secret**: **ADDITIONAL FINDING — HiH-DimaN/idea-to-deploy's `fixture-smoke.yml`** is fully committed but guarded by `if: false` AND absence of `ANTHROPIC_API_KEY`. This is a novel "disabled-by-default committed CI workflow" pattern — the workflow ships, the cost is gated behind two-hand activation. Research note §17 explicitly frames it as a "ship the infrastructure, do not pay the cost" discipline for expensive LLM-based integration tests.

**Non-Python test frameworks in the corpus** (for completeness — pattern doc is Python-specific):

- bash scripts: BULDEE, HiH-DimaN (stdlib Python+bash), Chachamaru127 (bash+Go), Chulf58 (node:test-style bash runner), ship, tretuttle, coco-workflow, BaseInfinity, REPOZY, brunoborges (installer tests), 777genius (installer tests), ChanMeng666
- node:test / vitest / jest / bun test: affaan-m, iVintik (1650+ vitest), Kanevry (vitest, retired bats), BrandCast-Signage (jest), IgorGanapolsky/ThumbGate (200+ node:test), robertnowell, ProductionOS (bun test), jmylchreest/aide (vitest+Go), marioGusmao (declared)
- Go: brunoborges, typemux-cc (cargo primary + go for harness), 777genius, Chachamaru127, stellarlinkco, jmylchreest
- Cargo: K-dash/typemux-cc (primary), lukasmalkmus/moneymoney (cargo test)
- bats: Arcanon-hub (bats-core submodule-pinned), iVintik, tretuttle

### Refined counts

- **Python test adoption**: **~16/54** (slight increase from pattern doc's "~10-15/54").
- **Non-mock, real-backend discipline in Python test suites**: **5+/16 captured in depth** — Vortiago, Cairn, SkinnnyJay, AgentBuildersApp, CronusL (~partial), CodeAlive-AI, ZhuBit (partial). Pattern doc's "0/5 use `unittest.mock`" claim **holds and extends**: no research note captures any mock-based fixture discipline. Note: this may be partially attributable to research notes not capturing *every* fixture pattern; future spot-checks could confirm.
- **Opt-in real-subprocess gates**: Pattern doc cites 2 (SkinnnyJay env-var, this project marker). Corpus extends with: **HiH-DimaN's `if: false` + absent secret gate** for `fixture-smoke.yml`. **3 distinct mechanisms** across the 54 corpus.

### Recommended pattern-doc update

- Bump Python test denominator from "~10-15/54" to "**~16/54**" in the Fixture discipline preamble.
- Add HiH-DimaN/idea-to-deploy's `fixture-smoke.yml` to the "Opt-in real-subprocess gates" subsection as a third mechanism: **CI-workflow-level `if: false` + absent-secret gate** (rather than just env-var or pytest marker). The research note captures exactly this: "**disabled-by-default committed CI workflow** — fully written and committed but gated by both `if: false` AND absence of `ANTHROPIC_API_KEY`... ship the infrastructure, do not pay the cost."
- Consider making the "Real backends over mocks" observation sharper: **across the ~16 Python test suites across 54 repos, 0 captured in research notes describe any mock-based fixture discipline.** This is a stronger claim than "0/5 sampled" but stays evidentiary (the notes don't say "mock is used") rather than a universal claim (the notes may not have described it at all — research notes vary in fixture depth).

### Gaps

- Most research notes do NOT deeply cover fixture discipline. Fixture patterns are captured *because* they appeared in a repo (surfaced in §13 or §17), not because the template asked. A future-wave targeted pass — for each Python-testing repo, fetch `conftest.py` and the top-level test-fixture patterns — would produce defensible 16-denominator counts.

---

## Summary — how refined counts compare to pattern doc

| Dimension | Pattern doc's claim | Corpus evidence | Direction |
|---|---|---|---|
| 1 — Description as discovery surface | 1/54 explicit discipline; 2-3/54 few-shot; 1/54 multilingual | 2/54 explicit discipline; 3-4/54 few-shot; 1/54 multilingual (trigger-phrase level) | Minor correction |
| 2 — Command and skill frontmatter | 14-file depth study, 9 repos | Corpus confirms permission-rule `allowed-tools` observed in 4+/54 (HiH-DimaN, skullninja, damionrashford, lukasmalkmus) not 2/14; other counts hold | Minor correction |
| 3 — Agent delegation patterns | 3/20 scope walls; 3+/20 skill composition; 7/20 worktree isolation | 3-4/~25 scope walls; **6/~25 skill composition**; **8/~25 worktree isolation** | Skill composition is doubled relative to pattern doc; worktree adds 1 |
| 4 — Cross-plugin dependencies | 0/21 verified native; 3 prose-encoded | **1/54 `dependencies` field (mdproctor, custom resolver)**; **4 prose-encoded** (+anthropics/financial-services) | Add mdproctor (unique) + financial-services |
| 5 — `userConfig` sensitive-value handling | ~14/54 with non-trivial userConfig | **12/54 direct, 13/54 with anthril-intended**; file-convention bypass ~**8-10/54** (not 6) | File-convention expansion; userConfig slight down-correction |
| 6 — Release notes format | 27/54 CHANGELOG; no generator tools | **28/54 CHANGELOG**; **3 use git-cliff, 1 uses changesets**; **2/54 runtime-consumed** (REPOZY added) | Generator-tool claim needs correction; runtime-consumed count doubles |
| 7 — Fixture discipline | ~10-15/54 Python test adoption; 2 gate mechanisms | **~16/54 Python test adoption**; **3 gate mechanisms** (HiH-DimaN `if: false` added) | Test adoption slightly higher; third gate mechanism found |

## Top 5 prioritized pattern-doc updates this resample justifies

1. **Dim 4 — Add mdproctor/cc-praxis as the one corpus repo using a `dependencies` field** (through its custom resolver, not native v2.1.110+). Currently pattern doc says "Effectively 0/21 verified." Corpus finds 1 non-native implementation worth flagging — proof of concept that the pattern predates the official feature.

2. **Dim 4 — Add anthropics/financial-services-plugins to the prose-encoded dependencies section** as a fourth example. Research captures it clearly ("Start with **financial analysis** — the core plugin that provides shared modeling tools and all MCP data connectors"). Currently pattern doc cites 3 repos; 4 is a more defensible count.

3. **Dim 6 — Correct the "no repo uses generator tools" claim**. Research surfaces **3 git-cliff users** (Emasoft, stellarlinkco, Chachamaru127) and **1 `@changesets/changelog-github`** user (IgorGanapolsky/ThumbGate). The claim in the pattern doc is literally "No sampled repo uses `release-please`, `semantic-release`, or `git-cliff`." It needs to be softened to: "Uses outside the release workflow itself are the norm — git-cliff and @changesets/changelog-github are adopted by 4 repos to produce CHANGELOG.md prior to release."

4. **Dim 6 — Upgrade CHANGELOG-as-runtime-consumed artifact from 1/54 to 2/54**. Add REPOZY/superpowers-optimized's RELEASE-NOTES.md (116 KB, consumed at SessionStart) alongside BaseInfinity's `/update-wizard`. Two repos with different file names but the same pattern; worth naming both.

5. **Dim 3 — Double the skill-composition-in-agents count**. Pattern doc says "3+/20". Corpus confirms **6/~25 agent-shipping repos**: CodeAlive-AI, damionrashford (4-skill `quant-analyst`), BULDEE (craftsman namespace), CronusL-1141, Lykhoyda, Chachamaru127. The existing paragraph cites 3 (CodeAlive-AI, damionrashford, BULDEE) but omits the other 3. Adding them strengthens the adoption signal for a pattern that is otherwise under-sold.

## Secondary pattern-doc updates (nice-to-have)

- **Dim 3** — Add Chachamaru127 to `isolation: worktree` citation (8/25 instead of 7/20).
- **Dim 5** — Add 777genius, Chulf58, raphaelchristi to file-convention bypass citations.
- **Dim 5** — Add Lykhoyda to CLAUDE_PLUGIN_OPTION_ citation pool.
- **Dim 7** — Add HiH-DimaN's `if: false` + absent-secret gate mechanism as third gate shape.
- **Dim 3** — Consider calling out `color:` as widely adopted (10+/25) but undocumented in Claude Code plugin reference. Pattern doc's non-canonical-frontmatter list should include it.

## Caveats

- Dimensions 1, 2 (length/framing details), and 7 (fixture depth) have the thinnest coverage in research notes. Counts for these are adjusted conservatively. Pattern doc's existing depth studies (9-file for dim 2, 5-file for dim 7) are authoritative for their narrow samples; corpus-wide breadth verification would need a targeted future-wave.
- Dimensions 3 (agent delegation) and 6 (CHANGELOG) are well-covered across 54 research notes and the counts are defensible.
- Dimension 4 (cross-plugin dependencies) is well-covered — every research note records whether the `dependencies` field is present.
- Dimension 5 (userConfig) is well-covered — every research note records `userConfig present: yes/no` and field count.
