---
log-role: reference
status: wave-survey — OpenAI counterpart to consolidated.md alignment shapes
sampled: 2026-05-18
---

# Wave: OpenAI platform survey

Mirrors `consolidated.md`'s shape catalog from the OpenAI side. Covers OpenAI's developer + enterprise platform — Assistants API (sunsetting), Responses API + Agents SDK, ChatGPT Enterprise/Business + Workspace Agents, Codex enterprise, Realtime API, MCP support, Operator/Computer Use, hooks/guardrails.

## Offerings inventory

### Assistants API (sunsetting)
- **What:** Stateful agents-on-OpenAI primitive — threads, tools, file search — created and managed per-API-organization. Holds per-thread conversation state on OpenAI's side.
- **Alignment shape:** Org-scoped assistant objects, per-user threads, shared tool definitions on the assistant object. Sharing is by assistant id within an API project; no marketplace.
- **Maps to consolidated.md shape:** Similar to **Managed Agents (#13)** in that OpenAI hosts state and governance; weaker on RBAC and audit.
- **Canonical URL:** [Assistants migration guide](https://developers.openai.com/api/docs/assistants/migration)
- **Recent (post-2026-01):** Deprecation announced; shutdown **August 26, 2026**. Migration target is the Responses API.

### Responses API (+ reusable Prompts)
- **What:** Unified agentic-loop API replacing Chat Completions + Assistants. Single request can drive multi-tool loops (web_search, file_search, code_interpreter, computer_use, remote MCP servers, custom functions). Includes a server-side **Prompts** object with versioning, diff, rollback, and `prompt_id` + optional `version` references.
- **Alignment shape:** Project-scoped prompt library shared by all users in a project — one canonical definition, code references `id` (with optional pin). Snapshots / diffs / rollbacks built in.
- **Maps to consolidated.md shape:** Closest to **Plugin marketplace (#2)** for *prompts only* (versioned, registry-style, shared by reference) plus **Layered configuration (#1)** semantics (pin vs latest). No analog in Anthropic-land for *server-hosted versioned prompts*.
- **Canonical URL:** [Responses API reference](https://developers.openai.com/api/reference/responses/overview); [Migrate to Responses](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- **Recent (post-2026-01):** Reusable prompts shipped with versioning + dashboard UI; `custom tool call` type, image/file as tool-call output added.

### OpenAI Agents SDK (Python + JS)
- **What:** Production SDK for multi-agent workflows. Primitives: Agent, Runner, Tools, Handoffs, Guardrails, Sessions, Sandbox Agents. Successor to Swarm (now archived/educational). v0.17.2 as of May 2026.
- **Alignment shape:** Code-as-config — agents, tools, guardrails are Python/TS classes. Sharing happens via normal package mgmt (PyPI, npm). No native registry; no managed runtime.
- **Maps to consolidated.md shape:** **Claude Agent SDK (#12)** — direct analog. Same shape, same caveats (config/governance not shared with the IDE-side product).
- **Canonical URL:** [openai-agents-python docs](https://openai.github.io/openai-agents-python/); [GitHub](https://github.com/openai/openai-agents-python)
- **Recent (post-2026-01):** Sandbox Agents (v0.14), Realtime voice agents on `gpt-realtime-2`, full MCP support across 5 transport variants.

### Agents SDK Guardrails + Lifecycle Hooks
- **What:** Three guardrail families (input, output, tool — via `@input_guardrail` / `@output_guardrail` / `@tool_input_guardrail` / `@tool_output_guardrail`) plus **RunHooks** (global to a run) and **AgentHooks** (per agent). Hook surface includes `on_llm_start/end`, `on_agent_start/end`, `on_tool_start/end`, `on_handoff`.
- **Alignment shape:** Decorator-attached, co-located with agent/tool definitions. Per-tool `needs_approval` enables HITL; run pauses with serializable `state`. Documentation explicitly notes agent-level guardrails are *not* org-wide — "place validation next to the tool that creates the side effect."
- **Maps to consolidated.md shape:** Similar to **Hooks-based governance (#5)** but scoped to the SDK process, not the IDE/agent runtime. No org-wide hook registry; no analog to Claude Code's `settings.json`-declared `PreToolUse`.
- **Canonical URL:** [Guardrails](https://openai.github.io/openai-agents-python/guardrails/); [Lifecycle](https://openai.github.io/openai-agents-python/ref/lifecycle/); [Guardrails & approvals guide](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- **Recent (post-2026-01):** Tool-input/output guardrail decorators standardized; HITL state serialization.

### MCP support across OpenAI products
- **What:** OpenAI ships MCP as a first-class tool transport. Five integration modes in the Agents SDK: **Hosted MCP** (Responses API executes server-side), Streamable HTTP, SSE (deprecated), stdio, and MCP Server Manager. ChatGPT Apps also speak MCP — apps implement `search` + `fetch` and connect via OAuth (CIMD).
- **Alignment shape:** Workspace-scoped OAuth-connected MCP apps; hosted MCP delegates auth + execution to OpenAI. Workspace Agents pull from an OpenAI-reviewed catalog of MCP connectors (Amplitude, Stripe, Vercel, Hex, etc.).
- **Maps to consolidated.md shape:** **Internal MCP servers (#4)** — same protocol, similar governance shape. OpenAI adds a *reviewed-connector tier* that doesn't exist in Anthropic-land.
- **Canonical URL:** [MCP servers for ChatGPT Apps + API](https://developers.openai.com/api/docs/mcp); [Agents SDK MCP](https://openai.github.io/openai-agents-python/mcp/)
- **Recent (post-2026-01):** OpenAI-reviewed MCP connector tier launched alongside Workspace Agents (April 22, 2026).

### Custom GPTs (legacy, being phased out)
- **What:** Bundle of instructions + actions (OpenAPI) + knowledge files + capability toggles, authored in ChatGPT. Sharable private / workspace / link / public-store. Workspace admins control GPT creation, sharing modes, and allowed action domains.
- **Alignment shape:** Per-user authoring with workspace-admin guardrails (approved-domain allowlist for actions, sharing-mode toggles). No versioning surface; no programmatic update flow.
- **Maps to consolidated.md shape:** Similar to **Plugin marketplace (#2)** in spirit (shared bundles) but personal-first, not org-first. Closer to a per-user appliance than a marketplace.
- **Canonical URL:** [Managing GPT access in Enterprise/Edu](https://help.openai.com/en/articles/8555535-gpts-chatgpt-enterprise-version)
- **Recent (post-2026-01):** Being replaced by **Workspace Agents** (below); phase-out announced April 22, 2026.

### Workspace Agents (Custom GPT successor)
- **What:** Team-owned, always-on automation workers powered by Codex. Scheduling, long-running tasks, 60+ enterprise connectors, custom MCP servers, admin controls. Launched April 22, 2026 on Business/Enterprise/Edu/Teachers.
- **Alignment shape:** Workspace-scoped agents (not per-user). Centralized admin controls over which connectors are enabled, scheduling, billing (credit-based after May 6, 2026). Shared resources rather than personal bundles.
- **Maps to consolidated.md shape:** **Managed Agents (#13)** — direct counterpart. Stronger on workspace ownership semantics than Anthropic's current managed-agents offering.
- **Canonical URL:** [Workspace Agents overview](https://openai.com/academy/workspace-agents/); [Reworked coverage](https://www.reworked.co/digital-workplace/openai-launches-workspace-agents-for-enterprise-workflow-automation/)
- **Recent (post-2026-01):** Entirely new — April 22, 2026 launch.

### ChatGPT Enterprise / Business / Edu + Global Admin Console
- **What:** Tiered subscription product with workspace admin console (workspaces.openai.com) and **Global Admin Console** at admin.openai.com — tenant-level control plane spanning multiple ChatGPT workspaces *and* API orgs under one SSO + verified-domains tenant.
- **Alignment shape:** Hierarchical: Tenant → Workspaces/API-orgs → Groups/Roles → Users. SSO (SAML), SCIM provisioning, IP allowlists, domain verification, custom RBAC roles, feature flags per workspace, app/integration enable-disable, Compliance Logs Platform (immutable JSONL exports: Admin Audit, User Auth, Codex Usage), GPT/action domain allowlist.
- **Maps to consolidated.md shape:** **Enterprise managed settings (#6)** + **Internal developer portal (#11)** combined. OpenAI's central console is *more vertically integrated* than Claude Code's managed-settings file approach — single UI, multi-product reach.
- **Canonical URL:** [Global Admin Console](https://help.openai.com/en/articles/12289294-global-admin-console); [Admin controls & compliance](https://help.openai.com/en/articles/11509118-admin-controls-security-and-compliance-in-apps-enterprise-edu-and-business)
- **Recent (post-2026-01):** Global Admin Console launched in 2026; Compliance Logs Platform with Codex Usage logs new this year.

### OpenAI Codex (CLI + IDE + Cloud) with hooks + AGENTS.md
- **What:** OpenAI's IDE-adjacent coding agent. Local (CLI/IDE) and cloud variants. Configured via `config.toml`, `managed-requirements.toml` (admin-locked, user-non-overridable), and `AGENTS.md` files discovered by walking from cwd to project root. **Hooks** went GA in 2026 — scripts injected into the agentic loop, observing MCP tools, `apply_patch`, and long-running bash.
- **Alignment shape:** Mirrors Claude Code almost exactly — layered config + project memory file + hook scripts + managed admin-floor. Workspace-owner enables Codex Local, security owner sets agent permissions, analytics owner wires compliance APIs.
- **Maps to consolidated.md shape:** Across-the-board parallel — **Layered configuration (#1)**, **Hooks-based governance (#5)**, **Enterprise managed settings (#6)**, **Convention CLAUDE.md (#15)** (Codex calls it AGENTS.md). Direct shape-for-shape counterpart to Claude Code in the IDE-coding-agent niche.
- **Canonical URL:** [Codex docs](https://developers.openai.com/codex); [Hooks](https://developers.openai.com/codex/hooks); [AGENTS.md](https://developers.openai.com/codex/guides/agents-md); [Enterprise admin setup](https://developers.openai.com/codex/enterprise/admin-setup)
- **Recent (post-2026-01):** Hooks GA, Codex access tokens, Enterprise admin setup, managed-requirements.toml admin-locked floor — all 2026.

### Function calling / tool definitions
- **What:** Per-request JSON-schema tool definitions in Chat Completions / Responses API. No first-class "tool registry" on the API side — tools are app-defined and inline per call.
- **Alignment shape:** Tool sharing is whatever the calling code's package manager provides. No OpenAI-hosted tool catalog except via Prompts (which can pin tool sets) and the Agents SDK (which is just Python/TS).
- **Maps to consolidated.md shape:** No analog — Claude Code doesn't expose this primitive directly to users; both ecosystems leave tool-def sharing to the SDK layer.
- **Canonical URL:** [Function calling](https://developers.openai.com/api/docs/guides/function-calling); [Using tools](https://developers.openai.com/api/docs/guides/tools)

### Realtime API + voice agents
- **What:** Speech-to-speech API for voice agents. `gpt-realtime-2` (May 7, 2026) with GPT-5-class reasoning, parallel tool calls, MCP remote servers, image inputs, SIP phone calling. Agents SDK has Realtime Agent wrappers.
- **Alignment shape:** Same governance surface as the rest of the Responses API stack (project keys, prompts, MCP connectors). Voice adds nothing unique to the alignment story beyond tool-call reliability metrics.
- **Maps to consolidated.md shape:** No direct analog; Claude has voice modes but not a developer-facing equivalent in the shapes catalog.
- **Canonical URL:** [Realtime + audio guide](https://developers.openai.com/api/docs/guides/realtime); [gpt-realtime announcement](https://openai.com/index/introducing-gpt-realtime/)
- **Recent (post-2026-01):** `gpt-realtime-2`, `gpt-realtime-translate`, `gpt-realtime-whisper` — May 2026.

### Operator / Computer Use (folded into ChatGPT Agent)
- **What:** Browser+desktop control agent. Standalone Operator product (operator.chatgpt.com) absorbed into **ChatGPT Agent** by July 2025; site sunsetting. `computer_use` available as a built-in tool in the Responses API.
- **Alignment shape:** Per-user agent in ChatGPT; admin controls inherit from the workspace's ChatGPT Enterprise governance. API-side computer_use is per-call.
- **Maps to consolidated.md shape:** No exact analog in the catalog (Anthropic has Computer Use as an Agent SDK capability; the consolidated.md doesn't enumerate it as a shape).
- **Canonical URL:** [Introducing Operator](https://openai.com/index/introducing-operator/)
- **Recent (post-2026-01):** Operator site sunset; functionality lives in ChatGPT Agent + Responses API `computer_use` tool.

## Shapes OpenAI has that Anthropic does not

- **Server-hosted versioned Prompts** with diff/rollback/pin-by-version, referenced by `prompt_id`. Claude has no server-side prompt registry; prompt sharing is file-based in repos or via plugins.
- **Tenant-level control plane spanning multiple workspaces and API orgs** under one SSO (Global Admin Console). Anthropic's enterprise admin surface is per-org and less unified across the product line.
- **OpenAI-reviewed MCP connector tier** (curated partners) — a vetted middle ground between "open MCP" and "first-party tool." Anthropic publishes some MCPs but doesn't curate a third-party connector tier with a review program.
- **Workspace Agents as a turnkey shared-automation primitive** with built-in scheduling, credit-based billing, 60+ pre-integrated connectors. Anthropic has Managed Agents but the Workspace Agents framing — team-owned, always-on, scheduled — is more developed.
- **Codex `managed-requirements.toml`** — admin-locked configuration that users *cannot* override, alongside user config. Closer parallel to enterprise managed-settings but expressed at the IDE/CLI layer with explicit user-vs-admin-floor split.
- **Compliance Logs Platform with immutable JSONL exports** (Admin Audit, User Auth, Codex Usage). Anthropic has audit features but not a published unified observability/compliance log paradigm at this maturity.

## Shapes Anthropic has that OpenAI does not

- **Plugin marketplace (`marketplace.json` + git-hosted plugin bundles)** that compose skills, slash commands, subagents, hooks, MCPs into discoverable installable units. OpenAI's nearest analogs are split: Custom GPTs (per-user, no versioning), Workspace Agents (workspace-scoped, no third-party marketplace), reviewed MCP connectors (curated, not user-publishable).
- **Skills-as-units with description-driven trigger matching** in the agent runtime. No counterpart in OpenAI's stack — closest is "tool with description" but skills carry behavioral framing, not just tool schemas.
- **Subagent specialization with shipped specialist agents** (Explore, Plan, code-reviewer). OpenAI's Agents SDK has handoffs but no shipped specialist library; everything is hand-rolled per project.
- **Skill router / dynamic dispatch pattern** (UserPromptSubmit hook + embedding match). OpenAI's tool-selection is in-model; no public skill-router pattern.
- **npx-distributed skill packages targeting user-scope `~/.claude/`** — the lightweight publish-update path. OpenAI's distribution paths (PyPI for Agents SDK, ChatGPT GPT Store, MCP connector reviews) don't include a user-scope-injection equivalent.
- **Slash-command-as-workflow** in the IDE coding agent. Codex has hooks but not the named-multi-step-workflow surface; Claude's `/commit`, `/release`, `/checkpoint` shape isn't replicated.

## Summary

OpenAI's stack is **more centralized and product-unified** at the org control plane (Global Admin Console, Compliance Logs, reviewed-connector tier, Workspace Agents) while **less rich at the bundling/composability layer** Anthropic invests in (plugin marketplaces, skills-as-units, subagents, skill router). Codex is the direct shape-for-shape counterpart to Claude Code — hooks, AGENTS.md, managed-requirements, layered config — landed in 2026 GA. The Agents SDK mirrors Claude Agent SDK with stronger built-in MCP transport variety; both share the same alignment caveat that SDK-side governance doesn't share state with the IDE-side product. The biggest cross-vendor gap: Anthropic's plugin marketplace is a real third-party sharing primitive; OpenAI keeps the analogous role split between Workspace Agents (admin-curated) and MCP connectors (OpenAI-reviewed), with no open marketplace surface.
