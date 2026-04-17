# update-system-docs Design Notes

Working design after research sprint (Waves 1-3) and user decisions. Ready for skeleton implementation; residual work items listed at end.

## Problem Statement

Project documentation drifts from code reality. Canonical documents (README, architecture, CLAUDE, SKILL) and non-obvious surfaces (CLI help, module docstrings, MCP tool descriptions, frontmatter descriptions, function docstrings) fall out of sync during refactors. The existing `evaluate-documentation` skill uses the evaluate-* pattern — surface observations for user triage. That pattern fits governance (intent decisions) but not documentation (consequence of reality). Per-finding user gates produce fatigue, not safety. This skill replaces evaluate-documentation with a reality-first maintainer.

## Core Premise

**Documentation is a consequence of reality.** The skill derives what docs should say from actual code, regenerates canonical docs from deterministic fact bundles, and applies surgical edits to non-obvious surfaces where regeneration would destroy author intent. Unverifiable prose is preserved via port-over from prior versions. Git diff is the review gate; unresolved questions bubble up to user at end of run.

## Research-Validated Approach

**Wave 1** (landscape): leaves-first DFS is empirically necessary (arXiv 2501.07857); driftcheck's conservative-edit discipline is closest prior art; Clover's regenerate-to-compare is the algorithm family; citation anchoring (Mutable.ai) is a future direction; the hierarchical conservative-edit maintainer is an empty niche.

**Wave 2** (mechanics): subagents cannot spawn subagents in Claude Code — recursive DFS infeasible; use multi-wave flat fan-out (orchestrator drives). Write-to-disk return-a-pointer for context budget. Python `ast` stdlib sufficient for fact extraction in v1 (no tree-sitter dependency). `${CLAUDE_PLUGIN_DATA}` for plugin state. Anthropic's official "overeagerness" prompt for conservative editing.

**Wave 3** (prompts): concrete templates for claim extraction (XML-structured with taxonomy), verification (4-verdict with evidence), surgical edit (quote-then-replace with validation), doc generation (grounded-only with forbidden vocabulary), unverifiable-prose classification (5 categories with regex markers).

## Architecture

Three layers, no recursion:

1. **Skill executor** (main conversation) — discovers systems, builds DAG, computes traversal waves, dispatches wave by wave, reads persisted summaries between waves, presents final report with bubbled-up unresolved questions.
2. **Per-system agent** (spawned per system per wave) — reads system's code scope, builds deterministic fact bundle, regenerates canonical docs from scratch, ports over unverifiable prose from prior versions, applies surgical edits to non-obvious surfaces, persists bubble-up summary to `${CLAUDE_PLUGIN_DATA}`, returns pointer plus status.
3. **Parent-wave agent** (later waves) — reads child summary pointers, incorporates child purposes + interfaces into parent canonical docs, handles its own system's fact bundle, forwards any unresolved questions it cannot answer.

Waves for this project:

- Wave 0 (leaves): auto_approval hook, plugin framework, each subsystem under `plugins/ocd/systems/*` — all in parallel
- Wave 1: ocd plugin (consumes wave-0 summaries)
- Wave 2: project root (consumes ocd summary)

## Canonical Doc Flow: Regeneration with Port-Over

User decision: full regeneration produces more cohesive docs than surgical patching. For each canonical doc (README, architecture, CLAUDE, SKILL):

```
1. Extract claims from existing doc (if present)
2. Classify each claim as verifiable or unverifiable-prose (per _unverifiable-prose.md)
3. Set aside unverifiable-prose claims as port-over candidates
4. Regenerate the doc fresh from fact bundle (per _doc-generation.md)
5. Review regenerated output for where port-over candidates fit:
    - Port over to matching section if one exists in regenerated output
    - Otherwise append to "Notes" section
6. Emit final doc
```

Surgical edits remain the mechanism for **non-obvious surfaces** (module docstrings, function docstrings, CLI help text, MCP tool descriptions, frontmatter descriptions) because regeneration of a single docstring can't "port over" meaningfully — the docstring is already small. Regeneration makes sense only when the output is substantial enough that prose coherence matters.

## Architecture.md Contents Table

New structural feature for every architecture.md: a `## Contents` section listing each `##`-level heading with its purpose statement copied from the section's first paragraph.

```markdown
## Contents

| Section | Purpose |
|---------|---------|
| Components | {first paragraph of ## Components} |
| Relationships | {first paragraph of ## Relationships} |
| Patterns | {first paragraph of ## Patterns} |
```

This is a derived projection — SSoT stays with each section's first paragraph. Our skill owns regeneration; if a section's purpose changes, the table updates next run. Serves as navigable index without violating Single Source of Truth.

If a section lacks a well-formed purpose statement (not a single paragraph conveying scope + role), the skill flags it as an unresolved question for user.

## Systems Include Skills

Skills are systems. They use SKILL.md as their agent-facing procedure doc (instead of CLAUDE.md). The split rules from `system-documentation.md` apply uniformly — a skill grows an architecture.md sibling only when its content starts containing architectural detail that shouldn't be in SKILL.md. No arbitrary complexity trigger.

Required docs per system kind:

