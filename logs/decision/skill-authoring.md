---
log-role: reference
---

# Skill Authoring

Decisions governing how skills are structured — shared content, multi-workflow organization, and agent-context isolation.

## Extract shared skill components to files

### Context

Skills with multiple workflows share content blocks (evaluation protocols, criteria catalogs, instruction sets). These blocks are passed to spawned agents as part of their instructions. Agents that receive content they do not need (coordinating agents seeing evaluation constraints, evaluation agents seeing triage criteria) can be confused by conflicting instructions or waste context on irrelevant material.

### Options Considered

**Inline `## Components` section in SKILL.md** — components defined as subsections, referenced by name in workflows. Orchestrator extracts and bundles referenced components when dispatching to agents. Disqualified: orchestrator pre-reads and inlines content, agents receive everything bundled in their prompt, coordinating agents see evaluation instructions they should not act on (caused a real conflict where recursion constraint told coordinating agent not to spawn subagents while its own instructions told it to).

**Extracted `_{name}.md` files alongside SKILL.md** — components as separate files in skill directory. Workflow steps include explicit `Read _file.md` instructions. Each agent reads only files it needs at execution time.

### Decision

Extract components to `_{name}.md` files. Underscore prefix signals internal (consistent with `_{purpose}.py` pattern for internal Python modules). Workflows include explicit read steps. Orchestrator does not pre-read component files — workflow steps dictate when files are read and by whom.

For multi-agent workflows: coordinating agents pass file read instructions to subagents without reading the files themselves. This prevents coordinating agents from being influenced by content meant for evaluation or execution agents.

### Consequences

- **Enables:** precisely scoped agent context; coordinating agents never see conflicting instructions; SKILL.md stays focused on routing and workflow structure; component files can grow without bloating SKILL.md (500-line convention limit applies to SKILL.md, not total)
- **Constrains:** more files per skill directory; workflows must include explicit read steps; component file paths are relative to skill directory
- **Trade-off:** single-workflow components can stay as workflow subsections per convention; extraction is for content shared across 2+ workflows or content that must be isolated from certain agents
