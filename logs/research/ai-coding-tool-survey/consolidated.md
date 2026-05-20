# Alignment Shapes for AI Coding Tools at Scale

Reference catalog of viable shapes for aligning AI coding tooling, rules, skills, governance, and cost across multiple projects and across vendors — plus footguns, organized by **platform applicability** since the alignment problem is multi-vendor.

**State of play (May 2026).** The ecosystem has converged. Claude Code, Codex, Cursor, Gemini CLI, JetBrains Junie, opencode, and GitHub Copilot Coding Agent all ship comparable plug-skill-hook-subagent-MCP stacks on top of a cross-tool substrate ([`AGENTS.md`](https://agents.md/) + `.agents/`, 60k+ projects). Differentiation for company-scale advisory has moved from "does the tool have shape X" to:

- **Enterprise compliance depth** — Windsurf (FedRAMP High + ITAR via Palantir FedStart), Cursor (SOC 2 + SIEM streaming), Anthropic Claude for Government (FedRAMP High, but not yet including Claude Code / Cowork).
- **Plugin model architecture** — markdown+frontmatter (Cursor, Junie, Gemini), JavaScript modules (opencode), YAML recipes (goose), TOML configs (Codex).

Substrate adoption itself has behavioral variance. Platform comparison:

- **Claude Code** — stays on `CLAUDE.md` / `.claude/` rather than the AGENTS.md substrate; `/init` reads AGENTS.md as a one-shot import.
- **Aider** — opts in via `read:` rather than auto-loading.
- **Zed** — surfaces AGENTS.md via `.rules` / CLAUDE.md interop.
- **Devin** — promiscuously reads `AGENTS.md` + `.cursorrules` + `.windsurf` + `CLAUDE.md` + `.mdc` + `.rules` with no canonical priority.

**Dual scope:** personal multi-project alignment (now) and company-scale advisory (next).

**Scope tags:** **(P)** personal multi-project · **(T)** small team · **(O)** organization-scale.

## Tradeoff axes

| Axis | Pole A | Pole B |
|---|---|---|
| Authority | Central (platform team owns) | Federated (each project owns) |
| Distribution direction | Push (org pushes config down) | Pull (projects opt in by version) |
| Enforcement | Hard gate (managed setting / hook blocks) | Soft norm (doc / convention) |
| Customization budget | Locked (managed, no deviation) | Layered (project overrides allowed) |
| Coupling | Tight (one canonical source) | Loose (many forks, eventual sync) |
| Surface | Native (settings / plugins / hooks) | Layered-on (docs / scripts / wiki) |
| Portability | Cross-tool substrate | Platform-specific |

The right pose on each axis depends on team maturity and trust. High-trust small team: all-federated, soft-norm, loose. Large org with compliance: closer to central / hard-gate / locked / platform-specific.

## Platform applicability matrix

Column key:

- **A** — Claude Code
- **B** — Codex CLI
- **C** — OpenAI Agents SDK
- **D** — ChatGPT / Workspace

| Shape | A | B | C | D |
|---|---|---|---|---|
| Layered config | X | X |   | X |
| Plugin marketplace † | X | X |   | X |
| Hooks | X | X | X | X |
| Subagents | X | X | X |   |
| Skills (`SKILL.md`+frontmatter) † | X | X |   |   |
| MCP † | X | X | X | X |
| Memory file † | X | X |   |   |
| Enterprise floor | X | X |   | X |
| Hosted agent (managed) | X | X | X | X |
| User-authored slash commands | X |   |   |   |
| OS-enforced sandbox | X | X |   |   |
| Tenant-level admin plane | X |   |   | X |
| Compliance log export | X | X |   | X |
| Vetted connector catalog | X |   |   | X |
| Server-hosted versioned prompts |   |   | X |   |
| Auto memory | X | X |   |   |

Empty cell = no native equivalent. Each row's nuance — protocol, scope, limitations, links — lives in the matching section below.

**† Cross-tool / vendor-neutral form exists** in addition to the per-tool implementations marked above — `AGENTS.md` + `.agents/` for memory file and skills, MCP as a cross-vendor protocol, and compatible `*-plugin/` registry shape (Claude Code's `.claude-plugin` and Codex's `.codex-plugin` interoperate via shared env aliases).

## Common shapes (cross-platform)

Shapes that appear in some recognizable form across Claude Code, Codex, and adjacent platforms. The safest bets for alignment work that spans vendors.

### 1. Layered configuration (foundation) — (P)(T)(O)

**What:** Hierarchy of config files; each layer overrides the layers below; topmost layer optionally locks fields. Platform comparison:

- **Claude Code** — enterprise-managed → command-line → project local → project shared → user ([settings docs](https://code.claude.com/docs/en/settings)).
- **Codex** — user `~/.codex/config.toml` → project `.codex/config.toml` (trust-gated on first load) → admin → `requirements.toml` ([reference](https://developers.openai.com/codex/config-reference)).

**Fits when:** Always. Every other shape sits on this foundation.

**Tradeoffs:** Settings only carry what the tool reads; rules/skills/memory content live elsewhere. Claude Code permission rules *merge* across scopes (not override). Codex requires explicit trust acknowledgment on first project-config load — mitigates supply-chain attacks via cloned repos.

**Notable expansions (May 2026):** Claude Code's [`managed-settings.d/`](https://code.claude.com/docs/en/settings) drop-in directory composes policy fragments alphabetically; `policyHelper` executable computes managed settings dynamically; Windows registry policies at `HKLM\SOFTWARE\Policies\ClaudeCode`. Files separate by role: `managed-settings.json` (admin), `managed-mcp.json` (MCP), project `settings.json` (shared), `settings.local.json` (user-local). Codex's `requirements.toml` is the admin floor distinct from regular `config.toml`.

### 2. Plugin marketplace — (P)(T)(O)

**What:** Git-hosted registry of installable bundles. Platform comparison:

- **Claude Code** — [`.claude-plugin/marketplace.json`](https://code.claude.com/docs/en/plugin-marketplaces); plugins bundle skills/commands/agents/hooks/MCP/[LSP servers](https://code.claude.com/docs/en/plugins)/background monitors/bin/.
- **Codex** — [`.codex-plugin/`](https://developers.openai.com/codex/plugins), launched 2026-03-27, with `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` env aliases for compatibility.

**Fits when:** Distributing reusable, composable units across multiple consumers; want versioning, discoverability, single source of truth.

**Tradeoffs:** Install/sync friction. Plugin scope must stay cohesive — kitchen-sink plugins become hard to opt into and impossible to deprecate piecemeal.

**Key 2026 governance shift — plugin dependencies:** Claude Code now has [first-class plugin deps](https://code.claude.com/docs/en/plugin-dependencies) with semver pinning via `{plugin-name}--v{version}` git tags and cross-marketplace deps via `allowCrossMarketplaceDependenciesOn`. `claude plugin disable` refuses if another enabled plugin depends on it. *Directly addresses* the Mega-plugin footgun: composition replaces bundling.

**OpenAI gap:** No open plugin marketplace surface. The role is split between Custom GPTs (deprecated), Workspace Agents (workspace-scoped, admin-curated), and the reviewed MCP-connector tier (curated, not user-publishable).

### 3. Subagent specialization — (P)(T)(O)

**What:** Specialized agents with restricted tools and focused prompts. Platform comparison:

- **Claude Code** — markdown+frontmatter at [`.claude/agents/`](https://code.claude.com/docs/en/sub-agents); ships Explore, Plan, general-purpose, code-reviewer, statusline-setup.
- **Codex** — TOML at `~/.codex/agents/` or `.codex/agents/` ([reference](https://developers.openai.com/codex/subagents)); ships `default`, `worker`, `explorer` with `agents.max_threads = 6` and `agents.max_depth = 1` defaults.
- **OpenAI Agents SDK** — `Handoffs` primitive in code.

**Fits when:** Work decomposes into clear specialist domains. Context window protection. Parallel work across independent tasks.

**Tradeoffs:** Dispatch overhead. Over-fragmentation. Subagent briefing must be careful per call. Codex's explicit fan-out caps are a tasteful default Claude Code currently leaves to convention.

**Anthropic 2026 additions:** Subagents can [preload skills](https://code.claude.com/docs/en/sub-agents) (`skills` field — full content injected at startup); persistent agent-scoped memory at `~/.claude/agent-memory/`; **forked subagents** via skill frontmatter `context: fork` + `agent: <name>` (skill becomes the agent's task prompt); [agent teams](https://code.claude.com/docs/en/agent-teams) and [background agent view](https://code.claude.com/docs/en/agent-view).

### 4. Hooks-based governance — (P)(T)(O)

**What:** Lifecycle hooks enforce policy. Platform comparison:

- **Claude Code** — [31 events](https://code.claude.com/docs/en/hooks) across session/turn/tool/subagent/tasks/environment/compact/worktree/notification/MCP lifecycles, with handler types beyond shell (`command`/`http`/`mcp_tool`/`prompt`/`agent`).
- **Codex** — [6 events](https://developers.openai.com/codex/hooks) (`SessionStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `Stop`).
- **OpenAI Agents SDK** — [RunHooks + AgentHooks + 3 guardrail families](https://openai.github.io/openai-agents-python/guardrails/) (input, output, tool).

**Composable sub-shapes:**

- **Audit logging** — every tool use, prompt, response emitted to central log.
- **Permission gates** — `if` field for permission-rule filters (Claude Code); `PermissionRequest` event (Codex).
- **Pre-flight cost estimation** — warn before expensive operations.
- **Convention gates** — path-glob-driven hooks block tool use that violates conventions.
- **Permission-decision via prompt/agent hook** (Claude Code 2026) — small fast model or agent decides whether to allow a tool call.
- **Tiered permission-decision in hook responses** — hooks return a structured verdict (`allow` / `ask` / `deny`) rather than just exit codes. Cross-vendor: GitHub Copilot Coding Agent's `hookSpecificOutput.permissionDecision: allow|ask|deny` ([hooks reference](https://docs.github.com/en/copilot/reference/hooks-configuration)), Windsurf's Cascade pre-hooks (exit code 2 to block), Claude Code's `prompt`/`agent` handlers. Converging cross-vendor sub-shape.

**Fits when:** Need enforcement beyond settings.json allow/deny. Audit and permission control land here.

**Known limitation on Claude Code (May 2026):** hook payloads omit token/cost data for `PostToolUse`, `Stop`, `UserPromptSubmit`; only the `Agent` tool's `PostToolUse` exposes token deltas. Ecosystem workaround: out-of-band parsing of `~/.claude/projects/*.jsonl` ([ccusage](https://github.com/ryoppippi/ccusage), [Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor)). Open issues: [#11008](https://github.com/anthropics/claude-code/issues/11008), [#52089](https://github.com/anthropics/claude-code/issues/52089), [#46089](https://github.com/anthropics/claude-code/issues/46089). For real-time quota gating, prefer Codex hooks (token deltas in payloads) or out-of-band log parsing.

**Tradeoffs:** Hooks proliferate without a registry pattern. Conflict resolution per-event. Hook failures can break workflows; need careful exit-code discipline. Claude Code's richer event taxonomy is more expressive; Codex's narrower set is simpler to reason about.

### 5. Enterprise managed floor — (O)

**What:** OS-level config that locks specific fields below user/project. Managed via MDM or config management. Platform comparison:

- **Claude Code** — `/etc/claude-code/managed-settings.json` (Linux), `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS, plus `com.anthropic.claudecode` preference domain for Jamf/Kandji), `C:\Program Files\ClaudeCode\managed-settings.json` (Windows, plus registry policies), drop-in directory, [`managed-mcp.json`](https://code.claude.com/docs/en/settings), managed-CLAUDE.md, dynamic `policyHelper`.
- **Codex** — [`requirements.toml`](https://developers.openai.com/codex/enterprise/admin-setup) with `allow_managed_hooks_only`, `[features]` enforcement, `managed_dir` for hook scripts, `guardian_policy_config`, `forced_login_method`, plugin allow/block policy.

**Fits when:** Compliance requires specific tools blocked, specific MCPs always enabled, specific audit hooks always on.

**Tradeoffs:** Requires MDM or equivalent. Managed settings should be the smallest non-bypassable floor — users can't deviate even when they should. Claude Code spreads admin/user/MCP separation across `managed-settings.json` + `managed-mcp.json` + `managed-CLAUDE.md`; Codex consolidates in `requirements.toml`. Both keep admin and user roles in separate files.

**MDM Managed Preferences as a cross-vendor floor mechanism:** macOS `.mobileconfig` Managed Preferences (Jamf / Kandji / FleetDM-deployable) is the standardized enterprise IT-managed configuration surface. Claude Code's `com.anthropic.claudecode` preference domain and [opencode's `.mobileconfig` support](https://opencode.ai/docs/config/) are early adopters. Worth considering alongside per-tool managed files when the org has MDM infrastructure.

### 6. Memory file convention — (P)(T)(O)

**What:** Project-rooted markdown file always loaded into context. Platform comparison:

- **Claude Code** — [`CLAUDE.md`](https://code.claude.com/docs/en/memory) at user/project root + `@path` imports up to depth 5 + managed-CLAUDE.md at policy paths + `claudeMdExcludes` for monorepo noise.
- **Codex** — [`AGENTS.md`](https://developers.openai.com/codex/guides/agents-md) concatenated from `$CODEX_HOME` down to cwd, with `AGENTS.override.md` per-directory + `project_doc_max_bytes` (default 32 KiB).

Same conceptual shape, divergent filenames.

**Fits when:** Project has non-obvious conventions, terminology, or orientation guidance. Cold pickups need fast onboarding.

**Tradeoffs:** Bloat is the failure mode — every line burns tokens every turn. Keep short, point to deeper docs.

**Cross-tool note:** `/init` in Claude Code reads existing `AGENTS.md`, `.cursorrules`, `.windsurfrules` and incorporates relevant parts — partial interop without full substrate adoption.

### 7. Path-scoped rules — (P)(T)(O)

**What:** Rule files that only fire when the agent is working on matching paths. Platform comparison:

- **Claude Code** — [`.claude/rules/`](https://code.claude.com/docs/en/memory) directory with glob-frontmatter on each rule file; symlinks supported for shared rule libraries.
- **Codex** — skill-frontmatter `paths` field plays a similar role for `.agents/skills/`.

**Fits when:** Discipline important only when working on certain file types or paths (test-authoring rules on test files; SQL conventions in migration directories).

**Tradeoffs:** Path glob discipline; risk of over- or under-firing. Direct alternative to "everything always-on" bloat.

### 8. MCP servers — (P)(T)(O)

**What:** [Model Context Protocol](https://modelcontextprotocol.io/) — open standard for tool servers. Platform comparison:

- **Claude Code** — [HTTP / stdio transports](https://code.claude.com/docs/en/mcp) (SSE deprecated), three scopes (`local`/`project`/`user`), [Channels for server-push events](https://code.claude.com/docs/en/channels), `Elicitation` hook events for mid-tool-call user input, auto-reconnect with exponential backoff.
- **Codex** — same protocol via `[mcp_servers.<id>]` in `config.toml`.
- **OpenAI Agents SDK** — [5 transport variants](https://openai.github.io/openai-agents-python/mcp/) including Hosted MCP (Responses API executes server-side).
- **ChatGPT Apps** — MCP via OAuth-CIMD.

**Fits when:** Capabilities need shared server-side logic (credential rotation, audit emission, internal-API gateways, RBAC). Or capability authors want versioning without each project bundling code.

**Tradeoffs:** Server infrastructure. Network dependency at runtime. Authoring complexity (transport choice, schema design). Latency accumulates if abused.

**Cross-platform reality:** MCP is the most fully cross-platform shape — same protocol, all major platforms speak it. Differentiation is in the *connector catalog* (next shape).

### 9. Vetted MCP connector catalog — (T)(O)

**What:** Vendor-curated catalog of pre-vetted MCP connectors employees can pull into agent runtimes. Platform comparison:

- **Claude** — [Anthropic Connectors Directory](https://support.claude.com/en/articles/11596036-anthropic-connectors-directory-faq), 398 vetted entries.
- **OpenAI** — reviewed-MCP-connector tier (Amplitude, Stripe, Vercel, Hex, etc.) used by Workspace Agents and ChatGPT Apps.

**Fits when:** Want governance over which MCPs employees can pull in; don't want to vet every third-party MCP yourselves.

**Tradeoffs:** Locked to vendor's reviewing throughput. Trades freshness/coverage for security/quality assurance.

### 10. Skills as units — (P)(T)(O)

**What:** Markdown files with name+description frontmatter that the agent runtime loads conditionally. Platform comparison:

- **Claude Code** — [`SKILL.md`](https://code.claude.com/docs/en/skills) with rich frontmatter (`when_to_use`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context: fork`, `agent`, `hooks`, `paths`, `shell`, `argument-hint`, `arguments`).
- **Codex** — same `SKILL.md`+frontmatter shape ([skills docs](https://developers.openai.com/codex/skills)), discovered from `.agents/skills/` and `~/.agents/skills/`.

Both follow the [Agent Skills open standard](https://agentskills.io).

**Fits when:** Discipline or capability that should load only when relevant — saves context budget vs. always-on.

**Tradeoffs:** Description-matcher fit is the dominant variable. In Claude Code, descriptions load up to a [1% context budget](https://code.claude.com/docs/en/skills) (`skillListingBudgetFraction`); per-skill cap is 1,536 chars (`maxSkillDescriptionChars`). `/doctor` diagnoses overflow. When budget overflows, least-invoked skills lose descriptions first.

**Visibility control:** Claude Code's `skillOverrides` setting (`on` / `name-only` / `user-invocable-only` / `off`) frees description budget by silencing third-party / plugin skills without editing their `SKILL.md`.

**Open-standard portability:** Same `SKILL.md` works across Claude Code and Codex with path adjustment (`.claude/skills/` vs `.agents/skills/`). Real-world repos already ship to both — see [netresearch/claude-code-marketplace](https://github.com/netresearch/claude-code-marketplace).

**Polyglot skill-path discovery (cross-tool):** Some tools read multiple skill-path conventions simultaneously. Platform comparison:

- **[opencode](https://opencode.ai/docs/skills/)** — discovers skills from `.opencode/skills/`, `.claude/skills/`, *and* `.agents/skills/` in one pass; turns "which path do we ship to?" into a non-question.
- **Cursor** — reads `.cursor/rules/` plus AGENTS.md.
- **JetBrains Junie** — reads `.junie/skills/` plus `.agents/skills/`.

When portability matters more than canonical paths, polyglot-reading tools are the bridge.

### 11. Compliance / governance log export — (O)

**What:** Vendor-emitted, immutable, structured logs of governance events. Platform comparison:

- **Anthropic** — [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api), GA 2026-03-30, ~30 typed events, JSON/CSV export, SIEM push (Splunk/Datadog/Elastic), **180-day retention**.
- **OpenAI** — [Compliance Logs Platform](https://help.openai.com/en/articles/11509118-admin-controls-security-and-compliance-in-apps-enterprise-edu-and-business) with immutable JSONL exports (Admin Audit, User Auth, Codex Usage), **30-day default retention**, broader scope (includes prompts, completions, tool calls).

**Fits when:** Regulated industries (finance, healthcare, government), org-wide audit requirements, anomaly detection.

**Tradeoffs across vendors:**

- **Anthropic Compliance API**: longer retention (180d vs 30d) but **does not capture prompts, completions, or tool calls** — governance events only. Decision-blocking for full conversation audit in regulated industries.
- **OpenAI Compliance Logs Platform**: shorter retention but captures the full conversation surface for Codex Usage.

If audit requires prompt/completion/tool-call content, OpenAI's catalog is broader; if governance-events-only with longer retention is enough, Anthropic's fits.

### 12. OpenTelemetry — (P)(T)(O)

**What:** Cross-platform observability via OTel exporters. Platform comparison:

- **Claude Code** — emits when `CLAUDE_CODE_ENABLE_TELEMETRY=1` ([monitoring docs](https://code.claude.com/docs/en/monitoring-usage)).
- **Codex** — emits when configured via `[otel]` block in `config.toml`.

The [GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/) (experimental, March 2026) standardize fields across vendors.

**Fits when:** Already running Datadog / Grafana / Honeycomb / SigNoz / Dynatrace; want a unified observability path that survives vendor churn. The most portable cost/usage telemetry shape.

**Tradeoffs:** Semantic conventions still maturing; field availability varies by emitter. Latency and storage costs of high-cardinality traces.

### 13. Tenant-level admin plane — (O)

**What:** Unified admin surface spanning multiple workspaces / products under one SSO + verified-domains tenant. Platform comparison:

- **Anthropic** — [Admin API](https://docs.anthropic.com/en/api/admin-api), 25 endpoints, parent-org → child-org hierarchy, cross-org SSO/SCIM.
- **OpenAI** — [admin.openai.com](https://help.openai.com/en/articles/12289294-global-admin-console) spanning ChatGPT workspaces and API orgs.

**Fits when:** Org needs single governance surface across multiple product lines from one vendor.

**Tradeoffs:** **Capability comparable; UX and marketing density differ.** OpenAI ships a unified web console; Anthropic's surface is API-centric without a prominent branded portal. For click-ops teams, OpenAI's UX is more developed. For automation-first ops, Anthropic's Admin API is the more programmable surface.

### 14. OS-enforced sandbox — (P)(T)(O)

**What:** OS-level sandboxing on the tool's tool-use (file write, process exec, network). Both vendors ship this. Platform comparison:

- **Claude Code** — [`/sandbox` + `@anthropic-ai/sandbox-runtime`](https://code.claude.com/docs/en/sandboxing) — Seatbelt on macOS, bubblewrap+seccomp on Linux, WSL2/native on Windows.
- **Codex** — same OS surface; modes `read-only` / `workspace-write` / `danger-full-access`.

**Fits when:** Untrusted code execution; agent operating with broad permissions where a misstep could damage the host.

**Tradeoffs:** Sandbox break is rare but possible (history of macOS Seatbelt escapes). Network egress controls vary. Both vendors use the same OS primitives — security ceiling is comparable.

### 15. Project starter / template repo — (T)(O)

**What:** Canonical `*-project-starter` repo new projects clone or scaffold from. Contains baseline `.claude/` or `.codex/`, memory file, conventions, baseline plugins enabled.

**Fits when:** Most projects share a baseline. Onboarding friction is real. Org wants consistency at project birth.

**Tradeoffs:** Drift — starters get stale; projects diverge after fork. Pairs with a "starter freshness" discipline.

### 16. Skill / rule distribution via package registry — (P)(T)

**What:** Skills, rules, or memory fragments published as npm/PyPI/git-tag packages and pulled into user-scope (`~/.claude/skills/`, `~/.agents/skills/`) by a one-liner. Claude Code's `checkpoint` skill describes both `installed` (npx user-scope) and `marketplace` (plugin cache) sync modes.

**Fits when:** Deliver author-side updates without each consumer touching plugin install machinery. Lighter than full plugin authoring for skill-only payloads.

**Tradeoffs:** Publishing pipeline. Private/internal use requires private-registry plumbing. Couples discovery to "did the user run the install script."

**Concrete:** [Renovate config presets](https://docs.renovatebot.com/config-presets/) — git-distributed instead of npm; closer analog than Prettier/ESLint for repos that don't want to publish to npm. [`gh extension`](https://docs.github.com/en/github-cli/github-cli/using-github-cli-extensions) for the low-ceremony git-distributed pattern.

### 17. Internal developer portal — (O)

**What:** Searchable catalog of available skills/plugins/MCPs with adoption metrics, documentation, onboarding paths. Often built on [Backstage](https://backstage.io/) — CNCF Incubating since 2022.

**Fits when:** Org has more shared AI tooling than a README can list. Discovery is a real bottleneck. Team-level adoption tracking matters.

**Tradeoffs:** Significant portal infrastructure. Metadata-rot if not maintained alongside tools.

**Alternatives:** Backstage is the dominant open shape; commercial alternatives include Port, Cortex, Compass, Roadie.

## Cross-tool portable substrate

Two substrates carry portability across vendors: one for *context* (AGENTS.md), one for *agent runtimes* (Agent Client Protocol). Orthogonal — a tool can adopt either, both, or neither.

### Context substrate: AGENTS.md + `.agents/` — (P)(T)(O)

**What:** Open file-convention substrate adopted across many AI coding tools. [`AGENTS.md`](https://agents.md/) is read by Codex, Cursor, Aider, goose, opencode, Zed, Devin, Copilot Coding Agent, Gemini CLI / Jules, JetBrains Junie, Windsurf, and others (60k+ projects). Companion path conventions: `.agents/skills/SKILL.md`, `.agents/plugins/marketplace.json`. Codex builds its full alignment stack on this substrate.

**Fits when:** Projects span tools (some on Claude Code, some on Codex, some on Cursor). Onboarding alignment work that should *not* lock you to a single vendor.

**Tradeoffs:** Claude Code is not on the substrate's primary path — stays on `CLAUDE.md` and `.claude/`, with `/init` reading AGENTS.md as a one-shot import (no live sync). Bridging Claude Code requires either (a) shipping both `.claude/` and `.agents/` from one repo (real examples: [duyet/codex-claude-plugins](https://github.com/duyet/codex-claude-plugins), [netresearch/claude-code-marketplace](https://github.com/netresearch/claude-code-marketplace)), (b) using `/init` for one-shot import, or (c) symlinking `CLAUDE.md` → `AGENTS.md` for read-only convergence on memory files.

**Behavioral variance within the adopter list:** Adoption is not uniform. Surveyed tools fall into four bands:

- **Full-stack adopters** — Cursor, Gemini CLI, Junie, opencode, Codex build their plug-skill-hook-subagent-MCP stacks on top of AGENTS.md / `.agents/` paths.
- **Memory-only adopters** — Aider, Zed surface AGENTS.md but don't build the extensibility stack. Aider opts-in via `read:` rather than auto-loading.
- **Hosted-managed adopters** — GitHub Copilot Coding Agent, Devin, Workspace Agents read AGENTS.md but govern sandbox + admin from vendor side rather than user/repo side.
- **Promiscuous readers** — Devin auto-pulls from `AGENTS.md`, `.cursorrules`, `.windsurf`, `CLAUDE.md`, `.mdc`, `.rules` — no canonical priority.

The same `AGENTS.md` file loads across these tools, but *priority*, *layering*, *override semantics*, and *nested-file handling* vary materially. Track [v1.1 spec proposal](https://github.com/agentsmd/agents.md/issues/135) to make these semantics explicit.

**Strategic call:** For company-scale advisory where the org uses multiple AI coding tools, the AGENTS.md substrate is the most portable *context* shape available today. Adopting it doesn't preclude Claude Code; it does mean shipping double config paths until Claude Code adopts (or you commit to single-vendor). For maximum bridge value, opencode-style polyglot-path readers minimize the duplication tax.

### Runtime substrate: Agent Client Protocol (ACP) — (T)(O)

**What:** [Zed's open Agent Client Protocol](https://zed.dev/acp) lets a single editor host *external* agent runtimes — Claude Agent, Gemini CLI, Codex — in one consistent UI panel. Where AGENTS.md ports the agent's *context*, ACP ports the agent *runtime itself*. Tool-side implementations exist for Claude Agent and Gemini CLI.

**Fits when:** Org wants editor flexibility (developers use whatever editor) without each developer running each vendor's CLI separately. Or a single editor needs to dispatch to multiple agent vendors based on task type.

**Tradeoffs:** Limited adopter set today — Zed is the primary host; cross-vendor agent embedding is novel. Protocol portability is real but not yet broad. Watch for adopter expansion.

**Concrete:** [ACP spec at zed.dev/acp](https://zed.dev/acp); Zed agent panel as the canonical implementation.

## Anthropic-specific shapes

### 18. Claude Agent SDK — (T)(O)

**What:** [Programmatic SDK](https://code.claude.com/docs/en/agent-sdk/overview) (Python + TypeScript) for embedding Claude in services, automated pipelines, scheduled jobs. TypeScript SDK bundles a native Claude Code binary — no separate install. Multi-cloud auth: Anthropic, AWS Bedrock, Claude Platform on AWS, Google Vertex AI, Azure AI Foundry.

**Fits when:** Production automation, scheduled jobs, customer-facing AI features, internal services off the IDE path.

**Tradeoffs:** SDK shares Claude Code's filesystem config by default — loads `.claude/skills/`, `.claude/commands/`, `CLAUDE.md`, and plugins from the working directory. Use `setting_sources` / `settingSources` to restrict.

**Quota note (effective 2026-06-15):** Agent SDK and `claude -p` usage on subscription plans draw from a new monthly Agent SDK credit bucket, separate from interactive usage.

### 19. Managed Agents (Anthropic-hosted REST API) — (T)(O)

**What:** [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) is a developer REST API where Anthropic runs the agent runtime and per-session sandbox. Public beta since 2026-04-09; early adopters Notion, Asana, Sentry. Composable APIs, isolated containers per session, native state + permission management.

**Fits when:** Want Anthropic to run runtime + sandbox for a production agent integration. Common pattern: prototype with Agent SDK locally, move to Managed Agents for production.

**Tradeoffs:** Vendor lock-in. Less filesystem-config sharing with Claude Code IDE than the Agent SDK has.

### 20. Auto memory — (P)

**What:** [Claude writes its own session notes](https://code.claude.com/docs/en/memory#auto-memory) to `~/.claude/projects/<project>/memory/`. First 200 lines / 25 KB of `MEMORY.md` loads each session. Controlled by `autoMemoryEnabled`. Distinct from `CLAUDE.md` (user-authored).

**Fits when:** Personal continuity across sessions. Captures incidentally-learned facts without burdening the user with writing them.

**Tradeoffs:** Quality is whatever Claude judged worth saving. Stale entries drift. No native team-share path — personal-scope by design.

### 21. Channels — (T)(O)

**What:** [MCP server-pushed events](https://code.claude.com/docs/en/channels) into a session via `claude/channel` (opt in with `--channels`). Telegram/Discord/CI integrations.

**Fits when:** Agent reacts to external events (CI failure, Slack mention, deploy completion) rather than user prompts only.

**Tradeoffs:** Request-response MCP is simpler. Channels require an event source and persistent connection.

### 22. LSP plugins + background monitors — (T)(O)

**What:** Language Server Protocol servers bundled in plugins for real-time code intelligence (`.lsp.json`). Background monitors (`monitors/monitors.json`) — `tail -F`-style streams that emit notifications into the session.

**Fits when:** Need editor-style code intelligence inside Claude Code; need to surface external state (build status, watcher output) without manual prompting.

**Tradeoffs:** Resource cost; orchestration complexity.

### 23. Skill router / dynamic dispatch (in-development / third-party) — (T)(O)

**What:** `UserPromptSubmit` hook embeds the prompt and matches it against a vector index of skill descriptions/exemplars, injecting matched skill pointers as a forcing function. Fixes the matcher's tendency to under-trigger on advisory skills.

**Fits when:** More than ~20 specialized skills exist and the description budget is exhausted (`/doctor` shows overflow). Want trigger reliability beyond the native matcher.

**Tradeoffs:** Requires embedding infrastructure. Threshold tuning. Match-quality risk.

**Concrete:** This repo's in-progress router POC; [darco81's skills-radar](https://github.com/darco81/skills-radar) (closest sibling); [K-Dense-AI's claude-skills-mcp](https://github.com/K-Dense-AI/claude-skills-mcp). See `logs/research/skill-router-prior-art.md`.

## Anthropic compliance posture

Concrete Anthropic-specific posture worth weighing in company-scale advisory work — both advantages and remaining gaps.

**Anthropic advantages over OpenAI specifically:**

- **FedRAMP High** on Claude for Government (April 2026) — OpenAI is FedRAMP Moderate.
- **HIPAA / BAA published** for Anthropic API — OpenAI's HIPAA/BAA is absent from the Trust Portal.
- **180-day retention on Compliance API** vs OpenAI's 30-day Logs Platform default.

**Anthropic gaps vs OpenAI specifically:**

- **Compliance API does not capture prompts, completions, or tool calls** — governance events only. OpenAI's Codex Usage logs cover the full conversation surface. Decision-blocking for full conversation audit in regulated industries.
- **Claude Code and Cowork are not yet in the Claude-for-Government FedRAMP-High envelope** — roadmapped 2026, not GA at writing.
- **ISO 27017, 27018, 27701, PCI DSS, CSA STAR not surfaced** on the Trust Center — OpenAI publishes all three ISO variants.
- **BYOK announced (H1 2026), no GA confirmation** as of 2026-05-18.

**Cross-vendor caveat (post-multi-vendor wave):** Anthropic's FedRAMP High is *not uniquely strong*. [Windsurf has FedRAMP High + ITAR + IL4/IL5](https://www.linkedin.com/posts/windsurf_codeium-has-achieved-fedramp-high-certification-activity-7307430545389428736-eIUh) via Palantir FedStart, plus SOC 2 Type II and HIPAA BAA. For defense / regulated-industry advisory, Windsurf's compliance posture is the deepest in the surveyed set. Cursor's enterprise floor (SOC 2 Type II + SIEM streaming via Splunk/Sumo Logic/Datadog/webhook/S3) is the second-tier baseline. JetBrains Junie and Gemini CLI inherit parent-corporate compliance (Google Cloud / JetBrains Trust Center). Treat compliance posture as *vendor-specific within the broader ecosystem*, not as a Claude-vs-OpenAI axis.

## OpenAI-specific shapes

### 24. OpenAI Codex CLI — (P)(T)(O)

**What:** [Apache-2.0 Rust CLI](https://github.com/openai/codex). One agent across CLI / IDE extension / desktop / cloud / ChatGPT with the same `config.toml`. Plugins and skills share across the product family.

**Differentiators worth naming (the rest are common shapes):**

- **Open-source license** (Apache 2.0) — forkable. Claude Code is closed-source binary.
- **Unified local↔cloud product family** — one agent across CLI / IDE / desktop / web / ChatGPT with shared customization stack.
- **PermissionRequest hook event** distinct from PreToolUse — approval-time policy without intercepting every tool call.
- **Hook payloads include token deltas** (verified gap on Claude Code side).

**Fits when:** Need open-source posture (forkable, public roadmap) or unified local↔cloud agent experience.

**Tradeoffs:** Narrower hook taxonomy (6 events vs Claude Code's 31). Slash commands not user-authored first-class. TOML config where Claude Code uses JSON.

### 25. Workspace Agents — (T)(O)

**What:** [Team-owned, always-on automation workers](https://openai.com/academy/workspace-agents/) powered by Codex. Scheduling, long-running tasks, 60+ enterprise connectors, custom MCP servers, admin controls. Launched 2026-04-22 on Business / Enterprise / Edu / Teachers. Replaced Custom GPTs.

**Fits when:** Org needs workspace-scoped (not per-user) shared automation. Scheduled work. Curated connector ecosystem desired.

**Tradeoffs:** Vendor lock-in to OpenAI / ChatGPT. Workspace-scoped — less suited to personal projects.

**Anthropic analog:** Managed Agents (REST API) — comparable hosted-agent shape with more developer-API framing than scheduled-team-worker framing.

### 26. Server-hosted versioned Prompts (Responses API) — (T)(O)

**What:** Project-scoped prompt library on OpenAI's servers, accessed by `prompt_id` (with optional `version` pin). Built-in versioning, diff, rollback, dashboard UI. Part of the [Responses API](https://developers.openai.com/api/reference/responses/overview), successor to Chat Completions + Assistants.

**Fits when:** Multiple services/clients need to reference the same prompt; want version control + rollback without managing it.

**Tradeoffs:** Vendor lock-in. **Anthropic has no analog** — prompt sharing in Claude-land is file-based via repos or plugins.

### 27. AGENTS.override.md — (P)

**What:** Codex's per-directory override file checked *before* `AGENTS.md`. Clean local-only memory layer that doesn't pollute shared `AGENTS.md`.

**Fits when:** Want per-developer / per-checkout overrides without forking shared memory.

**Tradeoffs:** Codex-specific (until Claude Code or others adopt). Claude Code's auto-memory plays an adjacent role (Claude-authored, not user-authored).

### 28. Custom GPTs (legacy, phasing out) — (P)

**What:** Bundle of instructions + actions (OpenAPI) + knowledge + capabilities, authored in ChatGPT. Per-user authoring with workspace-admin guardrails. [Help docs](https://help.openai.com/en/articles/8555535-gpts-chatgpt-enterprise-version).

**Status:** Being replaced by [Workspace Agents](https://openai.com/academy/workspace-agents/). Phase-out announced 2026-04-22.

**Mention only:** Don't build on this shape now.

## Adjacent prior art (analog patterns to learn from)

### DevContainer + dotfiles

Reproducible dev environments via [`.devcontainer/devcontainer.json`](https://containers.dev/) + [GitHub Codespaces](https://docs.github.com/en/codespaces) or local Docker. Dotfiles repos add personal config layers. The [Features](https://containers.dev/features) concept (composable add-ons) is a direct analog to plugins.

### Prettier / ESLint shareable configs

Configs published as npm packages — see [Prettier sharing configurations](https://prettier.io/docs/sharing-configurations) and [ESLint shareable configs](https://eslint.org/docs/latest/extend/shareable-configs). Projects extend with a one-liner; updates flow through package version bumps. Strongest precedent for shareable AI-tool config.

### Renovate config presets

[Repo-hosted shareable presets](https://docs.renovatebot.com/config-presets/) referenced as `github>org/repo` — no npm publishing required. Version pinning via git refs. Tighter analog to "git-distributed Claude config" than Prettier/ESLint.

### GitHub Actions reusable workflows

[`workflow_call` + typed inputs/secrets](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) — composable, versioned workflow templates referenced by `org/repo/.github/workflows/x.yml@ref`. Direct analog to "shareable slash-command-as-workflow."

### Terraform modules / Helm charts

Composable infrastructure templates. Versioned, registry-hosted, parameterized — [Terraform modules](https://developer.hashicorp.com/terraform/language/modules), [Helm charts](https://helm.sh/docs/topics/charts/). Plugin marketplaces follow this shape.

### Backstage / internal developer portals

[Backstage](https://backstage.io/) — CNCF Incubating; dominant open IDP. Self-service catalog of tools, services, templates. Commercial alternatives: Port, Cortex, Compass, Roadie.

### oclif (CLI plugin framework)

[oclif](https://oclif.io/) — framework underneath `sf` (Salesforce) and Heroku CLI. Native plugin model: `sf plugins install <pkg>` and the CLI gains new top-level commands. Direct architectural analog to "AI coding CLI that hosts plugins."

### gh CLI extensions

[`gh extension install`](https://docs.github.com/en/github-cli/github-cli/using-github-cli-extensions) — user-scoped, git-repo-distributed extensions named `gh-<extension>`. Lighter than oclif; closer to "skill packages distributed via git URL." Low-ceremony, registry-free.

### Krew (kubectl plugin manager)

[Krew](https://krew.sigs.k8s.io/) — community-curated, cross-platform plugin index for `kubectl`. The *separate-package-manager-for-a-host-CLI* shape: SIG-governed plugin index, manifest-based publishing, audited curation.

### Salesforce CLI `sf` (v2)

[Salesforce CLI](https://developer.salesforce.com/tools/sfdxcli) — canonical "internal CLI distribution at company scale" example. Built on oclif. Note: `sfdx` (v7) is deprecated; the current product is `sf` (v2). Centralized authentication, audit, versioning.

### Stripe CLI

[Stripe CLI](https://docs.stripe.com/stripe-cli) — opinionated, auth-aware vendor CLI distribution. Reference for "first-party CLI as an alignment / governance surface."

### Open Policy Agent / Rego

[OPA](https://www.openpolicyagent.org/) — org-policy-as-code engine. The "hard gate" pole of enforcement. Externalized policy expressed in Rego, queried by hooks/gateways. Canonical reference if policy-as-code becomes its own sub-shape.

### FinOps Foundation — AI working group

[FinOps for AI](https://www.finops.org/wg/finops-for-ai-overview/) — emerging discipline for AI spend attribution and chargeback. Published frameworks for generic LLM spend; case studies for IDE-assistant chargeback specifically remain thin (early in the adoption curve).

## Footguns and shapes to recognize

### Currently-popular-but-problematic

#### CLAUDE.md / AGENTS.md as catch-all

**Appeal:** Easy to dump everything you want the agent to remember. No infrastructure.
**Why it breaks:** Every line burns tokens every turn. Lossy under context-window pressure. Hard to maintain. Rule rot. Tempts dumping non-universal rules that should be on-demand.
**Better:** Tight always-on subset; trigger-loaded skills + `.claude/rules/` path-scoped rules for the rest. Cap memory file at a few hundred lines max.

#### Empty-description skills hoping for matcher magic

**Appeal:** Skill is in `.claude/skills/`, will fire if needed, no description-authoring work required.
**Why it breaks:** The matcher under-triggers reliably on advisory/discipline skills. Empty-description skills don't fire. Net effect: dead code disguised as available capability.
**Now diagnosable:** `/doctor` surfaces description-budget overflow; configurable via `skillListingBudgetFraction` (default 1%) and `maxSkillDescriptionChars` (default 1,536). Free budget with `skillOverrides` to silence noisy third-party skills.
**Better:** Author a real description that encodes the cognitive moment (see `description-authoring` skill), or move to direct-invocation-only and don't pretend it's auto-firing.

#### Mega-plugin

**Appeal:** One install, many capabilities. Less marketplace clutter.
**Why it breaks:** Forces consumers into the whole bundle. Update cycle locks all capabilities together. Hard to deprecate individual pieces.
**Now mitigated:** Claude Code's [first-class plugin dependencies](https://code.claude.com/docs/en/plugin-dependencies) (semver-constrained, `claude plugin disable` refuses if depended on, cross-marketplace deps via `allowCrossMarketplaceDependenciesOn`) let small focused plugins compose without bundling.
**Better:** Small focused plugins (`git`, `review`, `release`) declaring deps where they need each other.

#### Hook proliferation without registry

**Appeal:** Each concern gets its own hook; easy to author.
**Why it breaks:** Overlapping hooks fire in unspecified order. Conflict resolution is per-event. Debugging "why did this fire / not fire" becomes archaeology.
**Better:** Hook registry pattern — one entry per concern, declared dependencies, explicit ordering. Or consolidate related hooks into one well-tested module per event type. Claude Code's `agent` and `prompt` hook handler types reduce shell-script proliferation by letting an agent or fast-model decide policy in one place.

#### Hook-based cost gating on Claude Code without token data

**Appeal:** Hooks are the obvious surface for quota enforcement.
**Why it breaks:** As of May 2026, Claude Code hook payloads for most events (`PostToolUse`, `Stop`, `UserPromptSubmit`) **do not include token or cost deltas** — only the `Agent` tool's `PostToolUse` does. A naive hook-based quota gate has nothing to gate on.
**Better today:** Out-of-band parsing of `~/.claude/projects/*.jsonl` ([ccusage](https://github.com/ryoppippi/ccusage) is canonical); OTel emitter; or skill-based pre-flight estimation. Track [#11008](https://github.com/anthropics/claude-code/issues/11008) for native fix.
**Cross-platform alternative:** Codex hook payloads include token deltas; that side of the multi-tool reality already supports the naive pattern.

### Obsolete-but-still-followed

#### Wiki/Confluence-as-discipline

**Appeal:** Familiar; everyone has a wiki; "the way we do it" goes there.
**Why it broke:** Discipline-by-doc-without-enforcement = drift. The doc says one thing, the code does another, nobody knows which to trust. Worked in the pre-tooling era when humans owned the contract; doesn't work when an LLM is the contract-reader.
**Now better via:** Hooks (enforce), managed settings (lock), skills (load the discipline at trigger time).

#### Slack / Discord pastebin distribution

**Appeal:** "Here's a prompt I use, copy it" — frictionless sharing.
**Why it broke:** Untracked, unversioned, lost in channel history. No update propagation.
**Now better via:** Even a private git repo with a README. Plugin marketplace if worth versioning. Renovate-style presets for repo-distributed configs.

#### Per-developer-individual config (no alignment at all)

**Appeal:** Maximum autonomy. Everyone configures their own `~/.claude` or `~/.codex` however they want.
**Why it broke:** Zero alignment. "Works on my machine" is the dominant failure mode. New hires have nothing to start from. Audit/compliance impossible.
**Now better via:** Layered config — project-scope baseline + user-scope overrides.

#### "Just prompt right" / discipline-as-norm

**Appeal:** No infrastructure. "We just tell people to write good prompts."
**Why it broke:** Depends on individual diligence. Doesn't scale past a small high-trust team. New members spend months learning unwritten norms.
**Now better via:** Encode the norms in skills, rules, or hooks. Make the discipline part of the tooling, not the culture.

### Subtle anti-patterns (often invisible until they hurt)

#### Mirroring instead of sourcing

**Appeal:** Copy the skill/rule into your project; you control it; no marketplace dependency.
**Why it breaks:** Forks drift silently. Bug fixes in canonical source never reach mirrors. Improvements stay local.
**Better:** Source from canonical (plugin marketplace, npx-published package, Renovate-style preset). Edit downstream only via fork-PR-back.

#### API-cost-thinking when on subscription quota

**Appeal:** Familiar mental model — "how many dollars did that cost?"
**Why it breaks:** Subscription users (Claude Max, Claude Code Pro, ChatGPT Enterprise) burn quota, not dollars. Optimizing for dollar cost when the constraint is quota leads to wrong tradeoffs.
**2026 note:** Claude Code's Agent SDK draws from a separate monthly Agent SDK credit bucket on subscription plans (effective 2026-06-15). The subscription-quota path covers SDK too — with its own ceiling distinct from interactive use.
**Better:** Cost analysis in the actual constraint — subscription-quota burn, session-context tokens, daily message limits.

#### Rule-skill confusion (everything always-on)

**Appeal:** "If it's important, it should always be loaded."
**Why it breaks:** Most rules are situationally important. Always-on for situational guidance bloats context and dilutes attention.
**Better:** Tight universal subset always-on (honesty, basic discipline). Everything else on-demand via skill loading, path-scoped rules, or slash invocation.

#### Plugin marketplace as the only sharing shape

**Appeal:** "We have plugins; everything goes through plugins."
**Why it breaks:** Plugins are good for cohesive units. Bad for cross-cutting concerns (org-wide audit hook, single global rule).
**Better:** Right shape for the concern. Plugins for cohesive units; managed settings for floors; MCP for shared capabilities; npx/git-preset for skill packages; portal for discovery.

#### Authority centralization without escape hatches

**Appeal:** Strong governance, single source of truth.
**Why it breaks:** Real work hits cases the central authority hasn't anticipated. Without escape hatches, teams work around the system or productivity drops.
**Note on Claude Code:** Permission rules *merge* across scopes rather than override — central permissions add to project permissions rather than replace.
**Better:** Central baseline + per-project layering. Managed settings should be the minimum compliance floor, not the whole config.

#### Single-vendor commitment in a multi-vendor reality

**Appeal:** Pick one tool, align everyone, simpler.
**Why it breaks:** Different teams adopt different AI coding tools. Cursor for some, Codex for others, Claude Code for a third. Single-vendor alignment work doesn't transfer.
**Better:** Adopt the [`AGENTS.md`](https://agents.md/) substrate where it covers your case. Ship both `.claude/` and `.agents/` from the same source where you need Claude Code coverage. Accept the path-duplication tax as the cost of portability.

#### Asserting gaps without verification

**Appeal:** "Vendor X doesn't have Y" is tempting shorthand based on a single doc page.
**Why it breaks:** Vendor docs are uneven in marketing density. Anthropic ships features (Compliance API, OS sandbox, Connectors Directory, tenant Admin API) without front-page marketing; OpenAI markets them prominently. An early pass over this same material asserted five gaps against Anthropic that turned out to be wrong on verification — including the entire compliance-logs gap.
**Better:** Before asserting "no analog," check Trust Centers, Admin APIs, and the platform's own support center. The gap may be in marketing or UX, not in capability.

## Quick heuristics

| Concern | First reach for |
|---|---|
| Consistent permissions across projects | Layered settings + managed floor (managed-settings.json / requirements.toml) |
| Sharing reusable skill + command + hook bundles | Plugin marketplace (with deps, not bundling) |
| Centralized capability with audit/auth | Internal MCP server |
| Token/cost controls on Claude Code | Out-of-band log parsing (ccusage / OTel) until hook payload fix lands |
| Token/cost controls on Codex | Hook-based gates (token deltas in payloads) |
| Cross-platform token/cost telemetry | OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1`, Codex `[otel]` block) |
| Onboarding consistency | Project starter + plugin marketplace |
| Auto-fire discipline when matcher under-triggers | Skill router or path-scoped rules (`.claude/rules/`) |
| Production automation off the IDE path | Agent SDK (Claude) or Agents SDK (OpenAI) |
| Org-wide governance with minimal infra | Managed enterprise floor + Backstage |
| Discoverability at org scale | Internal dev portal (Backstage / Port / Cortex) |
| Multi-vendor alignment | AGENTS.md substrate; ship double paths if needed |
| Per-developer overrides | User-scope config + `AGENTS.override.md` (Codex) or `settings.local.json` (Claude) |
| OS-level sandbox enforcement | Both vendors ship it; use `/sandbox` (Claude) or Codex's modes |
| Server-hosted versioned prompts | OpenAI Responses API Prompts — no Anthropic analog |
| Tenant-level multi-product admin | Admin API (Anthropic, API-centric) or admin.openai.com (OpenAI, UX-centric) |
| Governance log export | Compliance API (Anthropic, 180d, governance events) or Compliance Logs Platform (OpenAI, 30d, includes prompts/tools) |
| FedRAMP High posture | Windsurf (FedRAMP High + ITAR + IL4/IL5 via Palantir FedStart) or Anthropic Claude for Government (not yet including Claude Code / Cowork) |
| HIPAA/BAA coverage | Anthropic API (published) or Windsurf (HIPAA BAA published) or Google Cloud via Gemini Enterprise; OpenAI does not publish BAA |
| Regulated-industry / defense compliance depth | Windsurf — FedRAMP High + ITAR + HIPAA + IL4/IL5 + air-gap self-host |
| Polyglot org with mixed AI coding tools | opencode (reads `.claude/` + `.agents/` + `.opencode/` paths simultaneously); Devin (promiscuous reader of multiple memory-file conventions) |
| Cross-vendor agent runtime embedding | Zed via [Agent Client Protocol](https://zed.dev/acp) — single editor hosts Claude Agent / Gemini CLI / Codex |

## What to validate in subsequent research passes

The cost-attribution, compliance-audit, and multi-vendor-adopters waves answered most earlier open questions. Remaining gaps:

- **AGENTS.md v1.1 spec — adoption semantics standardization** — [proposal #135](https://github.com/agentsmd/agents.md/issues/135) aims to make priority, layering, override, and nested-file handling explicit. Track when ratified and which adopters update.
- **22 cells marked `unverified` in the multi-vendor wave** — primarily OTel emission on most non-Claude-Code/non-Codex tools, server-hosted prompts, compliance log export for Junie/Continue/Zed/Devin. Targeted resample pass worthwhile.
- **Anthropic Compliance API event expansion** — does the roadmap include capturing prompts/completions/tool calls? Would close the conversation-audit gap.
- **Claude Code FedRAMP-High inclusion** — track when Claude Code / Cowork join the Government envelope (roadmapped, not GA).
- **Anthropic ISO 27017/27018/27701, PCI DSS, CSA STAR** — track Trust Center additions.
- **Windsurf-style FedRAMP High at scale** — case studies on regulated-industry deployments of Windsurf vs Anthropic Claude-for-Government vs Google Cloud / Gemini Enterprise.
- **Agent Client Protocol adopter expansion** — Zed is the primary host; track whether Cursor / Junie / others adopt ACP for cross-vendor agent runtime portability.
- **Channels adoption parity** — Claude Code's [Channels](https://code.claude.com/docs/en/channels) is novel; does Codex ship an analog?
- **Plugin dependency conventions cross-vendor** — Claude Code shipped first-class deps; does Codex / Cursor / Gemini CLI follow?
- **Workspace Agents maturation** — scheduling primitives, connector review throughput, credit billing transparency.
- **Skill router consolidation** — third-party POCs are diverging; does Anthropic ship a first-party router, or does the matcher get smart enough to retire the pattern?
- **OPA / policy-as-code integration** — concrete examples of Rego wired to hooks or managed-settings governance.
- **Codex / Windsurf / Cursor enterprise adoption stories** — case studies on `requirements.toml`-style floor configurations and SIEM streaming at named companies.

Subsequent research waves should each target one of these and produce a `wave-<topic>.md` alongside this consolidated doc.

## Sources

- Cross-tool substrate: [agents.md](https://agents.md/).
- Anthropic: [Claude Code docs](https://code.claude.com/docs/en/), [Claude Platform docs](https://platform.claude.com/docs/en/), [Admin API](https://docs.anthropic.com/en/api/admin-api), [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api), [Anthropic Connectors Directory FAQ](https://support.claude.com/en/articles/11596036-anthropic-connectors-directory-faq), [Trust Center](https://trust.anthropic.com/).
- OpenAI: [OpenAI developers](https://developers.openai.com/), [Codex docs](https://developers.openai.com/codex), [Agents SDK](https://openai.github.io/openai-agents-python/), [Workspace Agents](https://openai.com/academy/workspace-agents/), [Global Admin Console help](https://help.openai.com/en/articles/12289294-global-admin-console), [Compliance Logs Platform](https://help.openai.com/en/articles/11509118-admin-controls-security-and-compliance-in-apps-enterprise-edu-and-business), [Trust Portal](https://trust.openai.com/).
- Cost / observability: [ccusage](https://github.com/ryoppippi/ccusage), [Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor), [GenAI OTel semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/), [FinOps for AI](https://www.finops.org/wg/finops-for-ai-overview/), [Anthropic monitoring usage](https://code.claude.com/docs/en/monitoring-usage).
- Prior art: [DevContainer](https://containers.dev/), [Backstage](https://backstage.io/), [oclif](https://oclif.io/), [Krew](https://krew.sigs.k8s.io/), [Renovate config presets](https://docs.renovatebot.com/config-presets/), [GitHub Actions reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows), [Open Policy Agent](https://www.openpolicyagent.org/), [Salesforce CLI sf v2 migration](https://developer.salesforce.com/docs/atlas.en-us.sfdx_setup.meta/sfdx_setup/sfdx_setup_move_to_sf_v2.htm).
