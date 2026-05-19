# Wave: Claude Code platform verification

Verification of Claude-Code-specific shapes in `consolidated.md` against current Anthropic documentation as of 2026-05-18.

**Important meta-finding:** All `docs.anthropic.com/en/docs/claude-code/` URLs now 301-redirect to `code.claude.com/docs/en/<page>` (Claude Code split into its own docs domain). Agent SDK lives at `code.claude.com/docs/en/agent-sdk/`. Update all URLs in the consolidated doc to canonical `code.claude.com` paths.

## Per-shape verification

### 1. Layered configuration (settings.json hierarchy)

- **Doc claim:** Enterprise-managed → command-line → project local → project shared → user.
- **Status:** current — precedence order matches exactly.
- **Canonical URL:** [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)
- **Updates since cutoff:**
  - Managed-settings drop-in directory `managed-settings.d/` (alphabetical merge, arrays concat, objects deep-merge) — useful for federated policy fragments.
  - New top-level keys: `skillOverrides` (v2.1.129), `skillListingBudgetFraction` and `maxSkillDescriptionChars` (v2.1.105), `policyHelper` (v2.1.136, admin-deployed executable for dynamic managed settings), `parentSettingsBehavior` (v2.1.133), `worktree.bgIsolation` (v2.1.143), `disableRemoteControl` (v2.1.128), `claudeMd` (managed-only; inlines a CLAUDE.md into managed settings).
  - Windows managed path migrated from `C:\ProgramData\ClaudeCode\` to `C:\Program Files\ClaudeCode\` as of v2.1.75 (legacy path deprecated). Windows Registry policies under `HKLM\SOFTWARE\Policies\ClaudeCode` are also recognized.
  - Permission rules **merge** across scopes rather than override — relevant to the "Authority centralization" footgun.
- **Doc gaps:** Doc omits the drop-in directory pattern, `policyHelper`, and registry-based Windows policies — all enterprise-relevant.

### 2. Plugin marketplace

- **Doc claim:** `.claude-plugin/marketplace.json` Git-hosted; plugins bundle skills/commands/agents/hooks/MCP.
- **Status:** partially current — accurate but materially incomplete.
- **Canonical URLs:** [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins), [code.claude.com/docs/en/plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [code.claude.com/docs/en/plugins-reference](https://code.claude.com/docs/en/plugins-reference)
- **Updates since cutoff:**
  - Plugins can additionally bundle **LSP servers** (`.lsp.json`), **background monitors** (`monitors/monitors.json`), **bin/** executables added to Bash `PATH`, and plugin-level **`settings.json`** (currently honors only `agent` and `subagentStatusLine` keys).
  - **Plugin dependencies** are now a first-class feature: cross-plugin deps, semver pinning via `{plugin-name}--v{version}` git-tag convention, and `allowCrossMarketplaceDependenciesOn` in marketplace.json. `claude plugin disable` refuses if another enabled plugin depends on it (v2.1.143).
  - New marketplace fields: `displayName` (v2.1.143, human-readable name), `$schema` for editor validation, multi-source types (`github`, `url`, `git-subdir`, `npm`, local path).
  - Custom commands have been **merged into skills** — `.claude/commands/*.md` still works but skills are the recommended path.
  - `--plugin-dir` accepts `.zip` archives (v2.1.128+); `--plugin-url` fetches archives at session start; `/reload-plugins` for in-session updates.
  - Official in-app submission flow for the Anthropic marketplace via claude.ai/settings/plugins/submit.
- **Doc gaps:** No mention of LSP/monitors/bin, no mention of plugin dependencies (which is the biggest 2026 governance shift — directly relevant to the "Mega-plugin" footgun, now mitigatable via deps rather than bundling).

### 3. Internal MCP servers

- **Doc claim:** stdio / SSE / HTTP transports; `.claude/settings.json` or plugin-bundled.
- **Status:** changed — SSE deprecated.
- **Canonical URL:** [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)
- **Updates since cutoff:**
  - **SSE transport is deprecated** — HTTP is the recommended remote transport. `streamable-http` is accepted as a JSON-config alias for `http`.
  - Scope naming changed: `local` (was `project`), `project` (shared via `.mcp.json`), `user` (was `global`). MCP local-scope is **stored in `~/.claude.json`**, distinct from settings-local-scope at `.claude/settings.local.json`.
  - **Managed MCP** via `managed-mcp.json` alongside `managed-settings.json` at enterprise paths.
  - Dynamic tool updates via MCP `list_changed` notifications.
  - Auto-reconnect with exponential backoff for HTTP/SSE (up to 5 attempts); initial-connect retry up to 3 times on transient errors (v2.1.121+).
  - **Channels** capability: MCP servers can push events into a session via `claude/channel` (opt in with `--channels` flag) — major shape addition for "agent reacts to external events."
  - **MCP elicitation**: new `Elicitation`/`ElicitationResult` hook events for MCP-prompted user input mid-tool-call.
- **Doc gaps:** SSE-deprecated should be called out; channels concept is missing entirely; managed-MCP path is missing.

### 4. Hooks-based governance

- **Doc claim:** PreToolUse, UserPromptSubmit, PreCompact, Stop, SessionStart; quota/audit/permission/cost-estimation/convention sub-shapes.
- **Status:** partially current — list is wildly incomplete.
- **Canonical URL:** [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- **Updates since cutoff:** The current hook surface is **31 events**, organized into lifecycles. New/uncovered events:
  - Session: `Setup`, `SessionEnd`, `StopFailure`
  - Turn: `UserPromptExpansion`
  - Tool: `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied`
  - Subagent/teams: `SubagentStart`, `SubagentStop`, `TeammateIdle`
  - Tasks: `TaskCreated`, `TaskCompleted`
  - Environment: `CwdChanged`, `FileChanged`, `ConfigChange`, `InstructionsLoaded`
  - Compact: `PostCompact`
  - Worktree: `WorktreeCreate`, `WorktreeRemove`
  - Notification: `Notification`
  - MCP: `Elicitation`, `ElicitationResult`
  - Also new: **hook handler types beyond `command`** — `http`, `mcp_tool`, `prompt` (uses a fast model to decide), `agent` (uses an agent to decide). This dramatically expands hook authoring beyond shell scripts.
  - Hooks can now live in skill/agent frontmatter (scoped to the component's lifecycle) and in plugin `hooks/hooks.json`.
  - `if` field for permission-rule-style filters on tool events (e.g. `if: "Bash(git *)"`).
- **Doc gaps:** Missing `PostToolUse` (the most common hook in practice), `SessionEnd`, `InstructionsLoaded`, `SubagentStop`, and the new non-command hook types. Sub-shapes catalog is roughly right but missing "permission-decision via prompt/agent hook" pattern.

### 5. Enterprise managed settings

- **Doc claim:** Linux `/etc/claude-code/managed-settings.json`; macOS `/Library/Application Support/ClaudeCode/managed-settings.json`.
- **Status:** current with significant additions.
- **Canonical URL:** [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings) (managed section)
- **Updates since cutoff:**
  - Windows: `C:\Program Files\ClaudeCode\managed-settings.json` plus registry-based policies (`HKLM\SOFTWARE\Policies\ClaudeCode`, `HKCU\SOFTWARE\Policies\ClaudeCode`).
  - macOS managed preferences domain `com.anthropic.claudecode` for Jamf/Kandji MDM.
  - Drop-in directory `managed-settings.d/` for policy-fragment composition.
  - `managed-mcp.json` for org-wide MCP servers.
  - **Managed CLAUDE.md** at the same paths (e.g. `/etc/claude-code/CLAUDE.md`) or inline via the `claudeMd` key in managed settings.
  - `policyHelper` executable for dynamic managed-settings computation.
  - `parentSettingsBehavior` ("first-wins" / "merge") for SDK/IDE-supplied parent settings.
- **Doc gaps:** The doc treats managed settings as a single floor; in 2026 it's a layered system (managed file + drop-in dir + registry + dynamic policy helper + managed CLAUDE.md + managed MCP).

### 6. Always-on rules / CLAUDE.md hierarchy

- **Doc claim:** CLAUDE.md at user/project + small always-on universal subset; treat as tight token budget.
- **Status:** current with notable additions.
- **Canonical URL:** [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)
- **Updates since cutoff:**
  - **Auto memory** (v2.1.59+): Claude writes its own notes to `~/.claude/projects/<project>/memory/`; first 200 lines / 25KB of `MEMORY.md` loads each session. Controlled by `autoMemoryEnabled` setting.
  - **`.claude/rules/`** directory for path-scoped (glob-frontmatter) rules — addresses the "everything always-on" footgun directly. Symlinks supported for shared rule libraries.
  - **Managed CLAUDE.md** at policy paths (cannot be excluded by users); `claudeMd` key inlines managed-CLAUDE.md content in managed-settings.json.
  - `claudeMdExcludes` setting (with array-merge across layers) for monorepo noise.
  - `AGENTS.md` interop: `/init` reads existing AGENTS.md, `.cursorrules`, `.windsurfrules` and incorporates relevant parts.
  - Block-level HTML comments stripped before injection (cheap maintainer notes).
  - `@path` imports recursive to depth 5.
- **Doc gaps:** Missing `.claude/rules/` (a near-perfect implementation of "load on demand by path" that the doc's "small universal subset" recommendation can now lean on); missing auto-memory entirely (this is a major new shape — Claude-authored persistent notes); missing AGENTS.md interop (relevant to "OpenAI/Codex CLI alignment" wave).

### 7. Slash commands as workflows

- **Doc claim:** Multi-step workflows packaged as slash commands.
- **Status:** changed — commands and skills have merged.
- **Canonical URLs:** [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills), [code.claude.com/docs/en/commands](https://code.claude.com/docs/en/commands)
- **Updates since cutoff:**
  - **Custom commands have been merged into skills.** `.claude/commands/*.md` and `.claude/skills/*/SKILL.md` both create the same `/name` invocation. Skills are now the recommended authoring path; commands are legacy-compatible.
  - This means the doc's "Slash-command-as-workflow" shape (#8) and "Skills and skill descriptions" shape (#11) are increasingly **the same shape** with different framings — worth collapsing or at minimum cross-referencing.
- **Doc gaps:** Doesn't acknowledge the merge — readers following the doc may build a `.claude/commands/` library that should now be `.claude/skills/`.

### 8. Subagent specialization (`.claude/agents/`)

- **Doc claim:** Specialized prompts and tool restrictions; Anthropic ships Explore/Plan/general-purpose/etc.
- **Status:** current with major additions.
- **Canonical URL:** [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
- **Updates since cutoff:**
  - Subagents can **preload skills** (`skills` field) — full skill content injected at agent startup, not just descriptions.
  - Subagents support **persistent memory** at `~/.claude/agent-memory/` (separate from main auto-memory).
  - **Forked subagents** via skill frontmatter `context: fork` + `agent: <name>`: skill content becomes the agent's task prompt. Inverse pattern from old "agent invokes skill."
  - Explore and Plan skip CLAUDE.md and git status to keep their context small.
  - Background-agent view and agent teams: see [code.claude.com/docs/en/agent-view](https://code.claude.com/docs/en/agent-view), [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams).
- **Doc gaps:** Missing the skill-fork pattern (highly relevant to "skill router / dynamic dispatch" shape — subagent + preloaded skill is a built-in solution to context-protection); missing agent teams (multiple agents communicating, distinct from subagent dispatch).

### 9. Claude Agent SDK (Python / TypeScript)

- **Doc claim:** Python + TypeScript SDK; alignment work must be replicated.
- **Status:** current — confirmed both languages.
- **Canonical URL:** [code.claude.com/docs/en/agent-sdk/overview](https://code.claude.com/docs/en/agent-sdk/overview)
- **Updates since cutoff:**
  - **SDK shares Claude Code's filesystem config by default** — loads `.claude/skills/`, `.claude/commands/`, `CLAUDE.md`, and plugins from the working directory. The doc's claim that "SDK agents don't share hooks/settings/skills" is **outdated**; alignment work largely transfers. Use `setting_sources` / `settingSources` to restrict.
  - TypeScript SDK bundles a native Claude Code binary; no separate install needed.
  - Multi-cloud auth: Bedrock, Claude Platform on AWS, Vertex AI, Azure AI Foundry.
  - **Quota change (effective 2026-06-15):** Agent SDK and `claude -p` usage on subscription plans draws from a new monthly Agent SDK credit, separate from interactive usage. Relevant to the "API-cost-thinking when on subscription quota" footgun — the subscription-quota path now covers SDK too, with a separate bucket.
  - Subagents, hooks (including MCP/HTTP/prompt/agent hook types), session resume/fork, AskUserQuestion tool all available.
- **Doc gaps:** The doc's tradeoff "alignment work must be replicated" is partially wrong post-2026 changes — needs correction.

### 10. Managed Agents (Anthropic-hosted)

- **Doc claim:** Anthropic-hosted agents, org-level governance, "rolling out."
- **Status:** changed — public beta launched 2026-04-09.
- **Canonical URL:** [platform.claude.com/docs/en/managed-agents/overview](https://platform.claude.com/docs/en/managed-agents/overview)
- **Updates since cutoff:**
  - Launched 2026-04-09 in public beta — available to all builders on the Claude Platform, no invitation. Confirmed by [Anthropic news](https://www.anthropic.com/news/) coverage and [SiliconAngle](https://siliconangle.com/2026/04/08/anthropic-launches-claude-managed-agents-speed-up-ai-agent-development/).
  - **REST API**, not Claude.ai-only as the doc implies. Anthropic runs runtime + sandbox per session; your app sends events and receives streams.
  - Composable APIs (primitives that can be combined), isolated containers per session, native state and permission management.
  - Early adopters: Notion, Asana, Sentry.
  - Subsequent expansion (May 2026): "ability to dream," outcome-focused agents, multi-agent orchestration.
  - **Common pattern** Anthropic documents: prototype with Agent SDK locally, move to Managed Agents for production.
- **Doc gaps:** Description is materially wrong — Managed Agents is a REST API for developers, not a Claude.ai-employee-facing product. Should be repositioned alongside Agent SDK as the deployment-target choice, not as an org governance shape.

### 11. Skills and skill descriptions / matcher behavior

- **Doc claim:** (catalog #11, plus footgun "empty-description skills") — matcher under-triggers on advisory skills; description authoring matters.
- **Status:** current, with mechanics now well-documented.
- **Canonical URL:** [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
- **Updates since cutoff:**
  - Skill descriptions are loaded into context per session up to a **character budget** = 1% of context window (`skillListingBudgetFraction`, default `0.01`); per-skill cap is **1,536 chars** combined `description` + `when_to_use` (`maxSkillDescriptionChars`). When budget overflows, least-invoked skills lose descriptions first.
  - `/doctor` shows whether the budget is overflowing — confirms the matcher problem is now diagnosable.
  - **Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard** (cross-tool portable); Claude Code extends with invocation control, subagent execution, dynamic context injection.
  - New frontmatter: `when_to_use`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context: fork`, `agent`, `hooks`, `paths`, `shell`, `argument-hint`, `arguments`.
  - **`skillOverrides`** in settings (on / name-only / user-invocable-only / off) — visibility control without editing SKILL.md (key for third-party / plugin skills).
  - **`!command`** dynamic context injection at skill load (preprocessing, not Claude-executed). Disable via `disableSkillShellExecution` for managed lockdown.
  - **Skill content lifecycle**: invoked skills persist through the session; auto-compact carries forward most-recent invocations within a 25KB combined budget.
  - Path-scoped skill activation via `paths` frontmatter — direct analog to `.claude/rules/` path-scoping.
