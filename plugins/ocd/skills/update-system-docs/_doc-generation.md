# Doc Generation

Generate canonical docs (README.md, architecture.md, CLAUDE.md/SKILL.md) for a system. User decision: canonical docs are regenerated in full from the fact bundle, then content worth preserving from the prior version is ported over. Regeneration produces more cohesive prose than incremental patching; surgical edits remain the mechanism for non-obvious surfaces where single-entity regeneration has no coherence benefit.

### Variables

- {fact-bundle} — structured facts from the system
- {system-name} — system name from fact bundle
- {prior-doc-content} — current content of the doc being regenerated (empty string for fresh creation)
- {port-over-candidates} — list of unverifiable-prose spans from prior doc to splice into regenerated output

## Regeneration with Port-Over Flow

For each canonical doc being regenerated:

```
1. If {prior-doc-content} is non-empty:
    1. Extract claims from prior doc — Call: `_claim-extraction.md`
    2. Filter to unverifiable-prose claims → {port-over-candidates}
    3. Pass {port-over-candidates} to generation prompt as spliceable content
2. Else:
    1. {port-over-candidates} = []
3. Invoke generation prompt with {fact-bundle} + {port-over-candidates}
4. Post-generation validation (below)
5. Write final doc via Write tool
```

Surgical edits are NOT used for canonical docs. The regenerate-and-port-over pattern is the approach.

## README Prompt

Invoked via `Call: _doc-generation.md#readme`:

```
<role>
You draft README.md for a system, from a deterministic fact bundle extracted
from its source code, plus any prose worth preserving from the prior version.
Every concrete fact traces to the fact bundle; preserved prose is spliced in
verbatim from its original location.
</role>

<fact_bundle>
{fact-bundle}
</fact_bundle>

<port_over_candidates>
{port-over-candidates}
</port_over_candidates>

<required_structure>
# {system-name}

<purpose statement — ONE paragraph. Conveys SCOPE and ROLE per Purpose Statement
guidance. Excludes implementation details, section listing, history. This
statement is SSoT with the architecture.md H1 paragraph — use identical wording
if architecture.md exists or will be generated.>

<If the fact bundle has installation, usage, or configuration facts, include
corresponding sections below. For internal-only systems with none of these,
emit nothing beyond the purpose statement — a minimal README is correct.>

## Installation

<installation steps derived ONLY from fact bundle fields: package_manifest
(pyproject.toml, requirements.txt, package.json), system_dependencies. Omit
the entire section if the bundle has no such facts.>

## Usage

<usage derived ONLY from fact bundle CLI commands (argparse/click), exposed
API entry points, or MCP tool registry. Give literal invocations. Omit section
if no user-facing entry points exist.>

## Configuration

<only if fact bundle contains configuration fields — env vars, config file
schemas, settings. Otherwise omit.>
</required_structure>

<hard_rules>
1. Every concrete statement (file path, command, symbol, version) comes from the fact bundle. If not there, do not write it.
2. Forbidden: "Why X?" sections, marketing prose, emoji feature bullets, "modern", "fast", "robust", "scalable", "elegant", "seamless", "production-ready".
3. Forbidden: imagined use cases.
4. Internal-only systems (no manifest facts, no user-facing entry points, no configuration) produce a README that is JUST the H1 and the purpose statement. This is correct; do not pad.
5. Code blocks use exact commands from the fact bundle. Do not invent flags.
6. Paragraph wrapping: each paragraph is a single source line.
7. Blank line between every heading, paragraph, list, and code block.
8. Port-over candidates from <port_over_candidates> splice into the matching section if one exists in your output; otherwise append to a "Notes" section at the end. Preserve their wording verbatim.
</hard_rules>

<output_format>
Emit the README.md content only. Begin with the H1.
</output_format>
```

## architecture.md Prompt

Invoked via `Call: _doc-generation.md#architecture`. Includes the Contents table.

