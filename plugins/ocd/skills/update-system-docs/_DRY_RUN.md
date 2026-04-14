# Dry-Run Findings: lib/governance

Mental walkthrough of the skill's workflow against `plugins/ocd/lib/governance/` — the smallest real system in the project. Purpose: stress-test the design, surface failure modes, identify v1 scope cuts.

## Setup

Initial state of `lib/governance/`:

- `__init__.py` — facade
- `_governance.py` — governance operations
- `_frontmatter.py` — frontmatter parsing
- `cli.py` — CLI debug entry
- `tests/` — excluded from system scope
- No README.md, no architecture.md, no CLAUDE.md

System kind: **library** (heuristic 5). Required docs: README.md + architecture.md.

Wave 0: lib/governance runs as a leaf.

## Walkthrough

### Fact bundle build

- File inventory: 4 Python files via `paths_list`
- AST parse each: module docstrings, public/private functions, imports
- No manifests at system level (inherits from plugin)
- No MCP tools (library, not server)
- CLI commands from `cli.py` argparse
- No child summaries (leaf)
- Imports graph: `_governance.py` → `_frontmatter.py`; `cli.py` → facade

### Doc triage

- to-create: `[README.md, architecture.md]`
- to-update: `[]`

### Doc generation — README.md

Running the README generation prompt against the fact bundle reveals a problem:

- **Installation** — no manifest at system level. Section omitted.
- **Usage** — `cli.py` has argparse entries, but they're for debugging, not user-workflow. The prompt emits them literally.
- **Configuration** — no env vars or config schema.

Result:

```markdown
# governance

Governance library — matches files to applicable conventions, lists governance entries, and computes level-grouped dependency order.

## Usage

```
python3 -m plugins.ocd.lib.governance.cli order --json
```
```

The README is two lines plus one code block. That's barely a README.

### Doc generation — architecture.md

More substantial output:

```markdown
# governance Architecture

Governance library for matching files to applicable conventions, listing governance entries, and computing level-grouped dependency order. Reads directly from disk — no database, no caching.

## Components

### __init__.py

Facade — public interface for governance operations.

- (no public symbols defined here; facade re-exports from internal modules)

### _governance.py

Governance operations. Governance matching, listing, and dependency ordering.

- governance_match
- governance_order
- governance_list

### _frontmatter.py

Frontmatter parsing — YAML extraction from governed markdown files.

- parse_frontmatter
- matches_pattern
- normalize_patterns
- parse_governance

### cli.py

CLI for debugging — exposes governance operations via shell.

- (CLI subcommands; see `python3 -m lib.governance.cli --help`)

## Relationships

- _governance.py -> _frontmatter.py: matches_pattern, normalize_patterns, parse_governance
- cli.py -> __init__.py: facade star import
- _governance.py -> plugin: plugin.get_project_dir

## Patterns

- Facade + underscore-prefixed internal modules
- Disk-reading over cached/database storage (explicit anti-pattern declaration)
```

Reasonable and grounded.

### Non-obvious surfaces

Within lib/governance scope:

- `__init__.py` module docstring: "Governance library facade. Public interface..." — matches actual content. No drift.
- `_governance.py` module docstring: matches.
- `_frontmatter.py` module docstring: (assumed to match).
- `cli.py` module docstring and argparse help text: verified against argparse setup.
- Function docstrings: v1 scope cut — defer.

### Bubble-up summary

Written to `${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}/plugins/ocd/lib/governance/summary.md`. Parent (ocd plugin, Wave 1) reads this to describe lib/governance in ocd's architecture.md Subsystems section.

## User Decisions

All seven findings reviewed with user on 2026-04-14. Decisions:

