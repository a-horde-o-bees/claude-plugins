# Missing design factors — survey

Discovery-wave report across 7 design dimensions the pattern doc (`plugins/ocd/systems/patterns/templates/claude-marketplace.md`) does not yet cover as Decisions subsections. Draws on the 54-repo research corpus under `research/claude-marketplace/repos/` and the aggregated `_INDEX.md`.

For each dimension:

- **Observation** — adoption counts against an applicable subset, matching the pattern doc's denominator discipline.
- **Evidence** — per-repo citations anchored to research files.
- **Recommendation** — whether the dimension warrants a new Decisions subsection, merger into an existing one, or "observed but not actionable."

**Sample-size caveat.** The 54-repo corpus was built to verify the existing pattern doc's 16 purposes. Dimensions 1-3 and 5 were not first-class template fields — coverage is opportunistic, varies per-repo, and gaps below reflect what the template captured, not what exists in the wild. Dimensions 4 and 6 are covered by existing template fields (§12, §16) and were already partially aggregated in `_INDEX.md`. Dimension 7 has uneven coverage in the test-discussion sections.

---

## 1. User-facing help text quality

**Scope.** How plugins present skills and slash commands to users — README structure for skill introduction, SKILL.md frontmatter shape, `/help` integration, `argument-hint`.

### Observation

Per-plugin README adoption varies by plugin scale, not by quality concern. The template's §16 already tracks the presence/absence dimension; what's NOT tracked is the *shape* of how skills get introduced to users.

`argument-hint` is universal in commands with positional arguments where it was sampled (Chulf58/FORGE, HiH-DimaN, ZhuBit, anthril, lukasmalkmus — 5/5 where commands were deeply inspected), but the total sample with argument-hint evidence is too narrow to extrapolate. Not a first-class template field — would require re-scanning every repo.

Command-frontmatter `name:` is a known trap: BULDEE's CHANGELOG v3.3.3 explicitly documents that putting a `name:` in command frontmatter breaks auto-namespacing ("Claude Code uses the `name:` value as-is in autocomplete, bypassing automatic `craftsman:` prefix. Without `name:`, Claude Code derives from filename and correctly shows `/craftsman:setup` instead of `/setup`"). This is a concrete defect pattern, not a style guideline.

