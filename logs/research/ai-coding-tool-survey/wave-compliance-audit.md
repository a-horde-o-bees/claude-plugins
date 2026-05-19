---
log-role: research-wave
status: v1 — 2026-05-18 cross-vendor compliance/audit verification
scope: verify or refute consolidated.md gap claims around audit logs, admin plane, sandboxing, compliance certs
---

# Wave: Compliance and audit surfaces (cross-platform verification)

The consolidated doc's gap claims against Anthropic on audit/admin/sandbox are largely out of date or wrong. Anthropic launched a Compliance API in March 2026 with ~30 typed events, has a published 25-endpoint Admin API, supports a parent organization tenant hierarchy with SCIM/SSO across child orgs, ships OS-enforced sandboxing (Seatbelt / bubblewrap+seccomp / WSL2) with an open-source runtime, and runs a reviewed MCP connector directory (398 connectors). The remaining honest gaps are in discoverability and marketing (no `admin.openai.com`-style portal page; Compliance API is enterprise-gated and PDF-documented), log retention defaults (Anthropic 180d vs OpenAI 30d on Compliance Logs Platform), unified ChatGPT-Enterprise-style web console UX, and FedRAMP coverage of Claude Code/Cowork (not yet under Claude-for-Government's FedRAMP-High envelope, roadmapped for 2026). Net: Anthropic actually leads on FedRAMP-High (OpenAI is FedRAMP-Moderate as of April 2026); OpenAI leads on single-tenant-portal UX and marketing density. Decision-blocking for regulated industries today: capability parity exists, but Anthropic's enterprise governance is harder to discover and the Claude Code product specifically still has gaps inside the FedRAMP-High envelope.

## Per-platform compliance/audit surface inventory

### Anthropic (Claude Code + Agent SDK + Managed Agents + API)

