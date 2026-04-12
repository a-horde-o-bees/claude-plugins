---
includes: "*/evaluate-*/SKILL.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/conventions/ocd/skill-md.md
---

# Evaluation Skill Conventions

Specialized SKILL.md conventions for domain-specific evaluation skills. Applies to skills with the `evaluate-` directory prefix. Supplements the general skill-md convention — evaluation skills follow both.

Evaluation skills produce structured findings on a target set through a single holistic pass by a spawned agent. The orchestrator handles triage and application; the spawned agent is report-only. One invocation produces one walk of the target set and one set of findings for the orchestrator to act on.

## Naming

Directory: `evaluate-<domain>/`. Skill name: `evaluate-<domain>`. Domain names the target type.

## Holistic Reading, Not Lenses

Evaluation skills do not split their pass into independent lens traversals. A single agent reads the target set in the correct traversal order (dependency order, alphabetical, whatever the domain prescribes) and evaluates each target against every concern simultaneously per the skill's evaluation criteria file. Splitting into distinct lens passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading prevents that spiral.

Each skill describes its own concerns in its own criteria file rather than selecting from a shared lens catalog. The concerns an evaluation skill holds are domain-specific and documenting them in a shared catalog creates either the illusion of a universal framework or the burden of adapting every lens to every domain.

## Scope

Scope is domain-specific. Skill evaluation scopes to files and their references. Documentation evaluation scopes to a file type across systems. Governance scopes to a dependency chain.

Scope also declares accepted arguments beyond `--target`. When unrecognized arguments are provided, the skill responds with its description and argument-hint (same as calling without arguments). Document accepted arguments and their effect on scope.

## Report-Only Agent

The spawned agent does not classify findings, apply fixes, or reason about triage. It reads, evaluates, and reports. The orchestrator owns triage (via `evaluation-triage.md`) and application. This separation is load-bearing:

- Decoupling evaluation from classification lets the orchestrator apply uniform triage across all domains without requiring each agent to re-implement it
- Keeping the agent report-only means its returns can be audited against a small, stable format
- The orchestrator can interrupt between cycles without the agent holding stale classification state

## Evaluation Workflow File

Every evaluation skill carries its own `_evaluation-workflow.md` alongside SKILL.md. The agent reads it at the start of execution. The file follows a prescribed section structure; content within each section is customized to the domain. Two evaluation skills targeting different things do not share workflow files — governance evaluation watches for things skill evaluation does not, and vice versa.

Prescribed sections:

| Section | Content |
|---------|---------|
| `## Reading Disposition` | <What stance the agent holds as it walks the target set — domain-specific concerns the agent evaluates simultaneously> |
| `## What to Surface` | <Non-exhaustive inventory of patterns worth noticing, organized under subsection headings by concern>. Frame as partial inventory, not checklist — the agent should surface friction that doesn't match any listed category rather than filtering it out |
| `## <Anomaly Conditions>` | <Domain-specific conditions that force an early return from the traversal>. Omit section entirely if the domain has none; include a brief note explaining the absence if the convention's existence would otherwise make the omission ambiguous |
| `## Accumulation and Return` | <Finding return format and report-only instructions>. The following elements are prescribed across all domains and must appear verbatim or equivalent: agent is report-only (no triage, no classification, no fixes); violations with plausible intentional rationale still get recorded with `needs judgment`; findings are a flat list where each entry names file path, location, what is wrong, why, and proposed fix or `needs judgment` |

## Skill Structure

Evaluation skills follow the standard SKILL.md section ordering. This convention promotes Process Model from Common to Prescribed (every evaluation skill needs it) and prescribes the section ordering below:

1. Process Model — <holistic reading rationale and dispatch/triage design for this domain>
2. Scope — <accepted arguments and how target discovery works for this domain>
3. Trigger
4. Route
5. Workflow — sole executable section; use PFN blockquotes for inline rationale (e.g., why defects are safe to auto-apply, why observations exit to user). Includes `### Report` per the Report template below
6. Rules — must include the report-only agent invariant; <other load-bearing invariants specific to the domain>

Process Model covers the conceptual design at an appropriate level of abstraction. Detailed rationale lives in Workflow as blockquote context adjacent to the steps it explains, not in a separate Protocol section.

## Report

Every evaluation skill includes a `### Report` subheading in Workflow. The skeleton below is prescribed; items marked with `<...>` are customized to the domain.

1. **Scope** — <what was evaluated: files, levels, groups, or other domain-appropriate unit>
2. **Applied Defects** — grouped by file; each entry shows location, the fix applied, and the source finding
3. **Observations** — presented as-is from agent findings (file path, location, what is wrong, why, and proposed fix). Do not summarize or strip content — the user needs the full finding to make a judgment call. Observations are surfaced interactively (exit to user) before the final report because they require user judgment before the skill can proceed
4. **Status** — terminal outcome of the invocation. Common values include `clean`, `defects applied`, `observations outstanding`; <domain-specific statuses as needed, e.g., `restarted after anomaly` for governance>
