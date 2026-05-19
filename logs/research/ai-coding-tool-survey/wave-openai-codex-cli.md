---
log-role: research-wave
status: draft v1 — sampled 2026-05-18 against Codex CLI v0.131.0 + developers.openai.com/codex
scope: OpenAI Codex CLI (the agentic coding tool launched 2025-04, not the 2021 Codex model)
---

# Wave: OpenAI Codex CLI survey

Codex CLI (`github.com/openai/codex`, Apache 2.0, Rust, ~83.5k stars, created 2025-04-13) is OpenAI's local agentic coding tool. Latest stable: `rust-v0.131.0` (2026-05-18). One coding agent across CLI / IDE extension / desktop app / web-cloud / ChatGPT, with shared config and shared plugin ecosystem.

## Capability matrix

| Dimension | Codex CLI | Claude Code | Notes |
|---|---|---|---|
| Plugin marketplace | **yes** — launched 2026-03-27; `.agents/plugins/marketplace.json` registry; GitHub-shorthand / Git URL / SSH / local install via `codex plugin marketplace add` | yes — `.claude-plugin/marketplace.json`, `/plugin marketplace add` | **Similar** shape and timeline; cross-tool projects exist that ship both `.claude-plugin/` and `.codex-plugin/` from one repo |
| Skill format | **yes** — `SKILL.md` with name+description frontmatter; discovered from `.agents/skills/` (repo, walked from cwd up to git root), `$HOME/.agents/skills/` (user), `/etc/codex/skills/` (admin), built-in | yes — `SKILL.md` with name+description; `~/.claude/skills/`, `.claude/skills/`, plugin-bundled | **Same** SKILL.md frontmatter shape; **divergent path** — Codex uses cross-tool `.agents/skills/` per the AGENTS.md ecosystem; Claude Code uses `.claude/skills/` |
| Hooks | **yes** — 6 events: `SessionStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `Stop`. JSON-or-TOML, `matcher` regex, exit-code + JSON result semantics largely copied from Claude Code (env aliases `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` are explicit compatibility shims) | yes — `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `PreCompact`, `Stop`, `Notification`, `SubagentStop` | **Similar** with deliberate compat. Codex adds `PermissionRequest` as distinct event; lacks `PreCompact`/`Notification`/`SubagentStop` as named events |
| Subagents | **yes** — TOML files in `~/.codex/agents/` (user) or `.codex/agents/` (project); fields `name` / `description` / `developer_instructions` (+ optional `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`). Built-ins: `default`, `worker`, `explorer` | yes — markdown files in `.claude/agents/` with frontmatter; built-ins include `Explore`, `Plan`, `general-purpose` | **Similar** — both have user+project scope and built-in specializations. Codex uses TOML; Claude Code uses markdown+frontmatter. Codex has `agents.max_threads` (default 6) and `agents.max_depth` (default 1) caps |
| Tool format (MCP) | **yes** — first-class MCP via `[mcp_servers.<id>]`; tools are MCP-shaped; plugins can bundle MCP servers; OpenAI Agents SDK reusable inside Codex per `developers.openai.com/codex/guides/agents-sdk` | yes — `.claude/mcp.json`, plugin-bundled MCP servers | **Same** transport (MCP); both treat MCP as the canonical extension point for capabilities |
| Config layering | user `~/.codex/config.toml` → project `.codex/config.toml` (requires trust) → admin/managed → `requirements.toml` (enterprise floor with `guardian_policy_config`). Closest-file-wins for shared keys | enterprise managed-settings.json → CLI args → project local → project shared → user | **Similar** hierarchy; Codex uses TOML where Claude Code uses JSON. Codex adds an explicit *trust-on-load* gate for project configs |
| Managed / enterprise | **yes** — `requirements.toml` with `allow_managed_hooks_only = true`, `[features]` enforcement, `managed_dir` for hook scripts, `guardian_policy_config`, `forced_login_method`, `forced_chatgpt_workspace_id`, JSON plugin allow/block policy | yes — `/etc/claude-code/managed-settings.json` (Linux) / equivalent on mac/Win, locked fields | **Divergent shape, same intent**. Codex's `requirements.toml` is a richer enterprise floor (managed hooks, plugin policy, login method enforcement) than Claude Code's managed-settings.json |
| `AGENTS.md` convention | **yes** — primary memory file. Discovery: `~/.codex/AGENTS.md` (or `$CODEX_HOME`), then concatenated from git root down to cwd, blank-line-joined, `project_doc_max_bytes` (default 32 KiB). `AGENTS.override.md` checked first per directory | uses `CLAUDE.md` (analogous, similar concat-from-root behavior). Claude Code does *not* read `AGENTS.md` by default | **Divergent filename**. Codex sits on the cross-tool `AGENTS.md` open standard (60k+ projects, adopters: Cursor, Aider, goose, opencode, Zed, Devin, Copilot Coding Agent, Gemini/Jules, Windsurf, etc.). Claude Code is conspicuously absent from the published AGENTS.md adopter list |
| Slash commands | **yes** — ships ~40 built-ins (`/model`, `/permissions`, `/mcp`, `/plugins`, `/hooks`, `/compact`, `/clear`, `/theme`, `/statusline`, `/keymap`, …). Custom slash commands are not first-class in the CLI itself — plugins extend behavior via skills + `@`-mentions rather than user-authored `/commands/` files | yes — built-in slash commands plus user-authored `.claude/commands/*.md` and plugin-bundled commands | **Divergent**. Claude Code treats user-authored slash commands as first-class; Codex pushes that role onto skills + plugin-bundled workflows |
| Sandbox / safety | **yes** — OS-level: macOS Seatbelt, Linux `bwrap`+`seccomp`, WSL2/native on Windows. Modes: `read-only` / `workspace-write` / `danger-full-access`. Approval policies: `on-request` / `never` / `untrusted` / `auto_review`. Network off by default; domain allowlist (`*.example.com` matches subs but not bare). Local bind blocked by default | yes — permission allow/deny lists, hook-driven gates, no built-in OS sandbox of the same kind | **Divergent — Codex stronger here**. OS-level enforced sandbox is a real differentiator vs. Claude Code's policy-only model |
| Hosted vs local | **unified shape**. Codex = one agent across CLI, IDE extension, desktop app, web/cloud, ChatGPT. Shared config via `~/.codex/config.toml`; cloud sandbox = OpenAI-managed container with two-phase network (setup-with-net, then offline). Plugins work across all surfaces | Claude Code (local CLI/IDE) + Claude.ai (chat) + Claude Agent SDK (programmatic). Less unified — Agent SDK doesn't share hooks/skills/settings with Claude Code | **Divergent posture**. Codex sells "one agent everywhere" with a shared customization stack; Claude's surfaces are more siloed in alignment substrate |
| Open-source license | **Apache 2.0**. Public repo, public roadmap, ~12k forks | Claude Code is **closed-source** binary; plugins/marketplaces are user-authored OSS | **Divergent**. Codex's OSS posture enables third-party forks (e.g., `duyet/codex-claude-plugins`), public issue tracker for hook proposals (#14882, #15250, #19385), and DeepWiki-style indexes |