`allowed-tools` syntax on slash commands drifts between plain-name and permission-rule form, sometimes within the same file (HiH-DimaN's `/kickstart` mixes `Read Write Edit Glob Grep` with `Bash(git:*) Bash(npm:*)`).

### Evidence

- **BULDEE/ai-craftsman-superpowers** (`BULDEE--ai-craftsman-superpowers.md`) — CHANGELOG v3.3.3 codifies the anti-pattern: "OMIT `name:` from command frontmatter to get automatic plugin-namespacing. Aligns with official plugin conventions (vercel, metrikia, stripe all omit `name:`)." README is 27.7 KB with badge row, ToC, explicit API-cost disclosure.
- **HiH-DimaN/idea-to-deploy** (`HiH-DimaN--idea-to-deploy.md`) — Mixed `allowed-tools` syntax in same command. Bilingual trigger phrases (Russian + English) in every skill's `## Trigger phrases` section; bilingual descriptions for multi-population plugins.
- **Chulf58/FORGE** (`Chulf58--FORGE.md`) — Documents a full skill frontmatter template: `name`, `description`, `argument-hint`, `allowed-tools`, `model`.
- **lukasmalkmus/moneymoney** (`lukasmalkmus--moneymoney.md`) — Concrete example of scope-limiting via permission-rule syntax: `Bash(mm accounts *)`, `Bash(mm transactions *)` explicitly allowed; write-side verbs (`mm transfer`, `mm transaction add/set`) deliberately omitted to force permission prompt. This is the "intentional gap" form of allowed-tools as UX design.
- **Vortiago/mcp-outline** (`Vortiago--mcp-outline.md`) — 12 KB / ~240 line README: features, prereqs, one-click-install buttons, per-client config snippets, env-var table (16 vars), tool catalog in nine categories, troubleshooting. Representative of high-quality user-facing README shape.

### Recommendation

**Observed but not actionable at current data depth.** The template didn't capture description style, argument-hint presence, or README structure as first-class fields. A dedicated re-scan focused on user-facing surface is needed before proposing an adoption-count-backed Decisions subsection. Two sub-dimensions worth separating when that scan happens:

- *Slash-command frontmatter conventions* (the `name:` trap, `allowed-tools` syntax drift, `argument-hint` discipline) — a defect surface warranting a Pitfalls section if and when broader scan confirms the pattern.
- *README-as-user-entrypoint shape* (badges, install/quick-start/features ordering, per-client install snippets) — style guide territory rather than governance; lower priority for the pattern doc.

The BULDEE `name:` defect is sharp enough to lift into the existing pattern doc's **Plugin-component registration** Pitfalls section today — one concrete example, one concrete consequence, no further sampling needed.

---

## 2. Skill description quality

**Scope.** What makes a good frontmatter `description` — length, "when to use" vs "what it does", decision-aid framing, domain-object naming.

### Observation

The "description as discovery mechanism" axis is the dominant sub-purpose of skill metadata in Claude Code's skill-loader model, but the research template did not capture description length/shape per-repo. Only one repo in the 54-repo corpus codifies description-writing rules explicitly: CodeAlive-AI/codealive-skills's CLAUDE.md prescribes ("include concrete trigger verbs/nouns users actually say", "1024 char hard limit, aim 300-500", "don't bake in anti-patterns against failure modes of one session — read by many agents in many contexts").

The "Cowork pattern" (no always-on injection; skills discovered entirely through frontmatter `description` matching at prompt time) is referenced as folklore in anthropics/financial-services-plugins research but not formally documented anywhere in the corpus as a discipline. Agent `description` fields with embedded `<example>` / `<commentary>` XML blocks are observed in anthropics/knowledge-work-plugins (partner-built/brand-voice), Lykhoyda/rn-dev-agent — used as few-shot triggers for the description-matcher.

HiH-DimaN's bilingual trigger phrases (Russian + English in one description) extend the discoverability surface to multiple linguistic populations — observed once, not yet a pattern.

### Evidence

- **CodeAlive-AI/codealive-skills** (`CodeAlive-AI--codealive-skills.md`) — CLAUDE.md prescribes concrete description-writing rules: length target 300-500 chars, 1024 char ceiling, trigger-verb emphasis, multi-agent context awareness. Explicit because the plugin targets multiple AI hosts (Claude Code + skills.sh + MCP server + plugin-bridge). Noted as "Pattern candidate for the `description` discoverability axis."
- **anthropics/financial-services-plugins** (`anthropics--financial-services-plugins.md`) — "Plugins rely entirely on skills' frontmatter `description` matching to surface domain knowledge when relevant — the classic Cowork pattern (no always-on injection)." Named but not documented.
- **Lykhoyda/rn-dev-agent** (`Lykhoyda--rn-dev-agent.md`) — "Inline `<example>…<commentary>` XML in agent description frontmatter — multi-paragraph YAML literal block scalar with 3 example blocks per agent ... treated as a trigger-rich description by Claude Code's agent matcher."
- **anthropics/knowledge-work-plugins** (`anthropics--knowledge-work-plugins.md`) — `partner-built/brand-voice/agents/*.md` uses "multi-line YAML `>` folded, embeds `<example>` blocks for Claude few-shot."
- **HiH-DimaN/idea-to-deploy** (`HiH-DimaN--idea-to-deploy.md`) — Bilingual trigger phrases (e.g. `code-reviewer` description lists Russian trigger phrases `'проверь код', 'code review', 'ревью', 'проверь PR', 'найди косяки'`). "Multilingual trigger surface" candidate axis.

### Recommendation

**Worth a full subsection — but sourced primarily from docs and the CodeAlive-AI reference, not sample adoption.** Description quality is load-bearing for skill discoverability (that's how Claude Code decides when to load a skill), which makes it a governance concern even if the sample doesn't statistically support adoption counts. Framing:

- Adoption against "authors codifying description-writing rules": 1/54 (CodeAlive-AI). This is a low-adoption observation, not a convention.
- The `<example>`/`<commentary>` few-shot pattern for agent descriptions: 2-3/54 directly observed (anthropics/knowledge-work partner-built, Lykhoyda, possibly others not sampled on this axis). Reference-worthy but not yet a convention.
- Length targets, "when to use" phrasing, decision-aid framing — these are docs-prescribed in Claude Code's skill-creation guidance (fetch `https://code.claude.com/docs/en/plugin-skills` or similar to verify) and should cite docs, not sample.

If a subsection is added, scope it as **"Description as the discovery surface"** and lead with the mechanism (Claude Code's description-matcher behavior) — the sample supports a Pitfalls callout (descriptions that don't include user-facing trigger verbs don't surface to users) but not a full adoption matrix.

---

## 3. Agent delegation patterns

**Scope.** How skills delegate work — `Spawn:` / subagent invocation, isolation models, skill-calling-skill composition, context shaping.

### Observation

Template §5 (Plugin-component registration) captures agent frontmatter fields but not *delegation mechanics*. Across 54 repos, subagent orchestration appears in 8-12 repos with agents, but the mechanisms diverge sharply:

- **Scoped-tool subagents with hook-enforced walls** — AgentBuildersApp/eight-eyes is the sharpest case: 8 role-specific agents (skeptic, security, performance, accessibility, docs, implementer, verifier, …) each with different tool scope enforced by PreToolUse / PostToolUse / SubagentStop hooks. Frontmatter declares `isolation: worktree`, `background: true` (read-only roles only), `effort`, `maxTurns`. Contract: every agent must emit a `COLLAB_RESULT_JSON_BEGIN…COLLAB_RESULT_JSON_END` block or SubagentStop refuses the finish. Blind-review enforced by SubagentStart context-shaping (skeptic literally can't see implementer's summary).
- **Skill-backed subagents with model downgrade** — CodeAlive-AI's `agents/codealive-context-explorer.md` invokes the skill via `skills: [codealive-context-engine]` frontmatter and downgrades to `haiku` for cost optimization ("offload iterative searches to a cheaper model so the caller's expensive-model conversation stays short").
- **Worktree-isolated agents** — `isolation: worktree` observed on AgentBuildersApp, BULDEE, REPOZY, damionrashford, NoelClay, Lykhoyda, skullninja (7/54). Claim: per-role git-worktree isolation for the subagent. BUT — AgentBuildersApp's research note flags that `isolation: worktree`, `background: true`, `effort: medium` are **not documented in the public Claude Code plugin reference**; enforcement is in-hook (scope via PreToolUse) with frontmatter fields possibly being aspirational metadata.
- **Agent-orchestration tools invoked from `allowedTools`** — BULDEE's `team-lead.md` declares `TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage` in `allowedTools` — references to agent-orchestration tools not documented in the plugin reference.
- **subagent_type namespacing** — ShaheerKhawaja's `subagent_type: <plugin>:<name>` convention (1/54).

### Evidence

- **AgentBuildersApp/eight-eyes** (`AgentBuildersApp--eight-eyes.md`) — 8-role constrained-scope pattern with structured-result-block contract (`COLLAB_RESULT_JSON_BEGIN`...), compensating revert after PostToolUse, circuit-breaker-for-hook-crashes, blind-review via context shaping. "This is a novel pattern for multi-agent review: bias mitigation via context walls, not prompt pleading."
- **CodeAlive-AI/codealive-skills** (`CodeAlive-AI--codealive-skills.md`) — "Subagent + skill composition: `agents/codealive-context-explorer.md` invokes the skill via `skills: [codealive-context-engine]` frontmatter and downgrades the model to `haiku`" — cost-aware subagent design pattern.
- **BULDEE/ai-craftsman-superpowers** (`BULDEE--ai-craftsman-superpowers.md`) — `team-lead.md` lists undocumented agent-orchestration tools (`TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage`) in `allowedTools`.
- **damionrashford/trader-os** (`damionrashford--trader-os.md`) — Multi-plugin orchestration: polymarket/coinbase/trading-core each have 5 agents; `quant-analyst` uses `model: inherit, effort: high, maxTurns: 20, skills: [quant-math, position-sizing, bayesian-updating, time-series], memory: project`. Router-pattern at agent layer.
- **ShaheerKhawaja/ProductionOS** (`ShaheerKhawaja--ProductionOS.md`) — `subagent_type: <plugin>:<name>` + `stakes: low/medium/high` (borrowed from HumanLayer). Namespace convention not observed elsewhere.

### Recommendation

**Worth a full subsection, scoped carefully.** Agent-delegation patterns are a load-bearing purpose (multi-agent plugins are a meaningful fraction of the sample) but the delegation mechanism divides cleanly into three sub-patterns that should be named separately:

1. **Hook-enforced scope walls on subagents** — frontmatter declares agent tool set; hooks enforce scope at PreToolUse/PostToolUse. AgentBuildersApp is the flagship; AgentBuildersApp + BULDEE + Kanevry together exercise the pattern in 3/54.
2. **Skill composition in agents** (`skills:` frontmatter array on agent) — CodeAlive-AI, damionrashford, BULDEE. Observed in agents-with-skills form in at least 3/54 repos with agents.
3. **Worktree/background/effort frontmatter** (documented and undocumented fields) — 7/54 use `isolation: worktree`; several also use `background: true` / `effort`. Call out that several fields are not in the public plugin reference.

Framing for the pattern doc: one subsection with three sub-patterns tabulated. Pitfalls: "undocumented frontmatter fields" (the AgentBuildersApp flag), "isolation claims not verified without hook enforcement", "`skills:` array as implicit dependency" (no validation). Denominator for adoption: repos that ship agents (~20/54), not the full sample.

---

## 4. Cross-plugin dependencies

**Scope.** When plugins in a marketplace depend on each other (shared libraries, common infrastructure), how the dependency is expressed and resolved.

### Observation

Already covered by pattern doc §12 (**Plugin-to-plugin dependencies**) — adoption count **0/54 explicit `dependencies` usage** is confirmed at the extended sample. What the current pattern doc *doesn't* fully call out is the inferred/folklore dependency pattern: three distinct repos ship a multi-plugin marketplace where one plugin is functionally depended-on by siblings, documented in prose rather than declared in manifest.

### Evidence

- **damionrashford/trader-os** (`damionrashford--trader-os.md` §12) — "the README architecture diagram and CLAUDE.md both describe trading-core as 'shared quant layer the other plugins consume,' but that coupling is documentation-only, not wired into the dependency schema. Users who install polymarket without also installing trading-core would get broken scripts, but nothing in manifest-land warns them — CLAUDE.md tells contributors to 'Consume trading-core's math + journal from your scripts (don't re-implement Kelly)' but doesn't wire the `dependencies` field. This is a case of schema-supported enforcement being deliberately skipped."
- **BrandCast-Signage/root** (`BrandCast-Signage--root.md`) — `mcp-root-board` vs `mcp-local-rag` ownership-based install split documented in CHANGELOG 2.3.0 "Why" section, not in manifest. Split rationale: first-party vs third-party install location, lifecycle coupling.
- **stellarlinkco/myclaude** (`stellarlinkco--myclaude.md`) — "The npx installer encodes inter-module wrapper dependencies programmatically (`WRAPPER_REQUIRED_MODULES = new Set(['do', 'omo'])`, `WRAPPER_REQUIRED_SKILLS = new Set(['dev'])` in cli.js) rather than declaring them in config.json — 'if you select `do` or `omo`, also run `install.sh` for the `codeagent-wrapper` binary'. This is implicit module dependency baked into the installer, not declarative."
- **anthropics/knowledge-work-plugins** (`anthropics--knowledge-work-plugins.md`) — "Plugins are intentionally flat and independent. Cross-plugin interactions are handled by convention (e.g., `sales` and `marketing` both connect to HubSpot via their own `.mcp.json`) rather than by declared dependency." Negative case — deliberately no dependency.

### Recommendation

**Merge into existing §12.** The current section already flags 0/21 adoption and discusses the dual-tag-namespace pitfall. Two additions:

- **Prose/installer-encoded dependencies** — tabulate the 3 observed cases (trader-os documentation-only, BrandCast ownership-split in CHANGELOG prose, stellarlinkco installer-encoded `WRAPPER_REQUIRED_MODULES`). Call out: "schema-supported enforcement deliberately skipped" as a pattern — not a pitfall, since it's a rational choice pre-v2.1.110 or when targeting older hosts — but worth naming so readers recognize it.
- **Flat-by-convention as a valid alternative** — add the anthropics/knowledge-work case: deliberate flatness to avoid cross-plugin coupling, with shared infrastructure (HubSpot, etc.) configured per-plugin.

No new subsection needed; §12 absorbs these with ~4 bullet points.

---

## 5. `userConfig` sensitive-value handling

**Scope.** For plugins that accept API keys, tokens, secrets via `userConfig`: storage, rotation, log-hiding, validation, env-var indirection, keychain use.

### Observation

Partially covered by pattern doc's **User configuration** section, which already documents the `sensitive: true` anti-pattern with damionrashford and ChanMeng666 as examples, the 2KB keychain quota pitfall, and the file-convention bypass sub-axis. Extended corpus confirms the pattern at 14/54 `userConfig` adopters (~26% of sample) and surfaces additional evidence:

**`sensitive: true` correctness split within the 14 adopters:**

- Correct application — SkinnnyJay (all 3 secret fields), BULDEE (`sentry_token` correct, `sentry_org`/`sentry_project` correctly not flagged), includeHasan (5/8 correctly), Arcanon-hub (`api_token` correctly), NoelClay (`semantic_scholar_api_key`).
- Anti-pattern — damionrashford (7 fields across 3 plugins with "SECRET" in description but no `sensitive: true`), ChanMeng666 (`webhook_url` unmarked).
- Declared-but-unconsumed — Arcanon-hub declares `api_token` but no `.mcp.json` substitution wires it; worker code reads from a separate credential chain.

**Env-var bridging patterns:**

- `${user_config.KEY}` substitution in `.mcp.json` env blocks — anthril, damionrashford, Arcanon-hub (partial), includeHasan, BULDEE, SkinnnyJay.
- `CLAUDE_PLUGIN_OPTION_<KEY>` env var pattern — BULDEE (`agent-ddd-verifier.sh` reads `CLAUDE_PLUGIN_OPTION_agent_hooks`), damionrashford (inside hook scripts), jxw1102, includeHasan.

**Alternative storage backends (not `userConfig`):**

- OS keychain via CLI — CodeAlive-AI uses macOS Keychain + `security`/`secret-tool`/`cmdkey` rather than `userConfig`. Deliberate — shares credentials across agents on the machine.
- WSL-aware credential lookup — CodeAlive-AI's SessionStart hook detects WSL via `grep -qi microsoft /proc/version` and probes Windows Credential Manager through `cmd.exe /c cmdkey /list:codealive-api-key`; since bash can't read the credential value across the WSL boundary, the hook stores the sentinel string `"windows-credential-store"` to signal "credential exists, defer actual read to Python runtime via `powershell.exe`".
- File-convention in user workspace — ShaheerKhawaja's `~/.productionos/config/settings.json`, Lykhoyda's project `.env.local`, anthropics/financial-services-plugins' `.claude/<plugin>.local.md.example` (gitignored examples), coco-workflow's `.coco/config.yaml`. Already in pattern doc.

**No repos observed:** rotation workflows, encrypted-at-rest outside the OS keychain, file-based credentials with intentional disk-level encryption.

### Evidence

- **damionrashford/trader-os** (`damionrashford--trader-os.md`) — 15-18 `userConfig` fields per plugin. "descriptions explicitly flag secrets ... but NO field anywhere uses the `sensitive: true` flag." README acknowledges secrets "stay in your local Claude Code config; never committed, never written to disk" via `/plugin config set` — relies on the storage backend entirely, not the schema flag.
- **CodeAlive-AI/codealive-skills** (`CodeAlive-AI--codealive-skills.md`) — OS keychain via `security`/`secret-tool`/`cmdkey` CLIs; WSL sentinel-pass-through pattern for cross-boundary credential access. "Clever but fragile pattern — novel enough to mention."
- **BULDEE/ai-craftsman-superpowers** (`BULDEE--ai-craftsman-superpowers.md`) — 7 fields including correct `sensitive: true` for `sentry_token`; `CLAUDE_PLUGIN_OPTION_*` env-var bridging pattern in hook scripts.
- **Arcanon-hub/arcanon** (`Arcanon-hub--arcanon.md`) — `userConfig` declared with `sensitive: true` on `api_token` but no `.mcp.json` substitution wires it; worker reads from separate credential chain. Declared-but-unconsumed defect.
- **SkinnnyJay/wiki-llm** (`SkinnnyJay--wiki-llm.md`) — all 3 secret fields correctly `sensitive: true`; clean reference implementation of minimal userConfig.

### Recommendation

**Expand existing §8 (User configuration) rather than add a new subsection.** The current section already has the skeleton; what's missing is:

1. **Adoption count correction** — §8 says "3/21 directly observed with non-trivial `userConfig`"; extended corpus says ~14/54. Update.
2. **`sensitive: true` correctness split** — add a table of correct/anti-pattern/declared-unconsumed with the above repos as exemplars. The split is the actionable finding — it's not "some forget the flag," it's three distinct failure modes with different remediations.
3. **Env-var bridging patterns** — add `${user_config.KEY}` substitution and `CLAUDE_PLUGIN_OPTION_<KEY>` as the two observed bridging mechanisms. Docs likely prescribe these — verify against plugins-reference before claiming.
4. **OS keychain direct-use pitfall expansion** — CodeAlive-AI's cross-boundary sentinel deserves a named pitfall ("WSL boundary breaks keychain CLIs") for authors on Windows.
5. **Declared-but-unconsumed defect** — Arcanon-hub's pattern (declare `userConfig`, don't wire the substitution) is a validator gap — no CI I'm aware of checks that declared fields are actually referenced. Worth a Pitfalls callout.

No new top-level subsection — §8's expansion absorbs it.

---

## 6. Release notes format

**Scope.** Structure of GitHub Releases and CHANGELOG entries — Keep-a-Changelog adoption, Added/Changed/Fixed discipline, dated sections, issue/PR cross-linking, breaking-change callouts.

### Observation

Partially covered by pattern doc's **Release automation** section (which touches "only Chachamaru threads CHANGELOG through release workflow") and **Documentation** section (which mentions CHANGELOG adoption and Keep-a-Changelog as community convention). What's NOT explicitly tabulated is the release-notes *source* split across the sample:

**CHANGELOG.md adoption (N=54):** ~27/54 present, ~27/54 absent. (From _INDEX.md aggregation, matches pattern doc's 50% count.)

**CHANGELOG format when present (N=~27):**
- Keep-a-Changelog explicit (headers, link to keepachangelog.com) — ~17/27
- Custom format — ~8/27
- Keep-a-Changelog-like but loose — ~2/27

**Release-notes source (N=15 repos with `release.yml`):**
- `gh release create --generate-notes` (auto from commits/PRs) — ~8/15
- Custom body with install-command stanza appended — Vortiago
- CHANGELOG awk-extraction — 1/15 (Chachamaru127, the only repo doing this inside release automation)
- `softprops/action-gh-release` (often with generated notes) — ~6/15
- Draft release, human-edited — 2/15 (anthropics/healthcare, anthropics/life-sciences, identical)

**CHANGELOG-drives-in-product-behavior (novel):**
- BaseInfinity/sdlc-wizard — `/update-wizard` skill fetches CHANGELOG.md via WebFetch at runtime and diffs against installed version stamp. CHANGELOG is consumed by the plugin itself, not just by humans.
- BULDEE — CHANGELOG entries reference ADRs (`See [ADR-0013](docs/adr/0013-workflow-orchestrator.md)`), tying release notes to design-decision documents.
- Kanevry — "per-session dev-trail entries during pre-release cycles, stable release blocks, migration sections. Tracks GitLab issue numbers (e.g., `#131`, `#124`)."

**Breaking-change discipline:** not explicitly sampled per-repo; Keep-a-Changelog convention includes a `### Removed` section and major-version semver implies breaking changes, but no repo in the sample codifies a "BREAKING CHANGE" callout convention beyond what semver implies.

**Version-drift observations:**
- CHANGELOG version-drift vs `plugin.json` — anthril, ShaheerKhawaja, multiple others.
- Separate version spaces: marketplace.json vs package.json vs git tags — stellarlinkco has three independent version numbers (5.6.1, 6.7.0, v6.8.2).

### Evidence

- **BULDEE/ai-craftsman-superpowers** (`BULDEE--ai-craftsman-superpowers.md`) — "CHANGELOG.md ... present (41 KB) — Keep a Changelog v1.1.0 format, explicit SemVer adherence, dated entries for every version from v1.2.1 forward. Very detailed fix/change narratives — CHANGELOG entries routinely reference ADRs."
- **Chachamaru127/claude-code-harness** (`Chachamaru127--claude-code-harness.md`) — Only sampled repo doing awk-based CHANGELOG extraction inside release automation. CHANGELOG.md is 248KB; extraction is `awk`-based. Release body format prescribed in `.claude/rules/github-release.md` with `[X.Y.Z] - YYYY-MM-DD` + Before/After table discipline, Japanese for CHANGELOG and English for GitHub Release body.
- **Vortiago/mcp-outline** (`Vortiago--mcp-outline.md`) — "raw `gh release create` (not a marketplace action) with `--generate-notes --notes-start-tag $(git describe --tags --abbrev=0 ${{ github.ref_name }}^)` — auto-computes previous tag for range. Appends a literal Markdown body with PyPI + Docker install snippets." No CHANGELOG.md.
- **Kanevry/session-orchestrator** (`Kanevry--session-orchestrator.md`) — "Keep-a-Changelog format, 55.9 KB. Exceptionally detailed — per-session dev-trail entries during pre-release cycles, stable release blocks, migration sections. Tracks GitLab issue numbers."
- **BaseInfinity/sdlc-wizard** (`BaseInfinity--sdlc-wizard.md`) — "CHANGELOG.md is human-maintained but release notes come from `--generate-notes`. CHANGELOG.md is the durable artifact for in-product `/update-wizard` skill, which fetches it via WebFetch and diffs against the installed version stamp." Novel: CHANGELOG as runtime-consumed artifact.

### Recommendation

**Merge into existing §16 (Documentation).** The current CHANGELOG coverage is one paragraph; it undersells the decision surface. Expand with:

1. **CHANGELOG presence × format table** (4 rows: absent, Keep-a-Changelog explicit, custom, Keep-a-Changelog-loose) with the counts above.
2. **Release-notes source axis** (cross-reference to §14 Release automation) — `--generate-notes` vs CHANGELOG-awk vs custom body. Tabulate the 15 release-workflow repos' source choices.
3. **Novel pattern: CHANGELOG as runtime-consumed artifact** — BaseInfinity's `/update-wizard` fetches via WebFetch. Worth naming because it promotes CHANGELOG from "human docs" to "agent-readable contract" and implies format discipline (the skill has to parse it reliably). Adoption 1/54 — one-off, but illustrative of what CHANGELOG can carry when treated as data.
4. **Pitfalls:**
   - Version-drift between CHANGELOG and `plugin.json` — anthril, ShaheerKhawaja.
   - CHANGELOG-not-parsed-into-release — almost universal; one explicit Pitfall since `--generate-notes` is the path of least resistance and loses the CHANGELOG author's narrative choices.
   - Release body stanza "custom append" without schema — Vortiago's install-command stanza is hand-maintained and can drift from CHANGELOG.

No new subsection; §16 gains ~10-15 lines. Pattern doc's §14 already flags the awk-extraction rarity, so this is coordinated expansion across §14/§16.

---

## 7. Test fixture conventions

**Scope.** Fixture patterns beyond pytest-config-location — integration-test isolation, fixture scoping, mocking practices, real-vs-mock for git/DB/filesystem dependencies.

### Observation

Template §13 captures framework / location / config / CI plumbing but not *fixture internals*. Coverage in the research notes is uneven: some repos have detailed fixture notes, most don't. Within the sampled fixture observations:

**`conftest.py` / fixtures-dir presence (pytest repos):**
- smcady/Cairn — `tests/conftest.py` provides a session-metrics accumulator and asserts the `integration` marker; declares `integration` marker in `[tool.pytest.ini_options]`; has `tests/integration/` subdir with `external_project` fixture dir and `test_agent_loop.py` + `test_sdk_e2e.py`.
- Vortiago/mcp-outline — 12 KB `conftest.py`; `tests/features/` and `tests/e2e/` layouts; `MockMCP` in unit tests, Docker-backed `mcp_session` fixture in e2e.
- CronusL-1141/AI-company — `tests/` has `unit/`, `integration/` subtrees plus top-level `conftest.py`, `e2e_api_coverage.py`, `e2e_dashboard_coverage.py`, `smoke_api_comprehensive.py`; pytest-asyncio with `asyncio_mode = "auto"`.
- Kanevry/session-orchestrator (vitest, not pytest) — `tests/` at repo root with subdirs `hooks/`, `integration/`, `lib/`, `skills/`, `unit/`, `fixtures/`. Plus nested `skills/vault-sync/tests/` for a skill with its own `package.json`.

**Worktree-isolation for tests:** this project's `sandbox_worktree` fixture (wrapping `systems.sandbox`) is referenced in `tests/plugins/ocd/conftest.py` — the only observed case of a disposable-git-worktree fixture for integration tests in the corpus. No other repo uses git-worktree isolation for pytest.

**`tmp_path` usage:** mentioned generically in `testing.md` but not sampled per-repo. Would require re-scanning.

**Mock vs real backends:**
- Vortiago — `MockMCP` in unit tests; Docker container for e2e (`mcp_session` fixture backed by Docker-compose).
- AgentBuildersApp/eight-eyes — `tests/test_collab_hooks.py` (148 tests, ~126K) verifies the enforcement contract against actual adapter manifests — tests against real files.
- Chachamaru127 — co-located Go tests; `tests/run-tests.sh` (~20KB) bash orchestrator.

**Agent-spawning tests:** this project uses `pytest.mark.agent` for real-subprocess tests opt-in via `--run-agent`. No equivalent observed elsewhere in the corpus, though AgentBuildersApp's role tests exercise real-adapter manifests (a different kind of integration).

**Gaps:**
- Fixture scoping (session/module/function) — not captured in any research note.
- Property-based testing — no hypothesis/fast-check evidence in any research note.
- Snapshot/approval testing — not explicitly called out anywhere.
- Security-boundary exhaustive fixtures — AgentBuildersApp's role-spec-as-data pattern is adjacent but not pure security-boundary testing.

### Evidence

- **smcady/Cairn** (`smcady--Cairn.md`) — `tests/conftest.py` with session-metrics accumulator, `integration` marker gate, `external_project` fixture dir. `[tool.pytest.ini_options]` declares `integration` marker.
- **Vortiago/mcp-outline** (`Vortiago--mcp-outline.md`) — 12 KB conftest; unit vs e2e split with MockMCP and Docker-backed mcp_session fixture.
- **CronusL-1141/AI-company** (`CronusL-1141--AI-company.md`) — pytest-asyncio, `asyncio_mode = "auto"`, `unit/` + `integration/` + top-level conftest.
- **AgentBuildersApp/eight-eyes** (`AgentBuildersApp--eight-eyes.md`) — 148 tests verifying enforcement contract against real adapter manifests, enforcement-as-data tested against live spec files.
- **Kanevry/session-orchestrator** (`Kanevry--session-orchestrator.md`) — vitest with `include: ['tests/**/*.test.mjs', 'skills/*/tests/**/*.test.mjs']`; migrated off bats in v3.0.0; nested skill-local tests.

### Recommendation

**Observed but not actionable — not enough sample depth on fixture internals to claim a convention.** Template §13 captures the decidable surface (framework, location, config, CI triggers, matrix, caching, test-runner invocation); fixture-level discipline is a layer deeper that the research notes only sampled opportunistically (at most 4-5 repos with detailed fixture observations).

Two observations worth surfacing without claiming a pattern:

- **`conftest.py` presence in pytest projects** — in the 4 observed cases (Cairn, Vortiago, CronusL, this project), conftest.py is present and non-trivial. This matches pytest community convention more than any claude-plugin-specific pattern — probably not pattern-doc material.
- **No observed worktree-isolated pytest fixture outside this project.** Worth a single sentence in the pattern doc's §13 Pitfalls (or Testing.md rule) noting that the `sandbox_worktree` primitive is this project's convention and that other marketplaces that need to run git operations in tests have not converged on a shared primitive. That's a "not yet a convention" observation, not "observed convention."

If a future wave wants to claim this dimension as a Decisions subsection, it should re-scan ~15 pytest-using repos with the explicit question "what fixtures exist, at what scope, and what do they mock versus use real backends" — that data is not in the current corpus.

---

## Summary

| # | Dimension | Recommendation |
|---|-----------|----------------|
| 1 | User-facing help text quality | Not actionable at current depth; lift BULDEE `name:` defect into §5 Pitfalls now; defer broader scan. |
| 2 | Skill description quality | Worth a full subsection, primarily docs-sourced; 1/54 codifies rules (CodeAlive-AI); cite mechanism, Pitfalls only from sample. |
| 3 | Agent delegation patterns | Worth a full subsection with 3 named sub-patterns (scope-walls, skill-composition, worktree/background/effort). Denominator: repos with agents (~20/54). |
| 4 | Cross-plugin dependencies | Merge into existing §12; add 3 prose/installer-encoded cases and the deliberate-flatness alternative. |
| 5 | userConfig sensitive-value handling | Expand existing §8; add correctness-split table, env-var bridging patterns, WSL-boundary pitfall. |
| 6 | Release notes format | Merge into existing §16 with cross-ref to §14; add CHANGELOG format table, release-notes-source axis, CHANGELOG-as-runtime-artifact novel pattern. |
| 7 | Test fixture conventions | Not actionable; template §13 covers decidable plumbing; fixture internals under-sampled. Future wave material. |

Three of seven dimensions warrant net-new pattern-doc content: dimensions 2 and 3 as new subsections (with scoping caveats), and dimension 6 as a meaningful expansion to §16. Two (4 and 5) are absorbed into existing subsections. Two (1 and 7) are report-only findings pending a targeted re-scan.