- **Doc gaps:** Doc's "empty-description skills" footgun is correct but missing the diagnostic side (`/doctor`, the budget math) and the workaround (`skillOverrides` to free budget); missing the Agent Skills open-standard angle (relevant to portability discussions).

## New shapes or features the doc misses

These didn't fit cleanly into the existing 15-shape catalog but matter:

- **Auto memory** ([memory#auto-memory](https://code.claude.com/docs/en/memory#auto-memory)) — Claude writes its own session notes; lives at `~/.claude/projects/<project>/memory/`. Distinct shape from CLAUDE.md (you-authored) and skills (you-or-Claude-invoked).
- **Plugin dependencies** ([plugin-dependencies](https://code.claude.com/docs/en/plugin-dependencies)) — first-class semver-constrained plugin deps. Directly mitigates "Mega-plugin" footgun.
- **Channels** ([channels](https://code.claude.com/docs/en/channels)) — MCP-server-pushed events into a session (Telegram/Discord/CI). Different shape from request-response MCP; relevant to "agent reacts to external events."
- **Background agent view and agent teams** ([agent-view](https://code.claude.com/docs/en/agent-view), [agent-teams](https://code.claude.com/docs/en/agent-teams)) — multi-session parallelism with central monitoring; agent-to-agent communication. Distinct from subagent dispatch.
- **LSP plugins** — Language Server Protocol servers bundled in plugins for real-time code intelligence. New plugin component type.
- **Background monitors** — `monitors/monitors.json` in plugins; `tail -F` style streams that emit notifications into the session.
- **`.claude/rules/` directory** with path-frontmatter — the de facto solution to "rule-skill confusion (everything always-on)" footgun. Should be promoted to a catalog entry or merged with shape #7.
- **Worktree/background isolation** (`worktree.bgIsolation`, EnterWorktree/ExitWorktree tools) — concurrency primitive for parallel agents on the same repo.
- **Permission-decision hooks via `prompt` and `agent` hook types** — small/fast model or agent decides whether to allow a tool call. New shape between "static permission rules" and "human approval."
- **Open-standard skills** (agentskills.io) — Claude Code skills are now portable across tools; relevant when comparing to OpenAI/Codex CLI ecosystems.

## Summary

The doc's overall taxonomy holds, but **every shape needs updates** and several need outright corrections. The biggest deltas since 2026-01: documentation domain moved to `code.claude.com`; commands merged into skills; Managed Agents launched as a REST-API product (not a Claude.ai feature); Agent SDK now shares Claude Code's filesystem config by default; plugins gained dependencies, LSP, monitors, and bin/; hooks expanded to 31 events with non-command handler types; `.claude/rules/` and auto-memory introduce two whole new memory/rule shapes that the doc's "always-on rules" shape doesn't cover.

Sources:
- [Claude Code docs (settings)](https://code.claude.com/docs/en/settings)
- [Claude Code docs (plugins)](https://code.claude.com/docs/en/plugins)
- [Claude Code docs (plugin marketplaces)](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code docs (hooks)](https://code.claude.com/docs/en/hooks)
- [Claude Code docs (MCP)](https://code.claude.com/docs/en/mcp)
- [Claude Code docs (memory)](https://code.claude.com/docs/en/memory)
- [Claude Code docs (skills)](https://code.claude.com/docs/en/skills)
- [Claude Code docs (sub-agents)](https://code.claude.com/docs/en/sub-agents)
- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- [Anthropic Managed Agents launch coverage (SiliconAngle, 2026-04-08)](https://siliconangle.com/2026/04/08/anthropic-launches-claude-managed-agents-speed-up-ai-agent-development/)
- [Claude Code changelog](https://code.claude.com/docs/en/changelog)
- [Claude Code release notes](https://docs.anthropic.com/en/release-notes/claude-code)