## Notable shapes Codex uses that Claude Code does not

- **`requirements.toml` as a dedicated enterprise floor** — distinct from the regular `config.toml`. Holds managed hooks, plugin policy, `allow_managed_hooks_only`, forced login. Claude Code overloads `managed-settings.json` for the same role.
- **`AGENTS.md` cross-tool standard adoption** — Codex reads the same file as Cursor, Aider, goose, Gemini CLI, Copilot Coding Agent, etc. (`https://agents.md/`). Claude Code stays on `CLAUDE.md`.
- **`.agents/skills/` and `.agents/plugins/marketplace.json` cross-tool paths** — explicit "portable skill/marketplace location" convention shared with Gemini CLI. Claude Code uses `.claude/`-prefixed paths.
- **OS-enforced sandboxing** (Seatbelt / bwrap+seccomp / WSL2) baked into the CLI itself, not policy-only.
- **`PermissionRequest` as a distinct hook event** — separate from `PreToolUse`, allowing approval-time policy without intercepting every tool call.
- **`AGENTS.override.md`** — per-directory override file checked before `AGENTS.md`, gives a clean "local-only" memory layer.
- **Cloud-and-local unified product family** — Codex Cloud is the same agent as Codex CLI, same plugins, same skills, same `config.toml`.
- **Apache-2.0 source** — fork-and-modify is a viable adoption path; not so for Claude Code itself.
- **Project-config trust gate** — loading `.codex/config.toml` requires explicit user trust on first encounter (mitigates supply-chain attacks via cloned repos).
- **Built-in subagent caps** — `agents.max_threads = 6` / `agents.max_depth = 1` as defaults; explicit guardrails on subagent fan-out.
- **Compatibility aliases** — `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` env vars exposed to Codex plugin hooks, signaling deliberate convergence with Claude Code's plugin contract.

