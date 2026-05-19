---
log-role: recommendation
status: draft v1 — for Modern Campus, OpenAI-licensed multi-team org
basis: synthesis of `consolidated.md` against Modern Campus's profile
---

# Recommendation: AI Coding Tool Stack for Modern Campus

A "winning" framework / choice stack for an OpenAI-licensed higher-ed-tech org with tens of developers and four-to-five-digit monthly API spend.

## Profile

- **Org:** Modern Campus — higher education technology (CRM, web content management, catalog, lifelong learning). North American customer base. Acquired Destiny One, OmniUpdate, and others; product portfolio spans the academic-experience lifecycle.
- **Scale:** tens of developers actively using AI coding tooling. Cross-team alignment is a real concern, not theoretical.
- **Cost:** four-to-five-digit monthly API spend on OpenAI. Growing. Cost attribution and quota gating are decision-relevant *now*, not later.
- **Vendor commitment:** OpenAI licensing in place. Sunk cost in accounts, training, workflows.
- **Data sensitivity:** FERPA (student records) baseline; possible HIPAA exposure if any product touches medical-school clinics or health records; accessibility (ADA / Section 508) for client-facing surfaces.

## TL;DR — the recommendation

**Stay OpenAI-primary. Adopt Codex CLI as the IDE agent. Build internal alignment on top of Codex + Workspace Agents + the OpenAI Compliance/admin stack. Adopt AGENTS.md as the cross-tool substrate to future-proof against vendor shifts, without paying multi-vendor duplication cost today.**

The single biggest win is consolidating onto Codex CLI as the primary IDE coding agent. As of May 2026, Codex ships full alignment-shape parity with Claude Code (plugins, hooks, subagents, `SKILL.md` skills, MCP, layered config, enterprise floor, OS-enforced sandboxing) on top of the open AGENTS.md substrate, with two material advantages over Claude Code for this profile: (a) hook payloads include token deltas — enables real-time quota gating that Claude Code currently can't do natively; (b) Apache 2.0 source — forkable if you need to. Combined with the fact that you're already paying OpenAI, the alignment payoff per dollar is highest here.

Adopt AGENTS.md as the substrate for memory files, skills, and plugin paths. This both standardizes within Modern Campus *and* preserves the option to add Claude Code, Cursor, Gemini CLI, or others later without re-doing alignment work — they all read AGENTS.md.

The most decision-blocking near-term gap is cost observability: build the OTel pipeline early, before spend doubles.

## The recommended stack

### Layer 1 — IDE agent (primary)