```
<role>
You draft architecture.md for a system, from a fact bundle. Architecture
docs describe structure OBSERVABLE in code — modules, components, imports,
patterns that appear. Never speculate about intent.
</role>

<fact_bundle>
{fact-bundle}
</fact_bundle>

<port_over_candidates>
{port-over-candidates}
</port_over_candidates>

<required_structure>
# {system-name} Architecture

<one-paragraph purpose statement — SSoT with README's purpose statement; use
identical wording. Conveys SCOPE and ROLE from the internal/structural
perspective this doc serves.>

## Contents

| Section | Purpose |
|---------|---------|
| Components | <first paragraph of ## Components section, copied verbatim> |
| Relationships | <first paragraph of ## Relationships section, if that section exists> |
| Patterns | <first paragraph of ## Patterns section, if that section exists> |

<Build this table AFTER drafting the sections below. Each row is the section
heading + the section's first paragraph copied verbatim. If a section is
omitted from this doc, omit its row.>

## Components

<one subsection per top-level module or package in fact bundle's file inventory.
Each subsection starts with a one-paragraph purpose statement per Purpose
Statement guidance, applied at the module scale. Then a bullet list of public
symbols from the fact bundle.>

### {module_name}

<module purpose statement — single paragraph conveying scope + role at module
scale. Sourced from module docstring if present; else derived from primary
symbols. If neither yields a clear statement, write the literal: "Purpose not
documented in source." — this flags as unresolved to user.>

- {public-symbol-1} — {brief description from fact bundle}
- {public-symbol-2} — ...

## Relationships

<derived ONLY from imports graph. Format each relationship as:
  - {module_a} → {module_b}: {imported symbols}
Omit section if imports graph is empty or all intra-module.>

## Patterns

<only if fact bundle has pattern_signals confirming a pattern. Examples:
"pipeline" with ast.NodeVisitor chain; "facade + underscore internals" for
Python package structure. Omit section otherwise.>
</required_structure>

<hard_rules>
1. Components section is exhaustive over the fact bundle — one subsection per module, no omissions, no additions.
2. Do not describe behavior the fact bundle did not capture.
3. No design rationale. The "why" belongs in commit messages.
4. Forbidden vocabulary: "elegant", "clean separation", "robust", "well-designed", "scalable".
5. Relationships comes from imports only.
6. Contents table is built last, as an index of the sections you actually emitted. Each row copies the first paragraph of that section verbatim.
7. Port-over candidates splice into matching sections; otherwise append to "Notes".
8. Purpose statement at the H1 is SSoT with README's — identical wording.
</hard_rules>

<output_format>
Emit the architecture.md content only.
</output_format>
```

## CLAUDE.md Prompt

Invoked via `Call: _doc-generation.md#claude-md`:

```
<role>
You draft CLAUDE.md for a system with agent-facing procedures. CLAUDE.md
contains operational procedures, workflow rules, and tool invocation patterns
for agents. Excludes architectural internals (architecture.md) and
user-facing content (README.md).
</role>

<fact_bundle>
{fact-bundle}
</fact_bundle>

<agent_procedures>
{agent-procedure-signals}
</agent_procedures>

<port_over_candidates>
{port-over-candidates}
</port_over_candidates>

<required_structure>
# {system-name} Instructions

<purpose statement — what operational guidance this file provides.>

<procedure sections derived from agent_procedures signals: skills, slash commands,
workflow hooks, agent-invocable CLI subcommands. Each procedure is a numbered
step list or a named trigger → action pair. Use Process Flow Notation where
steps form a workflow.>
</required_structure>

<hard_rules>
1. Only procedures whose trigger/action pair is observable in code are included.
2. No rationale content.
3. No architectural description — refer reader to architecture.md if structural context is needed.
4. No user-facing installation/usage — lives in README.md.
5. If agent_procedures is empty: emit the single line "SKIP" and the skill will suppress creation.
6. Port-over candidates splice in where applicable; else append to "Notes".
</hard_rules>

<output_format>
Emit the CLAUDE.md content only, or "SKIP".
</output_format>
```

## Post-Generation Validation

```
1. Parse generated content as markdown
2. Assert H1 matches {system-name}
3. Assert no forbidden vocabulary appears
4. Assert code blocks contain only tokens from fact bundle
5. Assert paragraphs are single-line-in-source
6. For architecture.md: validate Contents table row count equals ## section count (minus Contents itself)
7. For architecture.md: validate each Contents row's Purpose column matches the corresponding section's first paragraph
8. If any validation fails: retry once; if still fails, abandon generation and record as unresolved
```

## Contents Table Regeneration

After the architecture.md body is generated, the Contents table is built from a deterministic scan:

```
1. Parse generated architecture.md
2. For each ##-level section (excluding ## Contents itself):
    1. Extract heading text
    2. Extract first paragraph immediately after heading
    3. Append row to Contents table: | {heading} | {first-paragraph} |
3. Insert table into the ## Contents section
```

The LLM generates the body; the script assembles the Contents table. Deterministic and idempotent.

## Port-Over Splicing

For each `{port-over-candidate}`:

```
1. If the regenerated doc has a section whose heading matches the candidate's original section:
    1. Splice candidate text into that section at the end of the section body
2. Else:
    1. Accumulate into a "Notes" section appended at the end of the doc
3. Preserve wording verbatim; do not edit preserved prose
```
