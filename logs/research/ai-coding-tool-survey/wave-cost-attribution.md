---
log-role: research-wave
status: v1 — 2026-05-18
scope: cost-attribution + quota-tracking implementation patterns for AI coding tooling, at personal and company scale
parent: consolidated.md
---

# Wave: Cost attribution and quota tracking

Cost-attribution for AI coding tools is now a non-trivial ecosystem with platform-native telemetry, a vibrant third-party tooling layer, OpenTelemetry GenAI semantic conventions stabilizing, and emerging FinOps practice. The consolidated doc's framing — that hooks are the right shape for quota/cost and that subscription-quota differs from API-dollar accounting — holds, but two of its specific gap claims now need refinement: (a) Anthropic *does* have programmatic usage/cost endpoints and a Compliance API analog to OpenAI's Compliance Logs Platform (launched Aug 2025), and (b) the bigger Claude Code gap is in *hook-event payloads* — token/cost data is still absent from `PostToolUse`/`Stop` payloads in May 2026, forcing third-parties to parse `~/.claude/projects/*.jsonl` transcripts out-of-band.

## Per-platform observability surface

### Claude Code / Anthropic

**Emitted at runtime:**
- **OpenTelemetry export** — opt-in via `CLAUDE_CODE_ENABLE_TELEMETRY=1` + standard OTLP env vars. Metrics: token usage by type (input/output/cache-create/cache-read), cost, session counters. Events for individual API calls and tool calls. Enterprise (OAuth) deployments add user identity (`user.email`, `user.account_uuid`, `organization.id`), MCP-server metadata, file-upload records. ([docs](https://code.claude.com/docs/en/monitoring-usage))
- **Local transcript JSONL** — `~/.claude/projects/<project>/<conversation-id>.jsonl` contains per-turn token counts, models, tool calls — *regardless of plan*. This is the data plane the third-party tooling layer reads. ([ccusage uses this](https://github.com/ryoppippi/ccusage))
- **Slash commands** — `/usage`, `/status`, `/stats`, `/cost` for in-session inspection. Surfaces 5-hour rolling window + 7-day weekly ceiling for subscription users; total cost + duration for API users.
- **Admin Usage & Cost API** — `/v1/organizations/usage_report/messages` (token consumption by model/workspace/service-tier) + `/v1/organizations/cost_report`. Admin API key required. ~5-min latency. ([reference](https://platform.claude.com/docs/en/api/admin/cost_report), [cookbook](https://platform.claude.com/cookbook/observability-usage-cost-api))
- **Compliance API** — launched 2026-04 / Aug 2025 depending on tier. ~30 typed events (auth, project lifecycle, conversation lifecycle, file uploads, SCIM). JSON/CSV export, SIEM-pushable to Splunk/Datadog/Elastic. ([docs](https://platform.claude.com/docs/en/manage-claude/compliance-api), [General Analysis review](https://generalanalysis.com/guides/claude-compliance-api))

**Notable gaps (verified May 2026):**
- **Hook event payloads still omit token/cost data** — `PostToolUse`/`UserPromptSubmit`/`Stop` receive session metadata but no token counts. Only the `Agent` tool's `PostToolUse` includes `tool_response.total_cost_usd` + `tool_response.usage`. ([issue #11008](https://github.com/anthropics/claude-code/issues/11008), [issue #52089](https://github.com/anthropics/claude-code/issues/52089), [issue #46089](https://github.com/anthropics/claude-code/issues/46089))
- **Compliance API does NOT capture** prompts, model invoked, tool calls, MCP traffic, sub-agent traces — only governance events. The detailed runtime data lives only in OTel exports and local JSONL.
- **No per-skill invocation telemetry** — session metadata tracks aggregate `Skill: 3` count but not which skill fired. Open feature request: [issue #35319](https://github.com/anthropics/claude-code/issues/35319).
- **Per-skill / per-plugin cost attribution is estimated, not measured** — Claude Code shows always-on tokens via the `count_tokens` API and proportionally scales on-invoke costs ([plugin reference](https://code.claude.com/docs/en/plugins-reference)).

### Codex CLI / OpenAI platform

**Emitted at runtime:**
- **OpenTelemetry export** — opt-in via `[otel]` table in `~/.codex/config.toml`, `otlp-http` or `otlp-grpc` exporters. Captures API requests, SSE/events, prompts, tool approvals/results, token usage, session activity. ([config reference](https://developers.openai.com/codex/config-advanced), [OTel PR #2103](https://github.com/openai/codex/pull/2103))
- **Slash commands** — `/status` for in-session limit checking. No `/cost` yet — [open feature request #117](https://github.com/openai/codex/issues/117), [open issue #5085](https://github.com/openai/codex/issues/5085).
- **Compliance Logs Platform — Codex Usage exports** — immutable time-windowed JSONL. Workspace usage (DAU, threads, turns, credits by surface), per-user usage (daily threads/turns/credits, optional emails), Code Review details (comments, reactions, priority findings). CSV or JSON. 30-day retention for ChatGPT-authenticated Codex; longer via Compliance Platform. ([governance docs](https://developers.openai.com/codex/enterprise/governance))
- **Pricing surface** — credits = pricing unit, billed per million input/cached-input/output tokens. ([pricing](https://developers.openai.com/codex/pricing))

**OpenAI Agents SDK:**
- **Guardrails framework does not include budget controls.** No `budget_usd`, no `on_exceed` hook, no token accumulation across a task. Confirmed by [OpenAI's own docs](https://openai.github.io/openai-agents-python/guardrails/) and [third-party critique](https://dev.to/pat9000/openais-guardrails-dont-control-costs-heres-the-gap-29j7). Blocking-mode guardrails *can* cost-optimize by short-circuiting before the agent runs, but that's adversarial not metered.
- Cost controls live one layer up — caller must instrument via OTel or wrap `Runner.run` with their own budget accumulator.

### Cross-platform / third-party

- **OpenTelemetry GenAI semantic conventions** — `gen_ai.client.token.usage` (histogram), `gen_ai.client.operation.duration`, computable `gen_ai.usage.cost_usd` from pricing tables. GenAI SIG active since April 2024; most conventions still *experimental* status as of March 2026. ([spec](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/))
- **Vendor integrations consuming Claude OTel:** Datadog ([Anthropic Usage and Costs integration](https://docs.datadoghq.com/integrations/anthropic-usage-and-costs/)), Grafana Cloud ([Anthropic integration](https://grafana.com/blog/how-to-monitor-claude-usage-and-costs-introducing-the-anthropic-integration-for-grafana-cloud/)), Honeycomb ([Anthropic monitoring](https://docs.honeycomb.io/integrations/anthropic-usage-monitoring)), SigNoz ([Claude Code monitoring](https://signoz.io/docs/claude-code-monitoring/)), Dynatrace ([Codex monitoring](https://www.dynatrace.com/hub/detail/openai-codex/)).
- **MCP audit/observability layer is gateway-shaped** — MCP servers don't emit enough natively; the pattern is a proxy/gateway (MintMCP, MCP Manager, MXCP, Datadog MCP Server) that intercepts tool calls and emits structured logs with correlation IDs. ([MCP-Manager checklist](https://github.com/MCP-Manager/MCP-Checklists), [Datadog MCP Server](https://docs.datadoghq.com/bits_ai/mcp_server/))

## Existing open-source implementations

Sorted by stars / relevance (verified May 2026):

| Repo | Stars | Last push | Purpose |
|---|---:|---|---|
| [ryoppippi/ccusage](https://github.com/ryoppippi/ccusage) | 14,349 | 2026-05-18 | Reference CLI: parses Claude Code + Codex local JSONL into daily/monthly/session/5-hour-block reports. `npx ccusage`. |
| [steipete/CodexBar](https://github.com/steipete/CodexBar) | 12,777 | 2026-05-18 | macOS menu-bar usage for Codex + Claude Code, no login |
| [Maciek-roboblog/Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) | 8,005 | 2025-09-14 | Terminal monitor, ML burn-rate prediction |
| [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | 3,012 | 2026-05-18 | Multi-tool token tracker (Claude Code, Codex, Cursor, Gemini, OpenCode, AmpCode, Kimi, more) with leaderboard |
| [phuryn/claude-usage](https://github.com/phuryn/claude-usage) | 1,553 | 2026-04-24 | Local dashboard, Pro/Max progress bar |
| [ColeMurray/claude-code-otel](https://github.com/ColeMurray/claude-code-otel) | 404 | 2025-06-17 | Full OTel + Grafana stack for Claude Code |
| [stormzhang/token-tracker](https://github.com/stormzhang/token-tracker) | 234 | 2026-05-18 | Statusline + CLI dashboard, rate-limit monitoring |
| [tobilg/ai-observer](https://github.com/tobilg/ai-observer) | 221 | 2026-03-29 | Unified local observability across AI coding assistants |
| [Piebald-AI/splitrail](https://github.com/Piebald-AI/splitrail) | 184 | 2026-05-18 | Cross-tool real-time tracker (Gemini/Claude/Codex/Qwen/Cline/Roo/Kilo/Copilot/OpenCode/Pi) |
| [mag123c/toktrack](https://github.com/mag123c/toktrack) | 140 | 2026-05-18 | Fast token+cost tracker |
| [egorfedorov/claude-context-optimizer](https://github.com/egorfedorov/claude-context-optimizer) | 50 | 2026-05-09 | Plugin: heatmaps, ROI reports, budget alerts, efficiency scores — PreToolUse hooks include read-cache + ContextShield |
| [Manavarya09/cost-guardian](https://github.com/Manavarya09/cost-guardian) | 31 | 2026-05-06 | Hard-mode budget enforcement: PreToolUse blocks tool calls when over budget; PostToolUse logs to SQLite |
| [boyand/cc-budget](https://github.com/boyand/cc-budget) | 27 | 2026-04-09 | Pacing-target budget intelligence; threshold warnings |
| [badlogic/cccost](https://github.com/badlogic/cccost) | 25 | 2026-05-05 | Instrument Claude Code for actual token+cost |
| [TechNickAI/claude_telemetry](https://github.com/TechNickAI/claude_telemetry) | 23 | 2025-10-24 | Drop-in `claude`→`claudia` wrapper, exports to Logfire/Sentry/Honeycomb/Datadog |
| [TylerGallenbeck/claude-code-limit-tracker](https://github.com/TylerGallenbeck/claude-code-limit-tracker) | 21 | 2026-05-18 | Statusline real-time subscription quota per model |

## Pattern catalog

**1. JSONL-transcript parsing (dominant for Claude Code).** Because hooks don't expose tokens, the ecosystem reads `~/.claude/projects/*.jsonl` out-of-band. Every major Claude tool (ccusage, claude-usage, phuryn/claude-usage, tokscale, splitrail) uses this. Cost = derive from token counts + a pricing table (often [LiteLLM's](https://github.com/BerriAI/litellm)). Works on all plans, including subscription.

**2. OTel export to backend dashboard.** Set `CLAUDE_CODE_ENABLE_TELEMETRY=1` + OTLP env vars; ship to Grafana/SigNoz/Honeycomb/Datadog. Same pattern works for Codex via its `[otel]` config block. The cross-platform-portable shape. Enterprise pattern of choice.

**3. Hook-based budget gate (Claude Code).** `SessionStart` initialises budget state, `PreToolUse` checks accumulated spend and blocks or warns, `PostToolUse` updates state (currently using JSONL re-read or `count_tokens` API since payload doesn't include usage). cost-guardian, cc-budget, claude-context-optimizer exemplify this.

**4. Statusline as real-time meter.** Cheap, always-visible, doesn't require backend infrastructure. ohugonnot/claude-code-statusline, TylerGallenbeck/claude-code-limit-tracker, stormzhang/token-tracker. Reads `/api/usage` endpoint or local JSONL on a 60s tick.

**5. CI/CD budget flags (Claude Code).** `claude -p --max-turns N --max-budget-usd X` for hard ceilings on non-interactive runs. Native, no hooks needed.

**6. MCP gateway as audit emitter.** Sit a proxy between agents and MCP servers, emit structured logs with correlation IDs (tool name, args, user, session, duration). MCP Manager, MintMCP, MXCP, Datadog MCP Server. The only audible layer for tool-call-level activity that survives the hook-event-payload gap.

**7. Per-skill estimation by static analysis.** No runtime per-skill cost telemetry. Claude Code reports plugin always-on cost via `count_tokens` and proportionally scales per-component on-invoke estimates. True per-invocation attribution is open feature request territory.

**8. Subscription-quota tracker (the footgun fix).** Different mental model: track 5-hour rolling window % and 7-day weekly ceiling %, not dollars. Surface as statusline pill (red/yellow/green). Maciek-roboblog/Claude-Code-Usage-Monitor and TylerGallenbeck/claude-code-limit-tracker are the canonical implementations. Distinct code paths from API-dollar tools — sometimes both in one app (ccusage, phuryn/claude-usage, CodexBar).

**9. FinOps-for-AI allocation primitives.** Four allocation problems per [Finout's framework](https://www.finout.io/blog/finops-for-ai-agents-a-four-step-allocation-framework): per-developer (IDE assistants), per-team (embedded agents), per-customer (AI features), shared back-allocation (untaggable). Industry tools: Finout, Holori, Amnic, nOps, Cloudchipr. FinOps Foundation now has a [FinOps for AI working group](https://www.finops.org/wg/finops-for-ai-overview/) and a [GenAI Cost & Usage Tracker guide](https://www.finops.org/wg/how-to-build-a-generative-ai-cost-and-usage-tracker/). No published case study I could find specifically on *AI-coding-tool chargeback at company scale* — the literature is still mostly about LLM API spend in general, not Claude-Code-vs-Codex IDE assistant allocation.

## Verification of consolidated.md claims

| Claim (in consolidated.md) | Status | Evidence |
|---|---|---|
| Hooks-based governance covers "quota tracking — count tokens per session/project, alert at thresholds" | **Verified for Codex, partially refuted for Claude Code** | Codex OTel + Compliance Platform yes. Claude Code hooks *don't* receive token counts as of May 2026 (issues [#11008](https://github.com/anthropics/claude-code/issues/11008), [#52089](https://github.com/anthropics/claude-code/issues/52089)) — third-parties work around via JSONL parsing |
| "Anthropic has no analog to Compliance Logs Platform" / "Anthropic has audit but less unified" | **Refuted** | Anthropic Compliance API ([docs](https://platform.claude.com/docs/en/manage-claude/compliance-api)) launched Aug 2025, ~30 typed events, JSON/CSV export, SIEM push to Splunk/Datadog/Elastic. Enterprise-tier only. Narrower scope than OpenAI's (no prompts, no model invoked, no tool calls) but it exists |
| Usage & Cost Admin API gap on Anthropic side | **Refuted** | Anthropic has [/v1/organizations/usage_report/messages](https://platform.claude.com/docs/en/api/admin/cost_report) + `/v1/organizations/cost_report` since 2025; Finout calls it the "Enterprise Analytics API" |
| OpenAI Agents SDK guardrails enforce cost | **Refuted** | [OpenAI docs](https://openai.github.io/openai-agents-python/guardrails/) confirm guardrails are input/output/tool validation; no budget primitive |
| Claude Max / Pro burns quota not dollars; API-cost thinking is wrong mental model | **Verified** | Anthropic [help center](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan) confirms 5h rolling + 7d weekly limits; `/usage` and `/status` are the native surfaces. Agent SDK on subscription now draws from separate monthly credit bucket effective 2026-06-15 |
| Per-skill cost attribution is not native | **Verified** | Open feature request [#35319](https://github.com/anthropics/claude-code/issues/35319). Plugin reference confirms costs reported per-component but on-invoke is estimated, not measured |
| OpenAI Codex compliance exports include per-user/per-workspace breakdown | **Verified** | [Codex governance docs](https://developers.openai.com/codex/enterprise/governance) detail CSV/JSON export with workspace usage, per-user usage (optional emails), Code Review details |
| Anthropic publishes some MCPs but doesn't curate a reviewed connector tier | **Verified** (out of scope for this wave but observed) | No reviewed-connector catalog surface found on Anthropic side |

## Open questions for next pass

- **Anthropic Compliance API expansion** — when (if?) will the event set include prompts/model/tool-calls? Currently it's identity-and-lifecycle only, leaving the runtime layer to OTel-only. The competitive pressure from OpenAI's broader Codex Usage exports is visible but no public roadmap.
- **Per-skill / per-plugin cost attribution in Claude Code** — issue [#35319](https://github.com/anthropics/claude-code/issues/35319) is open since 2025; no signal on shipping. Workaround: skills emit `console.log(JSON.stringify({skill: 'X', ts: ..., ...}))` at invocation and pair with JSONL token deltas — no one has published this pattern yet, opportunity to author.
- **Subscription-quota emit to hooks** — when Anthropic exposes 5h-window % and weekly % to hook stdin, hook-based budget gates become first-class for subscription users (currently they're only viable for API-key users via cost). Tracking via [#52089](https://github.com/anthropics/claude-code/issues/52089).
- **Codex hook payload parity** — does Codex's `PostToolUse` include token counts? Couldn't verify from public docs; would close the cross-platform asymmetry if yes.
- **Published FinOps case studies on AI *coding tool* chargeback specifically** — generic LLM-spend case studies are plentiful, but IDE-assistant-per-developer allocation stories at enterprise scale are thin. May be too early in adoption curve; revisit Q3 2026.
- **OPA / Rego integration with hooks** — consolidated doc flagged this; this wave didn't find concrete examples of cost-policy-as-Rego for Claude Code or Codex hooks. Conceptually viable but unbuilt.
- **MCP-emitter pattern for personal use** — the gateway pattern presumes infrastructure; is there a lightweight per-machine MCP audit-emitter usable on a personal multi-project setup? `tobilg/ai-observer` is the closest. Worth a deeper look for personal-scope alignment.