**Adopt: [OpenAI Codex CLI](https://github.com/openai/codex)** as the standard IDE agent across all engineering teams.

Why:

- Zero additional licensing cost — already on OpenAI.
- Shape parity with Claude Code (see [consolidated.md platform matrix](./consolidated.md#platform-applicability-matrix)).
- **Hook payloads include token deltas** — this enables real-time quota gating that Claude Code currently cannot do natively (its hook payloads omit token/cost data for `PostToolUse`, `Stop`, `UserPromptSubmit`).
- **OS-enforced sandbox** (Seatbelt on macOS, bwrap+seccomp on Linux, WSL2 on Windows) — `read-only` / `workspace-write` / `danger-full-access` modes give explicit safety floors.
- **Apache 2.0** source — forkable if a critical feature gap surfaces.
- **Unified product family** — same `config.toml` and plugin/skill stack across CLI, IDE extension, desktop app, Codex Cloud, and ChatGPT-side Codex.

Concrete next steps:

- Pilot Codex CLI with one team for 4 weeks to validate the workflow shift.
- Roll a baseline `.codex/config.toml` + `AGENTS.md` template to all engineering repos.
- Author a starter `~/.codex/agents/` set of subagents matching team specializations (review, search, plan, test).

### Layer 2 — Production agents and automation

**Use: [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) (Python or TS)** for production agent services, batch jobs, and customer-facing AI features.

Why:

- Same OpenAI auth as everything else — no separate credential surface.
- RunHooks + AgentHooks + three guardrail families (input / output / tool) — programmatic governance lives in code with the agent.
- Same MCP transport set as Codex — tool definitions transfer between IDE and production.
- Tight integration with the Responses API and its server-hosted versioned Prompts (a real Anthropic gap).

**Use: [Workspace Agents](https://openai.com/academy/workspace-agents/)** for team-owned automation — scheduled jobs, PR review, doc generation, support triage, sales workflow.

Why:

- Workspace-scoped (not per-user) — team-owned, admin-curated automation.
- 60+ pre-integrated connectors plus custom MCP servers.
- Credit-based billing isolates team automation cost from engineering API spend.
- Direct replacement for any Custom GPTs you have (those are phasing out — migrate before forced).

### Layer 3 — Sharing and distribution

**Build: an internal [Codex plugin marketplace](https://developers.openai.com/codex/plugins)** in a private GitHub repo as the canonical place for shared skills, hooks, MCP servers, and agent definitions.

Why:

- `.codex-plugin/marketplace.json` is the native registry shape; teams `codex plugin marketplace add` and `codex plugin install <name>`.
- Versioned via git tags — projects pin specific versions; updates flow through deliberate bumps, not surprise mutations.
- One canonical source of FERPA-aware skills, internal-API MCP servers, and review/release hooks.

Concrete plugins to author first (in order of payoff):

1. **`mc-baseline`** — baseline `AGENTS.md`, project-starter scaffolding, standard hook set (audit log emitter, pre-flight cost estimator).
2. **`mc-ferpa-guard`** — path-scoped rules + `PreToolUse` hook that prevents tool use on student-record paths without explicit confirmation; emits to Compliance Logs.
3. **`mc-internal-mcp`** — MCP servers for internal APIs (CRM, catalog, lifelong-learning systems) so devs don't reach for ad-hoc HTTP requests.
4. **`mc-review`** — PR review skill set + subagent specializations tuned to the codebase.
5. **`mc-release`** — release-cut workflow, changelog generation, deploy gating hooks.

**Adopt: [AGENTS.md](https://agents.md/) as the memory-file convention.** Standardize on `AGENTS.md` at repo root for every project; skills live under `.agents/skills/` (Codex reads this natively). Avoid Codex-specific path proliferation.

Why:

- 60k+ projects on the substrate. If you ever add Cursor, Gemini CLI, GitHub Copilot Coding Agent, JetBrains Junie, or opencode (any reason — cost shift, feature gap, contract requirement), they all read AGENTS.md. Future-proofs without paying portability tax today.
- Eliminates the "which file convention do we use?" question for new repos.
- Codex CLI tools and the broader AGENTS.md ecosystem can read the same content.

### Layer 4 — Governance and admin

**Centralize: [admin.openai.com](https://help.openai.com/en/articles/12289294-global-admin-console)** as the single governance surface.

Why:

- Tenant-level SSO + SCIM across ChatGPT workspaces *and* API orgs — single identity tenant for Modern Campus.
- IP allowlists, domain verification, custom RBAC roles, feature flags per workspace.
- Built-in foundation for the Compliance Logs Platform.

**Lock: [`requirements.toml`](https://developers.openai.com/codex/enterprise/admin-setup)** as the enterprise floor for Codex CLI.

Configure:

- `allow_managed_hooks_only = true` — only IT-blessed hooks run; prevents per-developer hook drift.
- `[features]` enforcement — selectively disable risky tool surfaces.
- `managed_dir` — central hook script directory deployed via MDM.
- Plugin allow/block policy — only sanctioned plugin marketplaces.
- `forced_login_method` + `forced_chatgpt_workspace_id` — every Codex session ties to the Modern Campus workspace identity.

Deploy via MDM (Jamf, Kandji, or Intune depending on fleet) using macOS Managed Preferences `.mobileconfig` profiles. Engineering laptops pick up the floor automatically; devs cannot bypass.

**Stream: [Compliance Logs Platform](https://help.openai.com/en/articles/11509118-admin-controls-security-and-compliance-in-apps-enterprise-edu-and-business)** to your SIEM (Splunk / Datadog / Sumo Logic / S3 — whichever you run).

Three log streams to enable:

- **Admin Audit** — every workspace/admin action, who changed what.
- **User Auth** — login/logout, MFA events, session lifecycle.
- **Codex Usage** — Codex CLI activity including prompts, tool calls, completions. **Critical for FERPA audit** — captures the full conversation surface.

Default retention is 30 days; budget for longer-retention copies in your own data lake if FERPA / corporate retention requires more.

### Layer 5 — Cost attribution and quota control

Given four-to-five-digit monthly spend with tens of developers, cost observability is decision-blocking *now*. Build this in Phase 1, not Phase 3.

**Enable: OpenTelemetry emission via Codex `[otel]` block** in `config.toml`. Pipe to whatever you already run (Datadog, Grafana, Honeycomb, SigNoz). The [GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/) standardize fields; this is the most portable telemetry path.

**Build: pre-flight cost estimation hooks.** Codex hook payloads include token deltas (Claude Code's don't yet) — use `PreToolUse` to estimate tool-call cost before running and warn or block above thresholds.

**Build: per-team cost dashboards.** Tag every Codex session, Agents SDK run, and Workspace Agent execution with `team`, `project`, and `cost-center` labels. Roll up in Datadog/Grafana for monthly review.

**Audit pattern: quarterly which skills / projects spend most.** Cut or refactor outlier skills that don't earn their cost. Top-10 spend list, every quarter.

**Consider: Workspace credits for batch workloads.** If you have predictable batch usage (nightly doc generation, periodic data enrichment), Workspace Agents' credit-based billing is often cheaper per-unit than direct API calls.

## Compliance considerations (higher-ed-tech-specific)

### FERPA (always relevant)

Student records exposure means audit trails of agent activity on those code paths are decision-relevant. Strategy:

- **Path-scoped rules** in Codex (skill frontmatter `paths` field) — flag student-data-handling repos / directories.
- **`PreToolUse` hook** for FERPA-sensitive paths — require explicit confirmation, emit to Compliance Logs Platform.
- **Compliance Logs Platform Codex Usage stream** — your FERPA audit substrate. Retain ≥ 7 years if institutional policy requires.
- **Documented data-flow map** showing where student data may transit agent context — separates "agent helps write code that touches student data" (low risk) from "agent's context window contains student data" (audit-relevant).

OpenAI's Trust Portal covers SOC 2 Type II and ISO 27001/27017/27018/27701 — review for FERPA-related contractual coverage.

### HIPAA (if applicable)

**Gap: OpenAI does not publish a HIPAA BAA.** If any Modern Campus product touches PHI (medical-school clinics, student health records), the OpenAI path doesn't cover you. Two options:

1. **[Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)** via your Azure tenant — Microsoft's BAA covers the deployment. Same models, BAA-covered.
2. **[Anthropic API](https://docs.anthropic.com/) (Claude)** — published HIPAA BAA. Only worth introducing as a second vendor if HIPAA is a real ongoing requirement.

For the engineering org's IDE work that doesn't touch PHI, Codex CLI on standard OpenAI is fine. The HIPAA gap is product-side, not tooling-side.

### Federal / government higher-ed contracts

If you bid on federal-funded research compliance work or government higher-ed contracts requiring FedRAMP High, OpenAI is FedRAMP Moderate; Anthropic Claude for Government is FedRAMP High but does not currently include Claude Code. The best-positioned vendor for FedRAMP High *plus* IDE coding agent today is [Windsurf](https://windsurf.com/) (FedRAMP High + ITAR + IL4/IL5 via Palantir FedStart). Worth considering only for the contract subset that requires it — not as a primary tool.

### Accessibility (Section 508 / WCAG)

Tooling-side: not impacted directly.
Product-side: AI-generated code touches accessibility-critical interfaces. Author a `mc-a11y` skill that loads accessibility conventions when working on client-facing UI repos — automated lint-and-suggest at authoring time, cheaper than retrofitting at review time.

## Phased rollout

### Phase 1 (Month 1): Foundation and observability

- **Pick a pilot team** (5-10 devs). Install Codex CLI; install Codex IDE extension where they use VS Code / JetBrains. Authenticate via the Modern Campus OpenAI workspace.
- **Set up [admin.openai.com](https://help.openai.com/en/articles/12289294-global-admin-console)** — tenant configuration, SSO, SCIM provisioning, IP allowlists.
- **Enable [Compliance Logs Platform](https://help.openai.com/en/articles/11509118-admin-controls-security-and-compliance-in-apps-enterprise-edu-and-business)** — Admin Audit, User Auth, Codex Usage streams to your SIEM.
- **Wire OpenTelemetry** — Codex `[otel]` block → existing observability stack. First dashboards: per-team API spend, per-skill invocation count.
- **Author `mc-baseline` plugin** — minimal `AGENTS.md`, baseline hooks, project starter.

Outcome at end of Phase 1: pilot team productive on Codex; you have cost visibility per team; audit trail in place.

### Phase 2 (Month 2-3): Standardization and policy

- **Deploy `requirements.toml` via MDM** — engineering laptops get the enterprise floor automatically.
- **Stand up the internal Codex plugin marketplace** in a private GitHub repo. Publish `mc-baseline`, then `mc-ferpa-guard` and `mc-internal-mcp`.
- **Migrate any Custom GPTs to Workspace Agents** — phase-out deadline already announced; don't wait for forced migration.
- **Author internal MCP servers** for the 2-3 most-requested internal APIs.
- **Establish skill authoring conventions** — `SKILL.md` frontmatter standards, naming, ownership.

Outcome at end of Phase 2: governance floor enforced; shared skills/plugins in place; teams are starting to compose on top of the foundation.

### Phase 3 (Month 4-6): Scale and refine

- **Roll Codex to all engineering teams.** Run a 1-day workshop per team on the agreed conventions.
- **Build per-team cost dashboards** — monthly burn, top-10 skills by cost, anomaly alerts.
- **Pilot Workspace Agents for non-engineering teams** — sales (proposal generation, RFP triage), support (ticket triage, knowledge-base authoring), product (PRD drafting).
- **Quarterly governance review:** which skills earn their cost? Which plugins are underused? What's missing?

Outcome at end of Phase 3: org-wide alignment, predictable cost growth, clear governance review cycle.

## What NOT to do (footguns for this profile)

### Don't dual-deploy Claude Code "to keep options open"

Single-vendor alignment beats portability at your scale. Adopting AGENTS.md as the substrate preserves the option of adding Claude Code later — you don't need to pay the duplicate-config tax today. The plug-skill-hook-subagent-MCP stacks are shape-equivalent; running both means doing alignment work twice. Revisit only if a specific Claude Code feature becomes decision-blocking.

### Don't lean on Custom GPTs

They're phasing out (Workspace Agents replaces them). Migrate now; don't accumulate workflows on a deprecated platform.

### Don't dump every convention into AGENTS.md

Cap it at a few hundred lines. Use path-scoped rules (skill `paths` frontmatter) for situational discipline. AGENTS.md every-line burns context every turn — bloat is the failure mode for memory files.

### Don't author one Mega-plugin

Author small focused plugins (`mc-baseline`, `mc-ferpa-guard`, `mc-review`, `mc-release`) and let them compose. Plugin dependencies (semver-pinned) are first-class; the Mega-plugin trap is unnecessary in 2026.

### Don't fragment governance per-team

One `requirements.toml` from IT, deployed via MDM. Teams own their plugin marketplace contributions; IT owns the enforcement floor. Permission rules merge across scopes — central + project layering composes well as long as the floor stays minimal.

### Don't gate cost with hooks alone if cost-blocking is critical

OpenAI Agents SDK guardrails are NOT org-wide policy by design. For hard cost limits, pair hook-side estimation with a server-side budget check (e.g., Workspace credits or a custom MCP that enforces a per-team budget). Hooks are advisory; the budget is authoritative.

### Don't ignore the OpenAI BAA gap if PHI is in scope

If even one product line touches PHI, route that subset through Azure OpenAI Service (Microsoft's BAA covers it) or Anthropic API (published BAA). Don't assume general OpenAI usage covers it — it doesn't.

## When to revisit the single-vendor decision

Single-vendor commitment is the right posture *today* given the constraints. It's not permanent. Revisit when:

- **Federal / government contracts require FedRAMP High** — Windsurf (FedRAMP High + ITAR via Palantir FedStart) becomes the natural fit for that contract subset. Don't migrate everything; route the contract-specific work.
- **HIPAA scope expands** — Azure OpenAI Service or Anthropic API for the PHI-touching subset.
- **A specific Codex limitation becomes decision-blocking** — track the [feature delta vs. Claude Code](./consolidated.md#platform-applicability-matrix). Likely candidates: Claude Code's 31-event hook taxonomy, Channels for server-pushed events, native skill router, LSP plugin bundling. Add Claude Code only if one of these matters operationally.
- **OpenAI pricing or service quality shifts adversely** — the AGENTS.md substrate means migration cost is mostly skill-translation, not full-stack rewrite. You're not locked in.
- **A regulated-industry acquisition lands** — re-run the compliance posture analysis for the acquired entity's data class.

The substrate adoption (AGENTS.md) is the optionality hedge. Maintain it deliberately even when single-vendor is working.

## Open questions for follow-up

- **Modern Campus's current FERPA audit policy** — does the 30-day Compliance Logs default retention meet contractual requirements? If not, what's the data-lake retention target?
- **PHI scope** — does any current or planned product touch student health records, clinic operations, or other PHI? Determines whether the Azure OpenAI / Anthropic-API hedge is needed.
- **Existing observability stack** — Datadog, Grafana, Honeycomb, or something else? Determines the OTel pipeline target.
- **MDM substrate** — Jamf, Kandji, Intune, or none? Determines whether `requirements.toml` deployment is automatic or manual.
- **Cross-team variance in current AI tooling** — are some teams already on Cursor, GitHub Copilot, or Claude Code? Document the migration cost vs. accept a hybrid for 6 months.

## Sources

- This recommendation is a synthesis of the AI coding tool survey in [`consolidated.md`](./consolidated.md) and its wave reports.
- Vendor docs cited throughout link to canonical sources.
- Cost-attribution patterns from [`wave-cost-attribution.md`](./wave-cost-attribution.md).
- Compliance posture from [`wave-compliance-audit.md`](./wave-compliance-audit.md).
- Cross-vendor capability data from [`wave-multi-vendor-adopters.md`](./wave-multi-vendor-adopters.md) and the HTML matrix at [`wave-multi-vendor-adopters.html`](./wave-multi-vendor-adopters.html).