1. **Internal-library README** — accept minimal (purpose statement only); README stays but has no installation/usage/config sections when fact bundle has none. Architecture.md Contents table supersedes the need for README→architecture pointers.
2. **Function docstrings** — in scope; implement hash caching via navigator to skip unchanged files on re-run. Heavy first-run cost accepted.
3. **Discovery CLI** — confirmed needed; implementation pending (Python module under skill dir).
4. **Heavily-drifted doc threshold** — irrelevant; canonical docs always regenerate with port-over. Threshold concept removed.
5. **cli.py → __main__.py** — cli.py was accidental convention violation; skill handles gracefully but the codebase cleanup is separate parallel work.
6. **Full regeneration over surgical edits (canonical docs only)** — new direction: regenerate canonical docs from fact bundle, port over unverifiable prose from prior doc. Surgical edits reserved for non-obvious surfaces where regeneration has no coherence benefit.
7. **Skills ARE systems** — no complexity trigger. SKILL.md always; architecture.md when Document Separation rule would otherwise be violated (i.e., SKILL.md starts containing architectural content).
8. **Unresolved questions bubble up** — any unresolvable claim/question propagates through parents to the final Report for user judgment. Replaces the previous "count no-evidence claims" approach with an actionable list.
9. **Contents table in architecture.md** — derived projection copying each section's first-paragraph purpose into a table after the architecture.md H1. Skill owns regeneration; SSoT stays with sections.
10. **Purpose Statement guidance updated** — design-principles.md revision makes explicit that purpose statements apply at every scale (document, section, module, function), with consistent scope + role structure across scales.

## Original Findings (superseded by user decisions above, retained for context)

### Finding 1: Internal-library READMEs are nearly empty

**Problem**: An internal library with no user-facing installation/usage/config produces a README with just a purpose statement. This may be technically correct but unhelpful.

**Options:**

- A. Accept minimal READMEs for internal libraries. The user's judgment is "docs are a consequence of reality" — if reality has nothing user-facing, the doc is minimal.
- B. Detect "internal" vs "external" systems via consumption patterns (imports graph from outside). For internal-only systems, expand the README's role to describe *contents* rather than user workflow.
- C. Drop the README requirement for internal-only libraries. Architecture.md covers contents. README is only for external systems.

**Recommendation**: C for v1. Update `_system-discovery.md` Required Documents Per Kind table to make README conditional on "external consumption detected" for library kind. system-documentation.md says README is "required for every system" but the rule was written for a different model; consistency with "reality-first" principle argues for dropping README when the audience doesn't exist.

**Impact on system-documentation.md**: This finding suggests tightening system-documentation.md's README requirement from "every system" to "every system with external consumers." Worth discussing with user separately.

### Finding 2: Function docstring drift detection is expensive in v1

**Problem**: Every public function's docstring could be a drift surface. For a system with 30+ functions, the extract-verify-edit loop per function is O(N·LLM-calls). First run dominated by creation, not update — function docstring drift is a rare marginal case.

**Recommendation**: Drop function docstring drift detection from v1 non-obvious surfaces. Keep only: module docstrings, CLI help text, MCP tool descriptions, frontmatter descriptions, header purpose statements. Add function docstrings to v2 scope.

### Finding 3: `update_system_docs.cli discover` doesn't exist yet

**Problem**: Route step 3 calls a Python CLI that must be implemented. The skill has no code yet — the component files are prompts and workflows only.

**Recommendation**: Implement discovery as a separate CLI module under `plugins/ocd/skills/update-system-docs/`. Pattern: `cli.py` with argparse, calls into `_discovery.py` for the heuristic logic. Output JSON as specified. This is deterministic code, not agent judgment — belongs in a script per Determinism by Default.

### Finding 4: Spawned agent data flow needs explicit prompt scaffold

**Problem**: The skill executor's `Spawn: Call: _per-system-workflow.md (...)` translates to a Task-tool agent prompt. The agent gets the workflow instructions plus variable values, but also needs to know which component files to read as Called. The skill framework for this is informal.

**Recommendation**: The spawned agent prompt explicitly lists file paths it can read. Example prompt structure:

```
You are a per-system documentation agent. Follow the instructions at
plugins/ocd/skills/update-system-docs/_per-system-workflow.md.

Variables:
- {system} = <path>
- {child-pointers} = <list>
- {run-id} = <id>

Component files you may read as needed (via Call):
- _claim-extraction.md
- _verification.md
- _conservative-edit.md
- _doc-generation.md
- _unverifiable-prose.md
- _summary-schema.md
- _surfaces.md

Return: summary pointer path + short status.
```

Not a workflow change — a skill-prompt-assembly detail.

