# Missing design factors — survey

Discovery-wave report across 7 design dimensions the pattern doc (`logs/research/claude-marketplace/consolidated.md`) does not yet cover as Decisions subsections. Draws on the 54-repo research corpus under `logs/research/claude-marketplace/samples/` and the aggregated `_INDEX.md`.

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

---

## 1b. Dimension 1 follow-up — targeted re-scan

**Scope.** Frontmatter-level decisions on slash commands and SKILL.md files — `description` length and framing, `argument-hint` presence and format, `name:` discipline, `allowed-tools` syntax, README structure for skill introduction.

**Sample.** 14 skill/command files across 9 repos (BULDEE, Chulf58/FORGE, HiH-DimaN, ZhuBit, lukasmalkmus, anthropics/claude-plugins-official, Kanevry, Vortiago, CodeAlive-AI, damionrashford, NoelClay, SkinnnyJay). One representative command and one representative skill per repo where both exist; skill-only or command-only where the repo ships one surface.

### Observation

**`description` framing splits sharply between "when to use" and "what it does".** 9/14 lead with a trigger-verb framing ("Use when the user…", "Use whenever…", "Activated automatically when…"); 5/14 are bare "what it does" descriptors. The docs (★ `https://code.claude.com/docs/en/skills#frontmatter-reference`) explicitly prescribe the former for `description`: "Front-load the key use case"; "the combined `description` and `when_to_use` text is truncated at 1,536 characters." Skills that ship a bare "what" description are leaving the description-matcher without the trigger phrases it needs to surface them.

**`description` length clusters in two regimes.** Short commands (19–97 chars) for task-style commands where invocation is explicit; medium-to-long skills (145–847 chars) for description-matched skills. Outliers: lukasmalkmus/moneymoney (677 chars, bilingual German/English trigger phrases), damionrashford/quant-math (847 chars, heavy trigger-verb enumeration). No sampled skill exceeds the docs-prescribed 1,536-char display cap, so no one is bumping the ceiling.

**`argument-hint` format drifts.** Three distinct forms observed: typed angle-bracket (`"<folder path>"`, `"<search query or folder path>"`, `<question-or-query>`) — 4/9 argument-taking skills; prose description (`project idea or description`, `Optional feature description`, `Optional plugin description`) — 3/9; flag-style (`[--fast|--standard|--deep] [--upgrade <tier>]`) — 1/9 (Kanevry); subcommand (`[subcommand]`) — 1/9 (damionrashford). Docs prescribe the bracketed form (★ `[issue-number]` or `[filename] [format]`); the prose form contradicts that convention but isn't blocked.

**`name:` on commands is inconsistently applied.** Of 7 sampled commands, 4 omit `name:` (BULDEE/challenge, anthropics/commit, anthropics/feature-dev, anthropics/create-plugin, Kanevry/bootstrap) — matching BULDEE's documented advice and Anthropic's own practice. 2 include `name:` (ZhuBit/index, NoelClay/learn). 1 has no frontmatter at all (Chulf58/FORGE/hello.md — intentional for a trivial echo command). The omission pattern correlates with being in a plugin directory where namespace-from-directory matters; 3/4 omissions are in plugin layouts (anthropics, Kanevry, BULDEE). SKILL.md files universally include `name:` (8/8) — docs-prescribed fallback applies but authors opt in, which is reasonable since skills must survive directory moves.