| Kind | README.md | architecture.md | CLAUDE.md / SKILL.md |
|------|-----------|-----------------|----------------------|
| project-root | required | required | CLAUDE.md if agent procedures |
| plugin | required | required | CLAUDE.md if agent procedures |
| mcp-server | required | required | n/a |
| library | required | required | n/a |
| framework | required | required | n/a |
| hook-system | required | required | n/a |
| skill | required | required when SKILL.md would otherwise violate Document Separation | SKILL.md (always) |

README is always required; for internal-only systems it is minimal — a purpose statement and nothing else. Architecture.md (with Contents table) carries the detail; the README's purpose statement and architecture.md's H1 paragraph are SSoT projections of the same fact.

## Fact Bundle with Hash Caching

Per-system agent builds a fact bundle. For v1, Python-only via `ast` stdlib:

- File inventory (navigator `paths_list`)
- Per `.py` file: module docstring, public and private function signatures + docstrings, class definitions + method signatures + docstrings, imports
- Manifests (plugin.json, pyproject.toml, requirements.txt)
- MCP tool definitions (`@mcp.tool` decorator walks)
- CLI commands (argparse / click walks in `__main__.py`)
- Frontmatter from governed markdown files
- Pattern signals (dataclasses, ast.NodeVisitor subclasses, FastMCP usage, etc.)
- Child summaries (via `{child-pointers}` read)

**Hash caching** (navigator integration): each file's fact bundle contribution is keyed by file content hash. Navigator tracks a `doc_verified_at` marker (hash + timestamp) per file. On re-run:

- If file hash matches stored `doc_verified_at` AND no downstream child summary has changed: skip fact-extraction and doc-verification for that file
- If file hash differs OR a child summary changed: re-process

This is a navigator schema extension — separate sub-task from the core skill. Acceptable v1 fallback: process all files without caching; hash integration lands in v1.1.

## Function Docstrings In Scope

Every public function, method, and class gets a docstring the skill verifies against its signature and body. Missing docstrings are populated for agent-facing needs. Heavy token cost at first run mitigated by hash caching on re-runs.

Docstring flow uses surgical edits (not regeneration) — single-docstring regeneration has no coherence benefit.

## Unresolved Questions Bubble Up

Every per-system agent accumulates an `unresolved` list:

- Claims the agent couldn't verify or refute (no-evidence verdicts)
- Cross-system references the agent couldn't resolve from its scope
- Sections with missing or malformed purpose statements
- Ambiguous surgical edits the retry loop couldn't uniquify

Parent agents inspect child `unresolved` entries and resolve any they have scope for (e.g., a child's cross-system reference to a sibling resolves at their common parent). Residual unresolved entries propagate up. The project-root agent's final `unresolved` list lands in the skill's Report for user judgment.

## Component Files

- `SKILL.md` — entry point
- `_per-system-workflow.md` — what each per-system agent does
- `_provability.md` / `_verification.md` — verifiability classification + verification
- `_summary-schema.md` — bubble-up summary shape; includes unresolved-questions field
- `_system-discovery.md` — heuristics for system boundaries; skills included; `__main__.py` handling
- `_surfaces.md` — non-obvious surface catalog; function docstrings + section purposes added
- `_claim-extraction.md` — prompt template for extracting claims
- `_conservative-edit.md` — prompt template for surgical edits
- `_doc-generation.md` — prompt templates for README/architecture/CLAUDE generation; includes Contents table logic; regeneration-with-port-over flow
- `_unverifiable-prose.md` — classifier with 5 categories

## Route / Workflow Sketch

See `SKILL.md` for PFN-formatted workflow. Shape:

- Route: validate target, discover systems via CLI, build DAG, compute waves, present plan, create scratch dir, dispatch
- Workflow: wave loop with async per-system agents; each writes summary pointer; orchestrator waits for wave, advances, repeats; final Report aggregates summaries + unresolved questions

## Idempotence Strategy

- **Structural match deterministic** — same fact bundle + same doc produces same verdict
- **Edit tool fails loudly on re-apply** — surgical edits on stable reality no-op naturally
- **Canonical docs regenerated from fact bundle** — second run on stable reality produces same content (given prompt determinism)
- **Hash markers** — re-runs skip unchanged file+scope
- **Scratch dir wiped on success, preserved on failure** — resumability for interrupted runs

## Residual Work Items

1. Implement discovery CLI (`plugins/ocd/systems/update-system-docs/__main__.py` + `_discovery.py`) — deterministic Python; not agent work.
2. Implement fact-bundle builder as a Python module (ast-based) — called by per-system agents via bash.
3. Navigator schema extension for `doc_verified_at` hash markers — separate navigator-side change; v1 can ship without it, pay the token cost per run.
4. Section purpose extraction utility — part of fact-bundle builder; needed for Contents table regeneration.
5. cli.py → __main__.py cleanup across existing code — completed.

## Open Decisions Remaining

None from user at this point. Design is consolidated; implementation is the next phase.

## Scale Estimate

- Systems (project root + plugin + 4 systems + ~9 skills): ~15 systems
- Docs to create or regenerate: ~30 canonical docs
- Non-obvious surfaces to check: ~100+ (every `.py` module docstring, ~200+ function docstrings, CLI help, MCP tools, frontmatter)
- First-run token estimate: 300-500k tokens (creation-heavy)
- Re-run with hash caching: 50-100k tokens (mostly verification)
