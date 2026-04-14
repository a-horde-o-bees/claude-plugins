# Per-System Agent Workflow

Workflow for one per-system agent spawned by the skill executor. Processes a single system in isolation: builds a deterministic fact bundle, regenerates canonical docs with port-over of unverifiable prose, applies surgical edits to non-obvious surfaces, writes a bubble-up summary to disk, returns a pointer plus unresolved questions.

### Variables

- {system} — path of the system root (relative to project root)
- {child-pointers} — list of paths to child systems' persisted summary files (empty for leaves)
- {run-id} — identifier for the current skill run; scopes scratch files under `${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}/`

## Process

### Setup

1. Build fact bundle — bash: `${CLAUDE_PLUGIN_ROOT}/run.py update_system_docs.cli fact-bundle --system {system} --child-pointers "{child-pointers}" --json`
    - File inventory from navigator
    - Per .py file: module docstring, public + private symbols with signatures + docstrings, imports
    - Manifests (plugin.json, pyproject.toml, requirements.txt)
    - MCP tool definitions from `@mcp.tool` decorator walks
    - CLI commands from `__main__.py` argparse/click walks; graceful fallback to cli.py
    - Frontmatter from governed markdown files
    - Pattern signals
    - Child summaries merged into bundle
2. {fact-bundle} = JSON result

### Hash-Cache Short Circuit

> Skip files whose fact contribution hasn't changed since last verification AND whose descendant summaries haven't changed.

3. For each file in {fact-bundle}.files:
    1. {current-hash} = content hash from fact bundle
    2. {verified-hash} = navigator lookup for file's doc_verified_at marker
    3. {children-changed} = any child summary hash differs from last run
    4. If {current-hash} == {verified-hash} AND not {children-changed}:
        1. Mark file as cached; skip surface processing for this file later
    5. Else:
        1. Mark file for processing

### Classify System

4. {kind} = classification from path per `_system-discovery.md`
5. {required-docs} = required doc set from `_system-discovery.md` Required Documents Per Kind table
6. {agent-procedures-present} = check for skills / slash-command registrations / operational procedures in {fact-bundle}

### Canonical Docs: Regenerate with Port-Over

> Every canonical doc is regenerated from {fact-bundle}. Prior unverifiable prose is ported over. Surgical edits are NOT used for canonical docs.

7. For each {doc-kind} in {required-docs}:
    1. {doc-path} = system root + filename for {doc-kind}
    2. If exists(doc-path):
        1. {prior-content} = Read {doc-path}
        2. Extract claims — Call: `_claim-extraction.md` ({doc-content} = {prior-content}, {source-doc} = {doc-kind})
        3. {port-over-candidates} = claims with claim_type == unverifiable-prose
    3. Else:
        1. {prior-content} = ""
        2. {port-over-candidates} = []
    4. Generate fresh content:
        - If {doc-kind} == README.md: Call: `_doc-generation.md#readme` ({fact-bundle} = {fact-bundle}, {port-over-candidates} = {port-over-candidates})
        - If {doc-kind} == architecture.md: Call: `_doc-generation.md#architecture` (...)
        - If {doc-kind} == CLAUDE.md: Call: `_doc-generation.md#claude-md` ({agent-procedures} = {agent-procedures-present}, ...)
    5. If generation returns "SKIP" (for CLAUDE.md with empty procedures): proceed to next doc
    6. Validate generated content per `_doc-generation.md` Post-Generation Validation
    7. If architecture.md: regenerate Contents table from section scan per `_doc-generation.md` Contents Table Regeneration
    8. Write final content to {doc-path} via Write tool

### Non-Obvious Surfaces: Surgical Edits

> Surfaces use surgical edits because single-entity regeneration has no coherence benefit.

8. Enumerate surfaces per `_surfaces.md` Surface Discovery:
    - Module docstrings
    - Function/method/class docstrings
    - CLI help text
    - MCP tool descriptions
    - Frontmatter descriptions + argument hints
    - Header purpose statements in markdown files
    - Section purpose statements in markdown files
9. For each {surface} (skip if file marked cached in step 3):
    1. Extract claims — Call: `_claim-extraction.md` ({doc-content} = {surface-content})
    2. For each claim with verifiable == true:
        1. Deterministic candidate-fact selection per `_verification.md` Candidate Fact Selection
        2. If no candidate facts: verdict = no-evidence; add to unresolved if claim is non-trivial
        3. Else: Call: `_verification.md` ({claim}, candidate-facts, {fact-bundle})
    3. For each claim with verdict in [contradicted, partial]:
        1. Call: `_conservative-edit.md` ({claim}, {evidence}, {fact-bundle-slice}, {doc-path}, {doc-content})
        2. Validate per `_conservative-edit.md` Post-LLM Validation
        3. Apply via Edit tool
    4. If surface is missing (e.g., public function with no docstring) and generation is appropriate:
        1. Generate a purpose statement from signature + body + module context
        2. Insert via Edit tool or Write surgical insertion

### Bubble-Up Summary

10. Collect unresolved questions from all stages:
    - No-evidence verdicts on non-trivial claims
    - Sections without well-formed purpose statements
    - Ambiguous surgical edits retry loop couldn't resolve
    - Cross-system references outside this scope
    - Ported-over content not fitting any regenerated section (landed in "Notes"; flag for user attention)
    - Forwarded child-unresolved entries this agent's scope can't resolve
11. Resolve inherited child-unresolved entries where possible:
    1. For each entry in child summaries' unresolved lists:
        1. If this agent's scope has the information: resolve it (update relevant doc, answer the question)
        2. Else: annotate with this agent's context and add to own unresolved list
12. Update navigator hash markers for processed files:
    - bash: `${CLAUDE_PLUGIN_ROOT}/run.py update_system_docs.cli mark-verified --system {system} --run-id {run-id}`
13. Assemble bubble-up summary per `_summary-schema.md`
14. Write summary to `${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}/{system}/summary.md`
15. Return:
    - Summary pointer path
    - Short status: docs regenerated / created / unchanged counts; surfaces touched counts; unresolved count

## Spawned Agent Prompt Scaffold

When the skill executor spawns this workflow, the agent prompt includes:

```
You are a per-system documentation agent. Follow the instructions at
${CLAUDE_PLUGIN_ROOT}/skills/update-system-docs/_per-system-workflow.md.

Variables:
- {system} = <path>
- {child-pointers} = <JSON list of pointer paths>
- {run-id} = <id>

Component files you may Read or Call as needed:
- _claim-extraction.md
- _verification.md
- _conservative-edit.md
- _doc-generation.md
- _unverifiable-prose.md
- _summary-schema.md
- _surfaces.md
- _system-discovery.md

Return: summary pointer path + short status + unresolved count.
```