### Finding 5: Fact bundle assembly is Python-only in v1

**Problem**: The workflow assumes Python AST parsing for fact bundle. Other languages (YAML, JSON configs, Markdown itself) are handled ad-hoc. For this project all "code" is Python + markdown + JSON, so this is fine — but the skill's generalizability to TS/Go/Rust projects requires tree-sitter or LSP later.

**Recommendation**: v1 is Python-only. Document the limitation in SKILL.md Rules. v2 adds tree-sitter MCP dependency for multi-language.

### Finding 6: No-evidence claims accumulating

**Problem**: The verification step emits `no-evidence` verdicts for claims the fact bundle doesn't cover. These show up in the summary as a count. Over many systems, these accumulate. The user has to decide whether the no-evidence claims are legitimate (unverifiable prose the classifier missed) or real drift the fact bundle couldn't catch.

**Recommendation**: Report no-evidence claims with their claim text in the final Report so user can audit. v1 surfaces them as "N no-evidence claims — see {scratch-dir}/no-evidence.md" for review.

### Finding 7: Idempotence on regeneration

**Problem**: If a README already exists and needs full regeneration (not just update), the skill's current flow goes through the update path (extract claims, verify, edit). Only if the file is truly absent does it go to creation. What if the existing doc is so misaligned that surgical edits are infeasible?

**Recommendation**: Add a threshold: if the ratio of (contradicted claims / total claims) exceeds 50% for a doc, prompt the user to either accept wholesale regeneration (with preserved-prose splicing) or proceed with surgical edits and accept a degraded doc. v1 defaults to surgical edits; flag the threshold crossing in the Report.

### Finding 8: Project-root-level traversal

**Problem**: The project root's README.md and architecture.md describe the whole marketplace. Wave 2 agent reads Wave 1's ocd plugin summary plus any other top-level plugins (e.g., blueprint if included). The dry-run scoped out blueprint — in reality blueprint would be another Wave 1 system feeding Wave 2.

**Recommendation**: The skill's scope should be the project root for --target=project. For --target=<specific-plugin> (v2), it would scope to that plugin and not touch project-level docs. v1 is whole-project.

## Design Adjustments from Dry-Run

Apply to the design:

1. Update `_system-discovery.md`: library READMEs conditional on external consumers (Finding 1)
2. Update `_surfaces.md`: drop function docstrings from v1 scope (Finding 2)
3. Add `cli.py` + `_discovery.py` to the skill directory; implement discovery CLI (Finding 3)
4. Update `_per-system-workflow.md` preamble: document expected prompt scaffold (Finding 4)
5. Add v1-scope Rule to SKILL.md: Python-only fact bundle; other language support is future (Finding 5)
6. Update `_summary-schema.md`: include no-evidence claim details (Finding 6)
7. Update `_per-system-workflow.md`: add heavily-drifted doc threshold (Finding 7)

## Residual Risks Not Resolved by Dry-Run

- **Prompt reliability** at claim-extraction and verification stages — no amount of design review substitutes for running against real doc content and measuring false-positive / false-negative rates. Early-iteration runs will need manual review.
- **Token usage at scale** — for a large project, whole-run could consume >500k tokens. Need to budget for this and consider smaller `--target` granularity in v2.
- **Interactive user decisions** during run — e.g., "this surgical edit is ambiguous; approve?" — the current design is fully automated. May need user-interrupt point for ambiguous edits.

Cross-plugin references — a plugin's docs claiming content about a sibling plugin — are invalid by construction. Per-plugin docs describe only their own plugin; project-root docs describe all plugins from project-root scope. The skill rejects cross-plugin claims as a valid category and treats any appearance as a defect to fix.

## Verdict

The design holds up in the walkthrough. The seven findings are refinements, not blockers. The core loop (discovery → wave dispatch → per-system fact bundle → claim extraction → verification → surgical edit → bubble-up summary) is sound and implementable.

v1 scope: whole-project, Python-only, canonical docs + module docstrings + CLI help + MCP tool descriptions + frontmatter descriptions. Function docstrings, multi-language, and interactive ambiguity resolution — all v2.

Ready to commit design + skeleton skill files for user review.
