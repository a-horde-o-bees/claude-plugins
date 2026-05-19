---
log-role: research-wave
status: draft v1 — sampled 2026-05-18 across the AGENTS.md adopter list
scope: multi-vendor AI coding tools that adopt the AGENTS.md substrate — survey against the 17 alignment shapes from consolidated.md
---

# Wave: Multi-vendor AGENTS.md adopter survey

Surveys 11 tools that adopt the [`AGENTS.md`](https://agents.md/) substrate (Cursor, GitHub Copilot Coding Agent, Gemini CLI, Aider, Continue.dev, Zed, goose, Devin, Windsurf, JetBrains Junie, opencode) against the 17 alignment shapes catalogued for Claude Code and Codex CLI in `consolidated.md`. The load-bearing finding is that the ecosystem is **much more converged than v1's framing implied**: Cursor, Gemini CLI, Copilot Coding Agent, opencode, and Junie all ship the full Claude/Codex-style plug-skill-hook-subagent-MCP-AGENTS.md stack, with the differences now in enterprise depth (Windsurf FedRAMP High, Cursor SOC 2, Junie JetBrains-corporate posture) and in agent format choice (markdown vs TOML). Aider and Zed are the conservative end (MCP + memory file but no skill/hook/plugin stack); Devin and Copilot Coding Agent are the hosted-only end (sandbox not user-facing, governance owned by GitHub/Cognition).

## Comparison matrix

Cell legend: y=yes, p=partial, n=no, n/a=not applicable, u=unverified.

Columns (1-17): 1 Layered config · 2 Plugin marketplace · 3 Hooks · 4 Subagents · 5 SKILL.md skills · 6 MCP · 7 AGENTS.md memory · 8 Managed floor · 9 Hosted variant · 10 User slash commands · 11 OS-enforced sandbox · 12 Tenant admin plane · 13 Compliance log export · 14 Vetted connector catalog · 15 Server-hosted versioned prompts · 16 OpenTelemetry · 17 Auto-memory

| Tool | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Claude Code** (ref) | y | y | y | y | y | y | p[CLAUDE.md] | y | y | y | y | y | y | y | n | y | y |
| **Codex CLI** (ref) | y | y | y | y | y | y | y | y | y | n | y | n | y | n | y | y | p |
| Cursor | y | y | y | y | y | y | y | y | n | n | n | y | p | y | u | p[3p] | n |
| Copilot Coding Agent | y | n | y | n | n | y | y | y | y | n/a | y[hosted] | y | y | u | u | u | n |
| Gemini CLI | y | y | y | y | y | y | y | y | y | y | u | y | p | y | n | u | u |
| Aider | y | n | n | n | n | p[3p] | p | n | n | y | n | n | n | n | n | n | n |
| Continue.dev | y | y | y | p | y | y | y | y | n | y | n | y | u | u | n | u | n |
| Zed | y | n | n | n | n | y | y | p | n | n | n | u | u | n | n | n | n |
| goose | y | y | p[recipes] | y | y | y | y | u | p | y | n | u | n | n | n | u | p[memory] |
| Devin | u | n | n | n | y | y | y | y | y | y | y[hosted] | y | u | u | n | u | y |
| Windsurf | y | n | y | p[Cascade] | n | y | y | y | n | y | n | y | y | u | n | u | y[memories] |
| JetBrains Junie | y | n | n | y | y | y | y | y | n | y | n | y | u | n | n | n | y |
| opencode | y | y | y | y | y | y | y | y | n | n | n | n | n | n | n | n | p |

## Per-tool inventory

### Cursor (Tier 1)

- **Confirmed shapes:**
  - Layered config — `.cursor/rules/` (project), team rules (org), user rules ([rules docs](https://cursor.com/docs/rules)).
  - Plugin marketplace — launched 2026-02-17 with Cursor 2.5; `.cursor-plugin/plugin.json` manifest, `.cursor-plugin/marketplace.json` for multi-plugin repos; install via `/add-plugin` or [cursor.com/marketplace](https://cursor.com/marketplace) ([plugin reference](https://cursor.com/docs/plugins/building)).
  - Hooks — `hooks/hooks.json` in plugins; pre/post tool, prompt, stop ([plugin reference](https://cursor.com/docs/plugins/building)).
  - Subagents — Cursor 2.4 (Jan 2026); independent agents with custom prompts/tools/models, run in parallel ([2.4 changelog](https://cursor.com/changelog/2-4)).
  - Skills — `SKILL.md` with name/description frontmatter; dynamic load ([rules + skills doc](https://cursor.com/docs)).
  - MCP — first-class, install via marketplace one-click, allowlists per team ([MCP docs](https://cursor.com/docs/mcp)).
  - AGENTS.md — supported directly in addition to `.cursor/rules/`; legacy `.cursorrules` also read ([rules docs](https://cursor.com/docs/rules)).
  - Managed floor — admin can blocklist/whitelist repos, models, MCP servers, agent run settings; MDM deployment documented ([enterprise](https://cursor.com/enterprise), [security](https://cursor.com/security)).
  - Tenant admin plane — dashboard at cursor.com/dashboard, SSO/SCIM, role permissions ([IAM docs](https://cursor.com/docs/enterprise/identity-and-access-management)).
  - Compliance export — admin audit log streams to Splunk/Sumo Logic/Datadog/webhook/S3 ([compliance-and-monitoring](https://cursor.com/docs/enterprise/compliance-and-monitoring)). Partial because **"We do not log agent responses or generated code content"** — governance events only.
  - Vetted connector catalog — Cursor Marketplace one-click verified plugins with security scores; launch partners Amplitude/AWS/Figma/Linear/Stripe/Cloudflare/Vercel/Databricks/Snowflake/Hex ([marketplace](https://cursor.com/marketplace)).
  - OpenTelemetry — third-party `cursor-otel-hook` integration ([pitchhut entry](https://www.pitchhut.com/project/cursor-otel-integration-2)); no first-party OTel emitter found.

- **Distinctive shapes:**
  - **Rule application modes** (Always / Intelligently / Globs / Manual) as explicit frontmatter dropdown — finer-grained than Claude Code's path-glob-only rule scoping.
  - **MCP install-links** ([install-links docs](https://cursor.com/docs/mcp/install-links)) — vendor-issued deep links that one-click-install an MCP server (Stripe, Linear, etc.) — closer to a "connector marketplace UX" than Anthropic's directory.

- **Enterprise posture:** SOC 2 Type II + GDPR + CCPA; SAML SSO (Okta/Entra ID/Google Workspace) + SCIM 2.0; CMEK for paying tiers; audit-log SIEM streaming. Trusted by 64% of Fortune 500 per Cursor's enterprise page. **Gap:** no HIPAA/FedRAMP posture surfaced; no agent-response/code logging by design.

- **Verification notes:** OpenTelemetry first-party emission — `unverified` first-party; third-party hook exists. Auto-memory — searched; nothing surfaced. Server-hosted prompts — `unverified`. OS-enforced sandbox — none documented at the Cursor IDE level (relies on macOS/Windows native + user permissions).

### GitHub Copilot Coding Agent (Tier 1)

- **Confirmed shapes:**
  - Layered config — `.github/copilot-instructions.md` + `AGENTS.md` + agent-specific instructions ([custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support)).
  - Hooks — 8 lifecycle events including `PreToolUse`, `PostToolUse`, `SessionStart`, `UserPromptSubmitted`, `AgentStop`, `SubagentStop`, `ErrorOccurred`, `SessionEnd`. Snake_case payload aligns with VS Code Copilot extension format ([hooks reference](https://docs.github.com/en/copilot/reference/hooks-configuration)).
  - MCP — `allow lists to prevent unauthorized access`; full MCP extension ([cloud-agent MCP](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp)).
  - AGENTS.md — added 2025-08-28; nested AGENTS.md supported per directory ([changelog](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/)).
  - Managed floor — enterprise policies gate cloud-agent enablement; repo-owner opt-out ([access management](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/access-management)).
  - Hosted variant — *is* the hosted variant; ephemeral GitHub Actions environment ([about-copilot-coding-agent](https://docs.github.com/en/copilot/concepts/about-copilot-coding-agent)).
  - OS-enforced sandbox — implicit via GitHub Actions ephemeral env.
  - Tenant admin plane — GitHub org/enterprise admin surface.
  - Compliance export — GitHub audit log streaming to SIEM (org-level GitHub Audit Log).
  - Copilot Spaces — knowledge bundles shared across an org ([github.com/features/copilot](https://github.com/features/copilot)).

- **Distinctive shapes:**
  - **`PreToolUse.hookSpecificOutput.permissionDecision`** with `allow|ask|deny` — a structured permission-decision protocol the hook reads on stdout; matches Claude Code's prompt/agent hook handler pattern but is HTTP/CLI agnostic ([hooks reference](https://docs.github.com/en/copilot/reference/hooks-configuration)).
  - **Custom agents in VS Code/Copilot** — repo-shipped custom agent personas separate from sub-agent concept ([create custom agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents)).
  - **Awesome-copilot meta-repo** ([github/awesome-copilot](https://github.com/github/awesome-copilot)) — community pattern catalog (instructions, agents, skills) blessed by GitHub but not a plugin marketplace.

- **Enterprise posture:** GitHub enterprise tenant inherits SOC 2, ISO 27001, FedRAMP Moderate (via GitHub Enterprise Cloud); SSO/SCIM via parent GitHub org. Admin audit log is the canonical governance log surface; cloud-agent activity surfaces there. **Gap:** no skill or plugin marketplace as a first-class shape; subagents not documented as a coding-agent feature.

- **Verification notes:** Subagents — not surfaced for the cloud agent; `n`. SKILL.md — Copilot does support agent skills in VS Code per [agent-skills doc](https://code.visualstudio.com/docs/copilot/customization/agent-skills), but the coding agent path isn't where the skills format lives; recorded `n` for the coding-agent-specific row to stay faithful to scope. Server-hosted prompts and OpenTelemetry — `unverified`.

### Gemini CLI (Tier 1)

- **Confirmed shapes:**
  - Layered config — `~/.gemini/settings.json` (user), workspace, system; **system has highest precedence and overrides** ([reference/configuration](https://geminicli.com/docs/reference/configuration/)).
  - Plugin marketplace — Extensions are the plugin shape; bundle prompts, MCP, custom commands, themes, hooks, subagents, skills ([extensions](https://geminicli.com/docs/extensions/), [browse extensions](https://geminicli.com/extensions/)).
  - Hooks — `hooks/hooks.json` in extension; "fully control and customize the agentic loop" per v0.26.0 release ([discussion #17812](https://github.com/google-gemini/gemini-cli/discussions/17812)).
  - Subagents — markdown definitions in extension `agents/` directory ([developers.googleblog.com](https://developers.googleblog.com/subagents-have-arrived-in-gemini-cli/)).
  - Skills — `skills/<name>/SKILL.md` in extensions; loaded conditionally ([medium write-up](https://medium.com/google-cloud/your-gemini-cli-extensions-just-got-smarter-introducing-agent-skills-a8fbfa077e7f)).
  - MCP — native via settings.json + extensions ([MCP server doc](https://www.geminicli.com/docs/tools/mcp-server)).
  - AGENTS.md / GEMINI.md — supports both; converging on AGENTS.md per AGENTS.md spec.
  - Managed floor — system-tier settings.json + Policy Engine ([policy-engine](https://geminicli.com/docs/reference/policy-engine/)); enterprise.md in the repo documents allowlists ([enterprise.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md)).
  - Hosted variant — Jules / Gemini Enterprise Agent Platform on Google Cloud.
  - Slash commands — user-authored TOML files in `~/.gemini/commands/` or `.gemini/commands/` ([custom commands](https://geminicli.com/docs/cli/custom-commands)).
  - Tenant admin plane — Google Cloud Gemini Enterprise (IAM roles, governance dashboard) ([govern docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern)).
  - Vetted connector catalog — Browse Extensions catalog ([geminicli.com/extensions](https://geminicli.com/extensions/)).
  - Compliance — Gemini Enterprise governance pillars include "Operational Oversight" / audit; partial because details vary by Google Cloud tier.

- **Distinctive shapes:**
  - **Extensions as the unit of distribution** — bundles MCP + skills + subagents + hooks + commands + themes in one package format, more uniform than separate "plugin" vs "extension" surfaces elsewhere.
  - **`/rewind`** ([discussion #17812](https://github.com/google-gemini/gemini-cli/discussions/17812)) — step-back primitive; novel agentic-loop control surface.
  - **Policy Engine** as a dedicated subsystem — exposes a policy evaluation layer distinct from hooks ([policy-engine](https://geminicli.com/docs/reference/policy-engine/)).

- **Enterprise posture:** Inherits Google Cloud's compliance stack (SOC 2, ISO 27001/17/18, FedRAMP, HIPAA BAA via GCP Enterprise) — strong but tied to Gemini Enterprise Agent Platform pathway. IAM via Google Workspace / Cloud IAM. **Strength:** Google's enterprise-control depth via GCP makes this the most enterprise-flexible of the open-source CLIs.

- **Verification notes:** OS-enforced sandbox — `unverified`; CLI does not surface a `/sandbox` equivalent in docs sampled. OpenTelemetry — `unverified`. Server-hosted prompts — `n` (extensions package prompts; not a versioned-hosted-prompt service).

### Aider (Tier 2)

- **Confirmed shapes:**
  - Layered config — `.aider.conf.yml` walks home → repo root → cwd ([yaml config](https://aider.chat/docs/config/aider_conf.html)).
  - MCP — partial; community shims (`mcpm-aider`, `MCP-Bridge`) but not first-party ([mcpm-aider](https://github.com/lutzleonhardt/mcpm-aider)).
  - AGENTS.md — partial: docs reference checking AGENTS.md first, but `CONVENTIONS.md` declared via `read:` array is the canonical Aider mechanism ([conventions](https://aider.chat/docs/usage/conventions.html), [issue #4395](https://github.com/Aider-AI/aider/issues/4395)).
  - Slash commands — `/code`, `/ask`, `/architect`, `/help`, `/chat-mode`, plus per-session command line ([modes](https://aider.chat/docs/usage/modes.html)).

- **Distinctive shapes:**
  - **Chat-mode switching as first-class** (`code` / `ask` / `architect` / `help`) — the ask→code workflow encoded in the tool itself, distinct from sub-agents because it's modal not delegated. Architect mode is a 2-model split (architect proposes, editor applies).
  - **CONVENTIONS.md via explicit `read:` declaration** — Aider's approach predates AGENTS.md and remains its primary convention surface; AGENTS.md interop is layered on top.

- **Enterprise posture:** No managed-floor / SSO / audit story documented. Aider is a developer-tool CLI with no commercial enterprise tier; alignment governance happens entirely at the user/repo level. Not a fit for centrally-governed deployments without significant scaffolding.

- **Verification notes:** Plugins / hooks / subagents / skills / OTel / auto-memory / connector catalog — all `n` after multiple targeted searches; Aider has not adopted the broader Claude/Codex shape catalogue. MCP native support is on the roadmap but not landed at sampling time.

### Continue.dev (Tier 2)

- **Confirmed shapes:**
  - Layered config — `config.yaml` per-project + hub config; clear hub-vs-local model ([understanding-configs](https://docs.continue.dev/guides/understanding-configs)).
  - Plugin marketplace — Continue Hub for assistants, models, rules, prompts, tools (MCP) — block-based composition ([hub.continue.dev](https://hub.continue.dev/)).
  - Hooks — Plugins can include hooks; quality-gate pattern documented.
  - Subagents — partial; agents as composed bundles of models + rules + tools, but no dedicated subagent-delegation primitive surfaced.
  - Skills — `continuedev/skills` reusable skill library ([github.com/continuedev/skills](https://github.com/continuedev/skills)).
  - MCP — first-class; only usable in agent mode; `mcpServers` in hub configs ([MCP deep-dive](https://docs.continue.dev/customize/deep-dives/mcp)).
  - AGENTS.md — supported; agents update AGENTS.md on PR open per Continue's Check system.
  - Managed floor — Team/Company plans include SSO + access controls + BYOK ([continue.dev pricing/teams]).
  - Slash commands — prompt files in `.continue/prompts/` are the slash-command shape (`slashCommands` array deprecated).
  - Tenant admin plane — Continue for Teams admin surface.

- **Distinctive shapes:**
  - **Checks** — markdown-defined AI checks fire as GitHub status checks on PRs; an agentic PR-review surface as a primary product feature ([continue.dev landing](https://www.continue.dev/)).
  - **Hub-vs-local explicit duality** — every config can be hub-published, version-pinned, and pulled by reference; cleaner than the per-project file model elsewhere.

- **Enterprise posture:** SSO + access controls + BYOK on the paid tiers; admin console surface less documented than Cursor/Windsurf. Open-source core gives self-host option. **Gap:** compliance certification posture not prominently surfaced in May-2026 sampling — `unverified` for SOC2/ISO/HIPAA.

- **Verification notes:** OTel — `unverified`. OS sandbox — `n` documented. Compliance log export — `unverified`. Auto-memory — `n`. Server-hosted prompts — `n` (prompts are hub-distributed files, not a server-hosted versioned API).

### Zed (Tier 2)

- **Confirmed shapes:**
  - Layered config — Zed settings JSON; project-level + user-level.
  - MCP — first-class via `context_servers` in settings; forwarded to Claude Agent / Codex via ACP ([MCP docs](https://zed.dev/docs/ai/mcp)).
  - AGENTS.md — supported via `.rules` files + CLAUDE.md compatibility ([rules](https://zed.dev/docs/ai/rules)).
  - Managed floor — partial; Zed for Business plan announced ($30/seat/mo) with admin controls roadmap (SAML / OIDC / SCIM / SOC 2 in progress) ([alternativeto write-up](https://alternativeto.net/news/2026/5/zed-for-business-launches-with-advanced-admin-controls-and-flexible-ai-billing/)).

- **Distinctive shapes:**
  - **Agent Client Protocol (ACP)** ([zed.dev/acp](https://zed.dev/acp)) — Zed's open protocol for embedding *external* agents (Claude Agent, Gemini CLI, Codex) directly in the editor's agent panel. Cross-vendor agent embedding is unique to Zed's posture.
  - **Per-tool-call explicit permission prompt by default** — "Zed's philosophy is explicit over automatic" — counter to the trend of fewer prompts.

- **Enterprise posture:** Just-launched (May 2026) Zed for Business; SAML/OIDC/SCIM/SOC 2 are roadmap items, not yet shipped. Currently the least enterprise-mature of the major editor tools.

- **Verification notes:** Plugins/hooks/subagents/skills/SKILL.md — all `n`; Zed's posture is to host other vendors' agents rather than build its own skill/plugin stack. Compliance/OTel — `unverified`.

### goose (Tier 3)

- **Confirmed shapes:**
  - Layered config — config.yaml-based.
  - Plugin marketplace — Extensions are the plugin shape; 70+ documented, 3000+ MCP servers in the registry ([goose docs](https://block.github.io/goose/docs/guides/recipes/)).
  - Hooks — partial; lifecycle events surface for "unified agent execution" per [discussion #4389](https://github.com/block/goose/discussions/4389) but not a first-class taxonomy comparable to Claude Code/Codex.
  - Subagents — yes via recipes invoking subrecipes concurrently ([recipes docs](https://block.github.io/goose/docs/guides/recipes/)).
  - Skills — supported; unification with subagents + recipes proposed in [discussion #6202](https://github.com/block/goose/discussions/6202).
  - MCP — one of the earliest and deepest adopters ([Linux Foundation AAIF announcement](https://block.github.io/goose/)).
  - AGENTS.md — supported.
  - Slash commands / recipes — Recipes are YAML workflow bundles; invoked as commands.

- **Distinctive shapes:**
  - **Recipes + Subrecipes** — YAML workflows with structured inputs and sub-recipe composition. The unit of automation is the recipe, not the skill. Unique vocabulary; closer to GitHub Actions composability than to Claude Code skills.
  - **Linux Foundation AAIF inaugural project** (alongside MCP and AGENTS.md per December 2025 announcement) — governance signal that goose is positioned as a community-stewarded substrate, not a vendor product.

- **Enterprise posture:** Block runs 12k internal users on goose; the public OSS product does not surface managed-settings/MDM/SSO documentation. Block's CISO did publicly red-team goose ("Operation Pale Fire", Jan 2026) and shipped Unicode-attack mitigations — security-conscious posture without an enterprise admin plane.

- **Verification notes:** Auto-memory — partial; opencode-style memory blocks exist in adjacent extensions but not first-party goose. OTel / sandbox / tenant admin — `unverified` to `n`.

### Devin (Tier 3)

- **Confirmed shapes:**
  - SKILL.md skills — `.agents/skills/<name>/SKILL.md` open Agent Skills format; cross-tool portable ([skills](https://docs.devin.ai/product-guides/skills)).
  - MCP — supported.
  - AGENTS.md — supported as primary onboarding mechanism; auto-pulls from `.rules`/`.mdc`/`.cursorrules`/`.windsurf`/`CLAUDE.md`/`AGENTS.md` ([AGENTS.md doc](https://docs.devin.ai/onboard-devin/agents-md), [knowledge onboarding](https://docs.devin.ai/onboard-devin/knowledge-onboarding)).
  - Managed floor — VPC deployment + SSO; enterprise-only.
  - Hosted variant — *is* the hosted variant by design.
  - Slash commands — `/handoff` and related; not user-authored first-class.
  - OS-enforced sandbox — implicit via hosted container per session.
  - Tenant admin plane — Cognition's admin surface for VPC enterprises (NDA-gated trust center at trust.cognition.ai).
  - Auto-memory — Knowledge graph; Devin auto-pulls knowledge per session ([knowledge](https://docs.devin.ai/product-guides/knowledge)).

- **Distinctive shapes:**
  - **Knowledge Graph** — Cognition surfaces an explicit "knowledge" abstraction that pins notes per-repo or globally and auto-includes them in sessions. Closer to a vendor-hosted memory layer than Claude Code's auto-memory.
  - **VPC deployment as a first-class tier** — single-tenant hosted deployment is the headline enterprise option.

- **Enterprise posture:** Trust center is NDA-gated; SSO + VPC documented; specific compliance certs (SOC 2 / HIPAA / FedRAMP) not publicly listed. Enterprise admin features described as "happy to provide more details upon request" — opaque public posture. **Caveat:** absent NDA access, public verification is limited.

- **Verification notes:** Layered config (CLI-side vs hosted) — `unverified` for the user-config side; the hosted product centralizes most config. Plugins/hooks/subagents/slash-as-author — `n`. Compliance export / OTel — `unverified` (likely behind NDA trust center).

### Windsurf / Codeium (Tier 3)

- **Confirmed shapes:**
  - Layered config — system / user / workspace hooks.json + `.windsurfrules` ([hooks](https://docs.windsurf.com/windsurf/cascade/hooks)).
  - Hooks — Cascade Hooks: 12 events (pre/post for read_code, write_code, run_command, mcp_tool_use, plus pre_user_prompt, post_cascade_response, post_cascade_response_with_transcript, post_setup_worktree). Only pre-hooks can block (exit code 2). System-level config under `/etc/windsurf/hooks.json`.
  - Subagents — Cascade is the agent abstraction; not a multi-agent subagent system per se.
  - MCP — supported with admin allow-lists.
  - AGENTS.md — supported (per adopters list).
  - Managed floor — Cloud dashboard hook enforcement + MDM (Jamf/Intune) deployment of system-level hooks.json.
  - Slash commands — Workflows in `.windsurf/workflows/*.md` invokable via `/plan-story`, `/develop-story`, etc.
  - Tenant admin plane — Cloud dashboard team settings.
  - Compliance — SOC 2 Type II, **FedRAMP High** ([LinkedIn announcement](https://www.linkedin.com/posts/windsurf_codeium-has-achieved-fedramp-high-certification-activity-7307430545389428736-eIUh)), HIPAA BAA, ITAR, IL4/IL5 via Palantir FedStart partnership ([AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-x4iqsqorbfaj4)).
  - Auto-memory — Memories feature (referenced in `.windsurfrules` discussions).

- **Distinctive shapes:**
  - **3-mode deployment** — Cloud / Hybrid / Self-Hosted, with self-hosted operable without outbound traffic except to trusted LLM endpoint. Strongest air-gap story in this survey.
  - **Workflows as user-authored slash commands** — markdown files in `.windsurf/workflows/` that define multi-step Cascade procedures with explicit step invocation. Closer to "scripted procedures" than the freer skill format.

- **Enterprise posture:** Strongest compliance posture in the survey — SOC 2 Type II + FedRAMP High + HIPAA BAA + ITAR via Palantir FedStart. Self-hosted deployment with offline updates available. SAML SSO + RBAC + audit logs default-on. Codeium has built enterprise-first for regulated industries (defense, healthcare, financial). **Strength:** if FedRAMP High is the bar, Windsurf is the only adopter here with full coverage.

- **Verification notes:** Plugin marketplace — `n` (workflows + hooks are the extension surfaces). SKILL.md — `n`; not adopted. Server-hosted prompts — `n`. OTel emission — `unverified`.

### JetBrains Junie (Tier 3)

- **Confirmed shapes:**
  - Layered config — `.junie/` directory with guidelines, AGENTS.md, commands, agents, skills ([CLI config](https://junie.jetbrains.com/docs/junie-cli-configuration.html)).
  - Subagents — `.junie/agents/` or `.agents/` markdown with YAML; auto-delegation only (no manual slash-invocation) ([subagents](https://junie.jetbrains.com/docs/junie-cli-subagents.html)).
  - Skills — `.junie/skills/SKILL.md` Agent Skills standard ([agent skills](https://junie.jetbrains.com/docs/agent-skills.html)).
  - MCP — supported via `.junie/mcp.json` ([MCP config](https://junie.jetbrains.com/docs/junie-cli-mcp-configuration.html)).
  - AGENTS.md — `.junie/AGENTS.md` plus `.junie/guidelines.md` ([guidelines and memory](https://junie.jetbrains.com/docs/guidelines-and-memory.html)).
  - Managed floor — IDE-policy-based; JetBrains corporate channels.
  - Slash commands — `.junie/commands/` markdown with YAML; argument substitution via `$argumentName` ([custom slash commands](https://junie.jetbrains.com/docs/custom-slash-commands.html)).
  - Tenant admin plane — JetBrains Account admin surface (Enterprise tier).
  - Auto-memory — `.junie/guidelines.md` + memory tooling.

- **Distinctive shapes:**
  - **Brave Mode** (deprecated by guidance) + **Action Allowlist** — explicit permission model with a documented "do not use brave mode" advisory in the docs ([user approval](https://www.jetbrains.com/help/junie/user-approval.html)). Allowlist-first culture.
  - **IDE-native agent embedding** — Junie ships as a JetBrains IDE plugin in addition to the CLI; the same agent runs in both surfaces with shared config ([junie-ide-plugin](https://junie.jetbrains.com/docs/junie-ide-plugin.html)).

- **Enterprise posture:** Inherits JetBrains' SOC 2 Type II + GDPR posture; Enterprise tier includes SSO + enhanced controls per JetBrains Account. Specific HIPAA/FedRAMP/ISO surface not prominently documented for Junie specifically — JetBrains Trust Center provides parent-org coverage. Strong IDE-administrator surface via JetBrains Toolbox enterprise tooling.

- **Verification notes:** Plugin marketplace — `n` (skills + commands + agents are the extension surfaces; no plugin marketplace shape). Hooks — `n` documented at sampling time; could be added in CLI evolution. Compliance log export — `unverified` (parent JetBrains audit posture exists). OTel — `n`.

### opencode (Tier 3)

- **Confirmed shapes:**
  - Layered config — `opencode.json` with managed config tier at `/etc/opencode` (highest precedence); macOS Managed Preferences via MDM `.mobileconfig` ([config](https://opencode.ai/docs/config/), [issue #19158](https://github.com/anomalyco/opencode/issues/19158)).
  - Plugin marketplace — JavaScript/TypeScript plugins; project `.opencode/plugins/`, global `~/.config/opencode/plugins/`, npm packages auto-installed via Bun ([plugins](https://opencode.ai/docs/plugins/)).
  - Hooks — extensive lifecycle event surface: `session.created`, `tool.execute.before`, `file.edited`, `message.updated`, plus Command/File/Installation/LSP/Message/Permission/Server/Session/Todo/Shell/Tool/TUI event families.
  - Subagents — primary + subagent split; `@`-mention manual invocation or auto-delegation ([agents](https://opencode.ai/docs/agents/)).
  - Skills — `SKILL.md` discovered from `.opencode/skills/`, `~/.config/opencode/skills/`, *and* `.claude/skills/` *and* `.agents/skills/` — explicit cross-tool path compat ([skills](https://opencode.ai/docs/skills/)).
  - MCP — first-class.
  - AGENTS.md — primary memory file.
  - Managed floor — `/etc/opencode` admin config tier; macOS MDM `.mobileconfig` ([enterprise](https://opencode.ai/docs/enterprise/)).
  - Tenant admin plane — opencode Enterprise advertises centralized config + SSO + internal AI gateway.

- **Distinctive shapes:**
  - **Cross-tool skill path compatibility built-in** — opencode reads `.claude/skills/`, `.agents/skills/`, `.opencode/skills/` simultaneously. Most aggressive interop posture in the survey.
  - **JavaScript-native plugin model** — plugins are JS/TS modules with strongly-typed hooks objects, run under Bun. Architecturally distinct from the markdown+frontmatter or TOML formats used elsewhere; closer to a "VSCode-extension-style" agent customization model.
  - **`.mobileconfig` MDM support** — Jamf/Kandji/FleetDM deployable settings as a first-class enterprise pattern (matches Anthropic's Jamf/Kandji posture).

- **Enterprise posture:** Enterprise tier emphasizes "code and data never leaves your infrastructure" + centralized config + SSO + internal AI gateway routing. MDM-managed-config surface is the floor. **Gap:** SOC 2 / compliance certs not surfaced in May-2026 sampling; rapid open-source iteration model. Auto-memory exists in 3p extensions ([opencode-agent-memory](https://github.com/joshuadavidthomas/opencode-agent-memory)) but not first-party.

- **Verification notes:** OS-enforced sandbox — `n`; relies on external tools like rivet-dev/sandbox-agent. Compliance log export / OTel / vetted connector catalog / server-hosted prompts — `n` documented. Auto-memory marked partial because of the credible third-party extension presence.

## Distinctive shapes worth catalog-promoting

Five shapes surfaced in this wave that should be considered for promotion to `consolidated.md`'s common-shapes catalog:

1. **Tiered permission decision in hook responses** (Copilot Coding Agent's `hookSpecificOutput.permissionDecision: allow|ask|deny`, mirrored by Windsurf's exit-code-2 pre-hook blocking, Claude Code's `agent` hook handler) — a cross-vendor pattern for "hook returns a policy verdict, not just a side effect". Worth a sub-shape under #4 Hooks-based governance.

2. **Cross-tool skill-path compatibility as a feature** (opencode reads `.claude/skills/`, `.agents/skills/`, *and* its own `.opencode/skills/` simultaneously). When portability is real, the tool that reads *all* the path conventions wins. Counterpart at the AGENTS.md substrate level deserves promotion as "polyglot skill discovery" — a sub-shape under #10 Skills as units.

3. **Chat-mode switching as a first-class primitive** (Aider's `/ask` / `/code` / `/architect` / `/help` with persistent vs per-message scope) — distinct from subagents because it's modal rather than delegated. Closer to "modal cognitive frame" than "specialist sub-agent". Worth a new sub-shape if more tools adopt it (Aider is currently the cleanest example).

4. **Agent Client Protocol (ACP) for cross-vendor agent embedding** (Zed's protocol that hosts Claude Agent, Gemini CLI, Codex inside Zed's agent panel via a single shared interface) — a portability shape orthogonal to AGENTS.md. AGENTS.md ports *context*; ACP ports *the agent runtime*. Promote to "cross-tool runtime substrate" alongside `AGENTS.md` substrate.

5. **MDM `.mobileconfig` / Managed Preferences as a managed-floor mechanism** (opencode, Claude Code's `com.anthropic.claudecode` Jamf/Kandji domain). Promote as a sub-shape under #5 Enterprise managed floor — the OS-managed-preferences path is the credible alternative to `requirements.toml` / `managed-settings.json` and is increasingly standardized for enterprise IT.

## Verification of consolidated.md claims about the AGENTS.md substrate

**Does the substrate hold as a portability layer?** Yes, but with caveats:

- **AGENTS.md memory file** — broadly adopted as claimed. All 11 surveyed tools support some form of AGENTS.md ingestion. Devin auto-pulls from a half-dozen tool-specific files including AGENTS.md; Aider includes it but defaults to its native CONVENTIONS.md; Zed supports it via `.rules` + CLAUDE.md interop.

- **`.agents/skills/` path** — adopted by Devin, opencode, Junie (which reads both `.junie/agents/` and `.agents/`), Gemini CLI (via extension `skills/`), and Codex. Cursor uses its own `.cursor/` paths; Continue uses `.continue/`. The cross-tool path convention is real but *not universal* — about 6/11 tools.

- **`.agents/plugins/marketplace.json`** — adoption is thinner. Cursor uses `.cursor-plugin/marketplace.json`, Gemini CLI uses Extensions, opencode uses npm + local-config plugins. Only Codex hews tightly to `.agents/plugins/marketplace.json`. The plugin-marketplace path is the weakest of the substrate's three load-bearing conventions.

- **Apparent adopters with divergent behavior worth flagging:**
  - **Aider** — listed as an AGENTS.md adopter but *defaults to CONVENTIONS.md*; AGENTS.md is read only when explicitly declared in `read:`. Treat Aider's adoption as "soft adoption / opt-in" not "default".
  - **Zed** — surfaces AGENTS.md via `.rules` and CLAUDE.md interop docs; not a primary first-class path. Closer to "AGENTS.md-aware" than "AGENTS.md-native".
  - **Devin** — does read AGENTS.md but also auto-pulls from `.cursorrules`, `.windsurf`, `CLAUDE.md`, `.mdc`, `.rules` — promiscuous reader. AGENTS.md is one of many sources, not the canonical one.

- **One tool absent from the adopter list but functioning as a node anyway:** Claude Code's `/init` reads AGENTS.md, `.cursorrules`, `.windsurfrules` and pulls relevant parts into CLAUDE.md — partial bridge, no live sync.

**Net:** the AGENTS.md substrate is real and is the most portable shape on offer, but treating "adopter list membership" as binary obscures real behavioral variance. Adopt with eyes open: the same `AGENTS.md` will *load* across tools, but *priority*, *layering*, *override semantics*, and *nested-file handling* vary materially. The spec's [v1.1 proposal](https://github.com/agentsmd/agents.md/issues/135) to make these semantics explicit is the right next move.

## Summary

The multi-vendor reality is **stronger and more converged than v1's "Claude Code conspicuously absent" framing implied** — Cursor, Gemini CLI, Junie, opencode, and Copilot Coding Agent ship the full Claude/Codex-style plug-skill-hook-subagent-MCP stack on top of AGENTS.md, leaving Aider and Zed as the conservative end (memory file + MCP, no full extensibility stack) and Devin/Windsurf/Copilot Coding Agent as the hosted-managed end (sandbox + governance owned by the vendor). The differentiation that matters for company-scale advisory has moved from "does the tool have shape X" to (a) **enterprise compliance depth** — Windsurf's FedRAMP High + ITAR is unmatched in this survey, Cursor's SOC 2 + SIEM streaming is the second floor, JetBrains/Google inherit parent-corp posture — and (b) **plugin model architecture** — markdown+frontmatter (Cursor, Junie, Gemini), JavaScript modules (opencode), YAML recipes (goose), TOML configs (Codex) each have different ergonomics for who can author and at what tier. For a developer advising at company scale, the AGENTS.md substrate is a credible portability bet but should be paired with awareness that priority/override semantics vary, and that compliance + IT-managed-config posture (FedRAMP, MDM, SIEM) is the dimension most likely to decide vendor selection in regulated industries.
