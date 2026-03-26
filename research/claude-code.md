# Claude Code

Official documentation for Claude Code plugin development, skills, hooks, and agent infrastructure.

## Plugin System

- https://code.claude.com/docs/en/discover-plugins.md — Plugin discovery, marketplace integration, installation workflow
- https://code.claude.com/docs/en/plugin-marketplaces.md — Marketplace creation and distribution; schema, plugin entries, hosting, version resolution
- https://code.claude.com/docs/en/plugins-reference.md — Plugin technical reference; plugin.json schema, manifest fields, directory structure, versioning, debugging
- https://code.claude.com/docs/en/plugins.md — Plugin overview, structure, lifecycle; when to use plugins vs standalone configuration

## Skills

- https://code.claude.com/docs/en/skills.md — Skill creation and configuration; SKILL.md format, frontmatter fields and reference, string substitutions, arguments, advanced patterns

## Hooks

- https://code.claude.com/docs/en/hooks-guide.md — Hook configuration and automation; setup, hook events, matchers, input/output handling, async hooks
- https://code.claude.com/docs/en/hooks.md — Hook technical reference; all hook event types with detailed input/output specs (SessionStart, PreToolUse, PostToolUse, SubagentStop, FileChanged, etc.)

## Settings and Permissions

- https://code.claude.com/docs/en/permissions.md — Permission system; tool-specific permissions, Bash/Read/Edit/WebFetch/MCP/Agent specifiers, permission modes
- https://code.claude.com/docs/en/settings.md — Settings file structure; settings.json schema, permission settings, sandbox settings, environment variables, precedence

## Project Instructions

- https://code.claude.com/docs/en/memory.md — CLAUDE.md and auto memory; structure, loading behavior, rules organization in `.claude/rules/`, memory management

## Agents

- https://code.claude.com/docs/en/agent-teams.md — Agent team orchestration; team setup, control, architecture, permissions, multi-agent coordination
- https://code.claude.com/docs/en/sub-agents.md — Subagent configuration; creating agents, frontmatter fields, MCP server scoping, conditional rules

## MCP

- https://code.claude.com/docs/en/mcp.md — Model Context Protocol servers; installing, plugin-provided MCP servers, tool search, resources, authentication

## Architecture

- https://code.claude.com/docs/en/cli-reference.md — CLI command reference; commands plugins may trigger or configure
- https://code.claude.com/docs/en/how-claude-code-works.md — Execution model and architecture; how plugins integrate with agentic loop

## Plugin Components

- https://code.claude.com/docs/en/channels-reference.md — Channel support for plugins; webhook receivers, notification format, permission relay
- https://code.claude.com/docs/en/output-styles.md — Custom output styles as plugin components