**`allowed-tools` syntax varies.** Space-separated plain names (HiH-DimaN, SkinnnyJay) — 2/14; permission-rule scoped form (lukasmalkmus with verb-scoping like `Bash(mm accounts *)`, anthropics/commit with `Bash(git add:*)`) — 2/14; YAML array/list form (NoelClay/learn, anthropics/create-plugin) — 2/14; absent (8/14). Docs prescribe "a space-separated string or a YAML list." Permission-rule form is a legal space-separated-string case with function-call syntax embedded; the mixed form in one file (HiH-DimaN's kickstart has both plain tool names and `Bash(git:*)` in the same space-separated list) is the concrete drift the main survey flagged.

**README skill-introduction structure is inconsistent but not chaotic.** 10 READMEs sampled, line counts spanning 65 to ~2,100. Predominant structure lead-ins:

- Features-then-install (Vortiago, ZhuBit, CodeAlive-AI) — 3/10
- Install-then-features (FORGE, BULDEE, anthropics-official) — 3/10
- Problem-then-solution-then-install (HiH-DimaN, Kanevry, trader-os) — 3/10
- Structure-only (anthropics-plugins-official — no Features/Commands sections at all) — 1/10

No repo explicitly lists commands as a discovery surface at the README top level except BULDEE (a Commands section appears after Quick Start). Skills-as-list sections are rare in README body; most repos surface skill discovery through in-product `/` menu and rely on description-matching rather than README lists.

### Evidence

- **BULDEE/ai-craftsman-superpowers** — `commands/challenge.md`: no `name:`, no `argument-hint`, description 158 chars ("Senior architecture review and code challenge. Use when reviewing code or PRs for quality, auditing architecture decisions, or responding to code review comments."). SKILL.md `session-init`: has `name:`, description 101 chars, includes `disable-model-invocation: true`.
- **Chulf58/FORGE** — `commands/forge/hello.md`: no frontmatter at all (trivial echo command). `commands/forge/doctor.md`: no YAML frontmatter — body-only content. Pattern: FORGE ships command-style skills under `skills/` and treats `commands/` as lightweight entry points.
- **HiH-DimaN/idea-to-deploy** — `skills/kickstart/SKILL.md`: description 145 chars, `argument-hint: project idea or description` (prose form), `allowed-tools: Read Write Edit Glob Grep Bash(git:*) Bash(mkdir:*) ...` (mixed plain + scoped).
- **ZhuBit/cowork-semantic-search** — `commands/index.md`: description 57 chars ("Index a folder of documents for semantic search"), `argument-hint: "<folder path>"` (typed). `skills/semantic-search/SKILL.md`: description 472 chars with bilingual trigger phrases ("was ist in dem Dokument uber..."), `argument-hint: "<search query or folder path>"`.
- **lukasmalkmus/moneymoney** — `skills/moneymoney/SKILL.md`: description 677 chars using YAML block-scalar (`|`), bilingual trigger verbs (German: Überweisung, überweisen, Lastschrift; English: transfer, direct debit). Permission-rule scoped `allowed-tools` with deliberate write-verb omission.
- **anthropics/claude-plugins-official** — `plugins/commit-commands/commands/commit.md`: no `name:`, description 19 chars ("Create a git commit"). `plugins/feature-dev/commands/feature-dev.md`: no `name:`, description 97 chars, `argument-hint: Optional feature description` (prose). `plugins/plugin-dev/commands/create-plugin.md`: no `name:`, description 123 chars, YAML-array `allowed-tools`. `plugins/plugin-dev/skills/skill-development/SKILL.md`: `name: skill-development`, description 287 chars leads with "This skill should be used when the user wants to..." — the docs-recommended trigger-verb form. README itself is minimal (~65 lines): Structure → Installation → Contributing; no Features/Commands/Skills sections.
- **Kanevry/session-orchestrator** — `commands/bootstrap.md`: no `name:`, description 79 chars, `argument-hint: "[--fast|--standard|--deep] [--upgrade <tier>] ..."` (flag-style enumeration — unusual).
- **damionrashford/trader-os** — `plugins/trading-core/skills/quant-math/SKILL.md`: description 847 chars — the longest in the sample — dense with trigger verbs and formula names ("what's my Sharpe", "compute VaR", "expected value of this bet", "convert odds", "confidence interval on my backtest"). `argument-hint: [subcommand]`.
- **CodeAlive-AI/codealive-skills** — `skills/codealive-context-engine/SKILL.md`: description 262 chars, trigger-phrase heavy ("Use when the user mentions 'CodeAlive', asks to list or get data sources, ..."). README 224 lines; Installation → Setup → Usage order. No Quick Start section.
- **NoelClay/academic-research-mcp-plugin** — `commands/learn.md`: description 94 chars ("Start a research-based learning session on any topic. Usage: /learn <topic>") — inlines argument hint in description rather than using the field. `skills/research-tutor/SKILL.md`: description 264 chars using YAML block-scalar.
- **SkinnnyJay/wiki-llm** — `skills/wiki-query/SKILL.md`: description 147 chars, `argument-hint: "<question about vault content>"` (typed). `commands/query.md`: no `name:`, description 78 chars.

### Recommendation

**Promote to a full Decisions subsection in the pattern doc.** Data depth now supports adoption-count claims across three sub-axes, matching the original main-survey recommendation but with concrete denominators:

1. **Description framing and length** — docs-prescribed trigger-verb form is followed by 9/14 sampled surfaces; bare "what it does" by 5/14. This is the sharp adoption-count finding for the description discoverability axis. Cross-references Dimension 2 recommendation (description quality), which suggested a docs-sourced subsection; this sample adds the adoption-count backing.
2. **`argument-hint` format drift** — four distinct forms observed across 9 argument-taking surfaces, with only the typed bracket form (`<query>`) aligned with ★ docs-prescribed examples. Four-variant drift is enough to warrant a Pitfalls callout or a conventions note pointing to the docs example.
3. **`name:` on commands vs SKILL.md** — commands omit `name:` 4/7 (matching BULDEE's defect note and anthropics' practice); SKILL.md includes `name:` 8/8. The asymmetry is load-bearing and docs-prescribed (★ skills-reference): directory-name fallback exists for both, but commands benefit from it for plugin namespacing while skills benefit from pinning the name so directory moves don't rename the skill. The main survey already recommended lifting the BULDEE defect into §5 Pitfalls; this sample confirms the pattern generalizes across Anthropic's own plugins.

README structure is too heterogeneous to claim a pattern — 4 distinct lead-in shapes across 10 repos, each internally coherent. Defer README structure to a style-guide addendum if ever warranted; not pattern-doc material today.

Fold-in location: new Decisions subsection under the existing **Plugin-component registration** section, or as a dedicated **Command and skill frontmatter** subsection since it now covers three first-class findings (framing, argument-hint, name:). The three findings share a consumer (Claude Code's description-matcher and slash-command router), so consolidating into one subsection serves the reader better than splitting across existing sections.

---

## 7b. Dimension 7 follow-up — targeted re-scan

**Scope.** Fixture-level testing conventions in plugins that ship test suites — `conftest.py` shape, fixture scoping, integration-test isolation mechanism, mock-vs-real backends, agent-subprocess test opt-in patterns.

**Sample.** 13 repos with Python or JS test suites (Cairn, Vortiago, CronusL, SkinnnyJay, AgentBuildersApp, Kanevry, BULDEE, Chachamaru, BaseInfinity, damionrashford, CodeAlive, NoelClay, Lykhoyda, ZhuBit). Conftest.py fetched and read on all repos where present (4 repos: Cairn ×2, Vortiago ×1, CronusL ×2, SkinnnyJay ×1). Test layouts inspected on all 13.

### Observation

**Python pytest adoption is thinner than the 54-repo narrative suggested.** Only 4/13 sampled repos actually ship a `conftest.py`: Cairn (2 files), Vortiago (1 file), CronusL (2 files), SkinnnyJay (1 file). Most "test-rich" repos in the research notes turn out to use shell scripts (Chachamaru with ~100 `test-*.sh` files; BaseInfinity similar; BULDEE no Python tests; damionrashford none), vitest/Node (Kanevry, AgentBuildersApp-adjacent), or `unittest` not pytest (AgentBuildersApp's 1,300-line single-class `unittest.TestCase` with method-level `setUp`/`tearDown`, no pytest fixtures). The narrative-reported "148 tests" in AgentBuildersApp is a single `unittest` module, not a pytest suite.

**Fixture scoping is deliberate where present.** The 4 pytest-using repos use session scope for expensive setup (Vortiago's Docker stack, SkinnnyJay's seeded vault, Cairn's session-metrics) and function scope for per-test isolation (Cairn's `integration_count`, CronusL's `tmp_project_dir` / `db_repository`, Vortiago's `mcp_session`). No repo uses module scope. Autouse appears in 1/4 (SkinnnyJay's `cleanup_claude`, which runs credential scrubbing before every test).

**Isolation mechanisms cluster into four patterns:**

- **tmp_path + in-memory databases** — Cairn's `temp_db` fixture (SQLite in `tmp_path`), CronusL's `"sqlite+aiosqlite://"` in-memory DB, SkinnnyJay's vault in `tmp_path`. Dominant pattern (3/4 of conftest-using repos).
- **Real Docker compose stack** — Vortiago's `outline_stack` session fixture spins `docker compose up -d` for the full MCP-plus-Outline stack, with real OIDC login via `httpx` and real `mcp_outline` server subprocess via `stdio_client`. 1/4 conftest-using repos; the only case of real external-service backing.
- **Real git tempdir** — AgentBuildersApp's `unittest.setUp` creates a fresh git-init'd temp repo per test method, spawns real `git` commands via `subprocess`, tests against actual adapter manifest files in `PLUGIN_ROOT / "adapters" / ...`. Real-subprocess-everywhere discipline, no mocking.
- **No isolation fixture at all** — ZhuBit ships pytest tests (`test_chunker.py`, `test_indexer.py`, etc.) without a conftest, relying on per-test setup in test files. 1/13.

**Mock usage is nearly absent.** Across all 4 conftest-using repos and the AgentBuildersApp unittest suite, **zero uses `unittest.mock`**. SkinnnyJay imports `lib.claude_env` for credential stripping (not mocking, just env-var scrubbing). CronusL replaces FastAPI lifespan context to suppress init/cleanup during tests — dependency injection, not mocking. Every repo tests against real backends (SQLite in-memory, real subprocess CLIs, real Docker containers, real git). This is a strong consistency signal: the claude-plugin ecosystem tests integration, not isolation.

**Real-subprocess tests against real CLIs are common where they matter.** Vortiago spawns real `mcp_outline` server via `sys.executable -m mcp_outline`; SkinnnyJay's `claude_runner` and `codex_runner` fixtures invoke the real `claude` and `codex` binaries from PATH, gated by environment variables `RUN_CLAUDE_TESTS` and `RUN_CODEX_SKILL_EVALS`; AgentBuildersApp invokes real hook scripts via subprocess. This is a partial analog to this project's `pytest.mark.agent` with `--run-agent` — the mechanism differs (env-var gate vs pytest marker) but the intent is identical: opt-in real-subprocess tests that cost tokens or external resources.

**No worktree-isolation fixture observed in the sample.** This project's `sandbox_worktree` fixture (wrapping `systems.sandbox`) remains unique in the corpus. The closest analog is AgentBuildersApp's real-git-tempdir pattern, which is git-init'd scratch dirs rather than worktrees on the actual repo — a different mechanism that doesn't share the main repo's object store.

**No `tests/fixtures/` directory convention.** Fixtures-as-data (test corpus files, mock inputs) are inconsistent: Cairn has an `external_project` fixture dir; Chachamaru has `tests/fixtures/` with scenario corpus; BaseInfinity has `tests/e2e/fixtures/` with 10+ mini-project fixtures (fresh-python, fresh-nextjs, legacy-messy, etc.) — genuine fixture-data directories. But no shared convention; each repo invents its own layout.

### Evidence

- **smcady/Cairn** — `tests/conftest.py` (110 lines): `metrics_recorder` (session), `_count_integration_tests` (function autouse). No `unittest.mock`, `subprocess`, or `tmp_path` imports at the top level — fixtures defer `tmp_path` to test parameters. `tests/integration/conftest.py` (27 lines): `temp_db` and `reset_cairn_registry`, default scope, `tmp_path`-based SQLite.
- **Vortiago/mcp-outline** — `tests/e2e/conftest.py` (~430 lines, 6 session-scoped fixtures): `outline_stack`, `_outline_credentials`, `outline_api_key`, `outline_access_token`, `mcp_server_params`, `mcp_session`. Uses `subprocess` to spawn `docker compose up -d`, real `httpx` for OIDC, real MCP server subprocess via `stdio_client`. No mocks.
- **CronusL-1141/AI-company** — `tests/conftest.py` (~30 lines): `tmp_project_dir`, `db_repository` (async, function scope). `tests/integration/conftest.py` (~65 lines): `integration_client`, `repo_and_client`. In-memory SQLite (`sqlite+aiosqlite://`), FastAPI lifespan replaced, no mocks.
- **SkinnnyJay/wiki-llm** — `tests/conftest.py` (385 lines): `cleanup_claude` (session autouse), `seeded_vault` (session tmp_path), `claude_runner` / `codex_runner` / `skill_eval_runner` (function). Imports `subprocess`, real CLI invocation gated by `RUN_CLAUDE_TESTS` / `RUN_CODEX_SKILL_EVALS` env vars.
- **AgentBuildersApp/eight-eyes** — `tests/test_collab_hooks.py` (~1,300 lines, 148 tests): single `unittest.TestCase` class, method-scoped `setUp`/`tearDown` with tempdir + real `git init`, tests invoke real hook scripts via `subprocess`, reads real `PLUGIN_ROOT / "adapters" / "copilot_cli" / "plugin.json"` manifest files. No pytest, no mocks.
- **Kanevry/session-orchestrator** — vitest (Node), not pytest; `tests/` tree with `hooks/`, `integration/`, `lib/`, `skills/`, `unit/`, `fixtures/`. Nested skill-local tests at `skills/vault-sync/tests/` with their own `package.json`.
- **ZhuBit/cowork-semantic-search** — `tests/` contains `test_chunker.py`, `test_indexer.py`, `test_mcp_tools.py`, `test_parsers.py`, `test_search.py`, `test_store.py` plus `helpers.py` — but no `conftest.py`. Per-test setup inline.
- **BULDEE, Chachamaru, BaseInfinity, damionrashford, CodeAlive-AI, NoelClay** — no `conftest.py`; test surfaces are shell scripts or bundled-helper Python only. The corpus-reported "extensive test suites" in these repos are bash-orchestrated, not pytest.
- **Lykhoyda/rn-dev-agent** — `tests/helpers.py`, `test_cli_smoke.py`, `test_setup_and_client.py`; default branch is not `main` so raw fetch 404'd, but the tree listing confirms three Python test files and no conftest.

### Recommendation

**Partially actionable — enough data for one focused Decisions subsection, not a broad one.** The Dim-7 main-survey conclusion ("not enough sample depth on fixture internals") is overturned by the deeper read on three specific axes where the data converges:

1. **Real-backend-over-mock is the de facto convention.** 0/5 Python test suites in the sample use `unittest.mock`. Every fixture goes after real backends (real SQLite in-memory, real subprocess CLIs, real Docker, real git). This is a strong enough consistency finding to document as a convention: "Claude-plugin test suites test integration end-to-end against real backends; mocking is nearly absent. Use in-memory databases and gated real-subprocess invocation for cost control." This matches this project's `testing.md` "Integration Tests Across Boundaries" guidance — observation and doctrine converge.
2. **Fixture scope discipline.** Session scope for expensive setup (Docker stack, seeded vault, metrics accumulator); function scope for per-test isolation; module scope unused. Worth a one-bullet note in the pattern doc since it's a consistent practice across 4/4 conftest-using repos.
3. **Opt-in real-subprocess / real-CLI tests.** SkinnnyJay's env-var gate (`RUN_CLAUDE_TESTS`) and this project's `pytest.mark.agent` (`--run-agent`) are the same pattern realized through different mechanisms. Worth surfacing as a named pattern for agent-spawning tests with cost implications.

Not actionable:

- **`conftest.py` structure** — too much shape variance across 4 repos for a shared template to emerge; each fits its own infrastructure.
- **Worktree isolation** — still unique to this project. The "not yet converged convention" framing from the main survey stands.
- **`tests/fixtures/` directory structure** — three repos have fixture dirs, each with a different layout; no shared convention to document.

Fold-in location: new Decisions subsection under the existing **Testing and CI** section (§13), scoped narrowly as "Fixture discipline" with the three findings above. Denominator: repos with Python test suites (4/13 sampled, ~10–15 across the full 54-repo corpus if extrapolated). The scoping caveat from the main survey ("not enough sample depth") is now resolved for these three axes; broader fixture conventions remain future-wave material.