**Audit log surface:**
- [Compliance API](https://support.claude.com/en/articles/13015708-access-the-compliance-api) GA'd 2026-03-30. ~30 typed events across auth (SSO/Google/Apple, magic-link, sign-out), account mgmt, projects, invitations, SSO/security toggles, conversation lifecycle, file uploads. Nine-field schema (`created_at`, `actor_info`, `event`, `event_info`, `entity_info`, `ip_address`, `device_id`, `user_agent`, `client_platform`). 180-day retention. Append-only, accessed via compliance access keys.
- Critical limitation: does not capture prompts, completions, model invocations, or tool calls. Real gap vs. the marketing positioning — answers "who configured what" not "what did they ask."
- Claude Code emits structured signals via [OpenTelemetry](https://code.claude.com/docs/en/monitoring-usage) (`CLAUDE_CODE_ENABLE_TELEMETRY=1`, OTLP/Prometheus/console exporters, metrics+logs+optional traces). User can sink to any OTel collector.
- [`ConfigChange` hook](https://code.claude.com/docs/en/hooks#configchange) lets organizations block or log settings drift during sessions — audit-grade hook event.
- Claude Code on the web logs all cloud-execution operations in Anthropic-managed VMs ([source](https://code.claude.com/docs/en/security#cloud-execution-security)).
- Cowork explicitly excluded from Compliance API, audit logs, and data exports as of this writing.

**Admin / governance API:** [25-endpoint Admin API](https://platform.claude.com/docs/en/api/admin-api) for programmatic org mgmt — workspaces, members, roles, API keys, rate limits, spend limits, data residency settings. Up to 100 workspaces per org. SCIM directory sync for auto-provisioning.

**Compliance posture:**
- SOC 2 Type I and Type II ([Trust Center](https://trust.anthropic.com/resources))
- HIPAA: BAA available on Claude API, Claude Enterprise, Claude Code CLI (ZDR only). Admin must activate ([BAA article](https://privacy.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers))
- FedRAMP High on [Claude for Government](https://support.claude.com/en/articles/13756069-public-sector-faqs) (standalone product). Supports CUI / FIPS 199 High; IL4/IL5 via Bedrock GovCloud; IL6 via AWS Secret region. Claude Code and Cowork are not yet in the C4G envelope (roadmapped 2026).
- ISO 27001:2022, ISO/IEC 42001:2023 ([cert article](https://privacy.claude.com/en/articles/10015870-what-certifications-has-anthropic-obtained)). ISO 27017/27018/27701 not surfaced on the Trust Center cert list.
- BYOK: announced for H1 2026, not yet GA in May 2026.
- ZDR: available as Enterprise addendum.
- Data residency: direct API is US/global only; EU via Bedrock EU profiles or Vertex AI EU regional endpoints.

**Tenant plane:** [Parent organization to child organizations to workspaces](https://support.claude.com/en/articles/13132885-set-up-single-sign-on-sso) hierarchy with parent-org-level identity (SSO, SCIM, domain verification) and per-child-org role mapping. An Anthropic equivalent to `admin.openai.com` exists in capability; it is not branded or marketed as a single named console.

**Regulated adoption:** [Claude for Healthcare](https://www.anthropic.com/news/healthcare-life-sciences) (JPM26 launch, includes BAA, HIPAA-ready, ICD-10/PubMed integrations); Advocate Health 167k-person rollout; [PwC partnership](https://www.anthropic.com/news/pwc-expanded-partnership) (insurance underwriting, pharma, financial services); [Salesforce Agentforce](https://www.anthropic.com/news/salesforce-anthropic-expanded-partnership) for regulated industries; Accenture multi-year partnership.

### OpenAI (Codex + Agents SDK + Responses API + ChatGPT Enterprise + Workspace Agents)

**Audit log surface:**
- [Compliance Logs Platform](https://developers.openai.com/cookbook/examples/chatgpt/compliance_api/logs_platform) — immutable append-only JSONL exports, time-windowed. Endpoints: `GET /v1/compliance/{workspaces|organizations}/{id}/logs[/{log_id}]`. 30-day platform retention (consumers must download for longer).
- Log types: Admin Audit, User Authentication, Codex Usage, ChatGPT Audit and Authentication ([release notes](https://help.openai.com/en/articles/10128477-chatgpt-enterprise-edu-release-notes)).
- Stateful Compliance API alongside Logs Platform for point-in-time state queries.
- [API Platform Admin/Audit Logs API](https://help.openai.com/en/articles/9687866-admin-and-audit-logs-api-for-the-api-platform) separately covers API-org events.

**Admin / governance API:** [Global Admin Console](https://help.openai.com/en/articles/12289294-global-admin-console) tenant hierarchy: Tenant to Workspaces + API orgs to Groups/Roles to Users. SCIM, IP allowlists, custom RBAC, verified domains. Marketed as a single named portal (`admin.openai.com`). Spans ChatGPT, API, Codex, Workspace Agents under one SSO.

**Compliance posture (from [trust.openai.com](https://trust.openai.com/)):**
- SOC 2 Type II, SOC 3
- ISO 27001:2022, 27017:2015, 27018:2019, 27701:2019, 42001:2023
- FedRAMP 20x Moderate (ChatGPT Enterprise + API Platform, [April 27 2026](https://openai.com/index/openai-available-at-fedramp-moderate/)). Not FedRAMP High. Azure OpenAI Service via Microsoft is High-authorized — separate product.
- HIPAA/BAA: not listed on Trust Portal as a published cert (gap or undisclosed).
- PCI DSS v4.0.1, CSA STAR, GDPR, CCPA.
- Customer-managed keys: not published on Trust Portal.
- ZDR: available via API.

**Regulated adoption:** Workspace Agents launched 2026-04-22 on Business/Enterprise/Edu. Notion/Asana/Sentry (cited in consolidated doc) are Managed Agents (Anthropic) adopters, not OpenAI — the consolidated doc framed this correctly but the mapping is worth restating.

## Verification of consolidated.md gap claims

| Claim | Status | Evidence |
|---|---|---|
| Anthropic has no analog to Compliance Logs Platform | REFUTED | [Compliance API GA 2026-03-30](https://support.claude.com/en/articles/13015708-access-the-compliance-api), ~30 events, 180d retention. Anthropic gap: no prompts/completions/tool-call capture. OpenAI gap: 30-day vs 180-day retention default favors Anthropic |
| Anthropic enterprise admin surface is less vertically unified | PARTIAL | Capability exists — [parent-org hierarchy with cross-org SSO/SCIM](https://support.claude.com/en/articles/13132885-set-up-single-sign-on-sso), [25-endpoint Admin API](https://platform.claude.com/docs/en/api/admin-api). Real gap is UX/branding: no named portal equivalent to `admin.openai.com`; admin work spans Console + Claude.ai admin panel + managed-settings files |
| Codex `requirements.toml` is cleaner than `managed-settings.json` overloading | REFUTED | Claude Code [uses separate files](https://code.claude.com/docs/en/settings): `managed-settings.json` (admin floor), `managed-mcp.json` (admin MCP), distinct from project/user `settings.json` and `.mcp.json`. Admin-only fields are explicitly marked. Naming is less semantically sharp than `requirements.toml` but separation of concerns is real |
| Claude Code is policy-only on sandbox (Codex has OS-enforced) | REFUTED | Claude Code [ships OS-enforced sandboxing](https://code.claude.com/docs/en/sandboxing): Seatbelt on macOS, bubblewrap+seccomp on Linux, bubblewrap on WSL2. Open-source runtime at [`@anthropic-ai/sandbox-runtime`](https://www.npmjs.com/package/@anthropic-ai/sandbox-runtime). Enabled via `/sandbox`. Residual differences: Codex default-on, Claude Code opt-in; Codex bakes it into the threat model from launch |
| OpenAI's reviewed-MCP-connector tier has no Anthropic analog | REFUTED | [Anthropic Connectors Directory](https://support.claude.com/en/articles/11596036-anthropic-connectors-directory-faq) — 398 verified connectors as of May 2026, vetted by Anthropic for security/reliability/compatibility, [listing criteria published](https://claude.com/docs/connectors/building/review-criteria). Genuine analog |
| Tenant-level admin plane is OpenAI-only | REFUTED (capability) / PARTIAL (UX) | Anthropic parent-org to child-org hierarchy with parent-level SSO/SCIM/domain verification and per-child role mapping. Real gap: not branded as a single named admin console |

## Compliance posture comparison table

| Cert/Capability | Anthropic | OpenAI | Notes |
|---|---|---|---|
| SOC 2 Type II | yes | yes (+ SOC 3) | parity |
| HIPAA / BAA | yes (Claude API, Enterprise, Claude Code CLI ZDR-only) | not published on Trust Portal | Anthropic advantage on regulated healthcare; OpenAI via Azure OpenAI separately |
| FedRAMP | High on [Claude for Government](https://support.claude.com/en/articles/13756069-public-sector-faqs); Claude Code/Cowork not yet in C4G envelope | Moderate (20x, April 2026) on ChatGPT Enterprise + API Platform; High only via Azure OpenAI | Anthropic leads at impact level; OpenAI ahead on which products are covered |
| ISO 27001 | 27001:2022 | 27001:2022 | parity |
| ISO 27017 / 27018 / 27701 | not surfaced on Trust Center | yes (all three) | OpenAI advantage on cloud-specific privacy certs |
| ISO 42001 | yes | yes | parity |
| BYOK / CMK | announced H1 2026, not yet GA | not published | both gaps |
| Zero data retention | yes (Enterprise addendum, API) | yes (API) | parity |
| GDPR / data residency | direct API US/global only; EU via Bedrock or Vertex | published GDPR docs | OpenAI more direct EU posture; Anthropic via cloud-provider re-deployment |
| PCI DSS | not surfaced | v4.0.1 | OpenAI advantage |
| CSA STAR | not surfaced | yes | OpenAI advantage |
| Audit log retention default | 180 days (Compliance API) | 30 days (Logs Platform) | Anthropic advantage |
| Audit log capture scope | admin/auth/resource events — no prompts/completions/tool calls | admin/auth/Codex usage/ChatGPT audit | OpenAI captures more inference-side data |

## Recommended corrections to consolidated.md

**Section 22 ("Global Admin Console + Compliance Logs Platform"):** rewrite the "no Anthropic analog" framing. Replace with: "Anthropic ships an equivalent capability set (parent-org tenant hierarchy + SCIM/SSO + 25-endpoint Admin API + Compliance API with ~30 typed events + connector directory) but does not market it as a single named portal. The discoverability gap is real; the capability gap is not. Note the inverse gap: Anthropic's Compliance API does not capture prompts/completions/tool calls; OpenAI's Codex Usage logs do."

**Section 23 ("Reviewed-MCP-connector tier"):** strike the "Anthropic publishes some MCPs but doesn't curate a third-party connector tier" claim. Replace with: "Both vendors run reviewed connector directories — Anthropic's at 398 verified entries as of May 2026, OpenAI's curated for Workspace Agents and ChatGPT Apps. Marketing prominence differs; the review program exists on both sides."

**Section 24 ("Codex `requirements.toml` enterprise floor"):** soften "Cleaner separation between admin floor and user config than Claude Code's `managed-settings.json` overloading both roles" — Claude Code's `managed-settings.json` is admin-only by design with its own separate file (`managed-mcp.json` for MCP); the criticism conflated the file name with overloading. Keep the naming critique (`requirements.toml` is more semantically pointed), drop the overloading claim.

**Platform applicability matrix row "OS-enforced sandbox":** flip Claude Code from "no (policy-only)" to "yes (Seatbelt / bwrap+seccomp / WSL2, OS-enforced via `/sandbox`)." Both vendors now ship OS-level sandboxing; the residual differentiation is "default-on (Codex) vs opt-in (Claude Code)" and Codex's WSL2/native-Windows posture.

**Platform applicability matrix row "Tenant-level admin plane":** flip from "no (per-machine managed)" to "yes (parent-org hierarchy + SCIM/SSO + Admin API)". Differentiator is named/branded portal UX, not capability.

**Quick heuristics table — last three rows:** rewrite all three.
- "Compliance log exports (JSONL, immutable)": both vendors ship. OpenAI default retention 30d vs Anthropic 180d; OpenAI captures inference-side, Anthropic does not.
- "Tenant-level multi-product admin": both vendors ship. OpenAI's is portal-branded; Anthropic's is API-first + parent-org.
- "OS-level sandbox enforcement": both vendors ship. Codex default-on, native WSL2 support; Claude Code opt-in via `/sandbox`.

**"What to validate in subsequent research passes":** strike "Compliance Logs Platform on Anthropic side: rumored unified audit/admin surface beyond per-machine managed-settings." It shipped (Compliance API, March 2026). Replace with: "Track Claude Code/Cowork inclusion in Claude for Government FedRAMP-High envelope (roadmapped 2026)" and "Track Anthropic BYOK GA (announced H1 2026)."

## Open questions for next pass

- Does Anthropic's Compliance API plan to add prompt/completion/tool-call capture? The current scope (resource/auth/admin only) is the most decision-blocking gap for regulated industries that need full conversation audit.
- When does Claude Code join the Claude-for-Government FedRAMP-High envelope? Today, a federal customer with High-impact data cannot use Claude Code under C4G.
- Does Anthropic publish ISO 27017/27018/27701? Not surfaced on Trust Center; either undisclosed or genuinely absent.
- BYOK GA timing — currently announced H1 2026 with no public GA confirmation as of 2026-05-18.
- Does Anthropic's parent-org admin gain a branded portal page (admin.claude.com analog)? Discoverability gap is the biggest single delta.
- Cowork roadmap into Compliance API and FedRAMP scope.
- OpenAI HIPAA/BAA — visibly absent from Trust Portal published certs; need to confirm whether available via direct enterprise contract.

## Sources

Anthropic:
- [Compliance API access](https://support.claude.com/en/articles/13015708-access-the-compliance-api)
- [Compliance API coverage analysis (General Analysis)](https://generalanalysis.com/guides/claude-compliance-api)
- [Claude Code on Team/Enterprise launch (Aug 2025)](https://www.anthropic.com/news/claude-code-on-team-and-enterprise)
- [Claude Code Security](https://code.claude.com/docs/en/security)
- [Claude Code Sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Claude Code Monitoring (OpenTelemetry)](https://code.claude.com/docs/en/monitoring-usage)
- [Claude Code Settings (managed-settings)](https://code.claude.com/docs/en/settings)
- [Trust Center](https://trust.anthropic.com/resources)
- [Certifications article](https://privacy.claude.com/en/articles/10015870-what-certifications-has-anthropic-obtained)
- [BAA for commercial customers](https://privacy.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers)
- [Public Sector FAQs (FedRAMP High)](https://support.claude.com/en/articles/13756069-public-sector-faqs)
- [Connectors Directory FAQ](https://support.claude.com/en/articles/11596036-anthropic-connectors-directory-faq)
- [SSO/SCIM setup](https://support.claude.com/en/articles/13132885-set-up-single-sign-on-sso)
- [Healthcare launch](https://www.anthropic.com/news/healthcare-life-sciences)
- [PwC partnership](https://www.anthropic.com/news/pwc-expanded-partnership)
- [Salesforce regulated industries](https://www.anthropic.com/news/salesforce-anthropic-expanded-partnership)

OpenAI:
- [Global Admin Console](https://help.openai.com/en/articles/12289294-global-admin-console)
- [Compliance Logs Platform quickstart](https://developers.openai.com/cookbook/examples/chatgpt/compliance_api/logs_platform)
- [Compliance APIs for Enterprise/Edu](https://help.openai.com/en/articles/9261474-compliance-apis-for-enterprise-customers)
- [API Platform Admin/Audit Logs](https://help.openai.com/en/articles/9687866-admin-and-audit-logs-api-for-the-api-platform)
- [FedRAMP Moderate (Apr 2026)](https://openai.com/index/openai-available-at-fedramp-moderate/)
- [ChatGPT Enterprise/Edu release notes](https://help.openai.com/en/articles/10128477-chatgpt-enterprise-edu-release-notes)
- [Trust Portal](https://trust.openai.com/)