## Notable shapes Claude Code has that Codex does not

- **User-authored slash commands as first-class units** (`.claude/commands/*.md`). Codex pushes this work onto skills + plugin workflows.
- **`PreCompact` / `Notification` / `SubagentStop` hook events** — Codex's hook taxonomy is narrower.
- **Dedicated Claude Agent SDK for programmatic use** — Codex's analog is the OpenAI Agents SDK, less integrated with the local-CLI customization stack.
- **Plugin and skill format is markdown-native** — Codex agents use TOML and Codex plugins use JSON; Claude Code keeps everything in markdown+YAML-frontmatter, more uniform with the docs they live next to.
- **MCP server registry** (`claude mcp` commands with project/user scopes) — Codex configures MCP only via `config.toml`.

## Canonical URLs

- Repo: `https://github.com/openai/codex` (Apache 2.0, Rust)
- Top-level memory file: `https://github.com/openai/codex/blob/main/AGENTS.md`
- AGENTS.md guide: `https://developers.openai.com/codex/guides/agents-md`
- Skills: `https://developers.openai.com/codex/skills`
- Subagents: `https://developers.openai.com/codex/subagents`
- Hooks: `https://developers.openai.com/codex/hooks`
- Plugins: `https://developers.openai.com/codex/plugins`
- Plugin authoring: `https://developers.openai.com/codex/plugins/build`
- Config (basic): `https://developers.openai.com/codex/config-basic`
- Config (advanced): `https://developers.openai.com/codex/config-advanced`
- Config reference: `https://developers.openai.com/codex/config-reference`
- Slash commands: `https://developers.openai.com/codex/cli/slash-commands`
- CLI overview: `https://developers.openai.com/codex/cli`
- Security / approvals: `https://developers.openai.com/codex/agent-approvals-security`
- Agents SDK reuse: `https://developers.openai.com/codex/guides/agents-sdk`
- Changelog: `https://developers.openai.com/codex/changelog`
- Cross-tool AGENTS.md standard: `https://agents.md/`
- Cross-tool plugin example: `https://github.com/duyet/codex-claude-plugins`
- Cross-tool skill marketplace example: `https://github.com/netresearch/claude-code-marketplace` (Claude + Cursor + Copilot + Codex + Gemini)
- Third-party reference: `https://codex.danielvaughan.com/2026/04/12/codex-cli-customisation-stack-unified-system/`

## Summary

Codex CLI ships nearly every alignment shape Claude Code does — plugin marketplace, hooks (with deliberate Claude-style env aliases), subagents, skills with `SKILL.md`+frontmatter, layered config, enterprise managed floor, MCP — but lands them on a **cross-tool open standard** (`AGENTS.md`, `.agents/skills/`, `.agents/plugins/marketplace.json`) and adds OS-enforced sandboxing plus a unified local↔cloud product family. The two products are converging on the same shapes from opposite cultural starts: Claude Code as a polished proprietary tool growing extensibility outward; Codex as an open-source Rust CLI growing toward enterprise control with `requirements.toml` and managed hooks. For the alignment-at-scale research, the load-bearing finding is that **Codex's adoption of `AGENTS.md` + `.agents/` puts it on a portable substrate shared with Cursor, Aider, Gemini CLI, and many more — making "the alignment substrate" a multi-vendor concern, not a Claude-Code-specific one.**
