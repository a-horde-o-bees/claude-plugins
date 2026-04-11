---
includes: "*/evaluate-*/SKILL.md"
governed_by:
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/skill-md.md
---

# Evaluation Skill Conventions

Specialized SKILL.md conventions for domain-specific evaluation skills. Applies to skills with the `evaluate-` directory prefix. Supplements the general skill-md convention — evaluation skills follow both.

Evaluation skills produce structured findings on a target set through a single holistic pass by a spawned agent. The orchestrator handles triage and application; the spawned agent is report-only. One invocation produces one walk of the target set and one set of findings for the orchestrator to act on.

## Naming

Directory: `evaluate-{domain}/`. Skill name: `{plugin}-evaluate-{domain}`. Domain names the target type.

## Holistic Reading, Not Lenses

Evaluation skills do not split their pass into independent lens traversals. A single agent reads the target set in the correct traversal order (dependency order, alphabetical, whatever the domain prescribes) and evaluates each target against every concern simultaneously per the skill's evaluation criteria file. Splitting into distinct lens passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading prevents that spiral.

Each skill describes its own concerns in its own criteria file rather than selecting from a shared lens catalog. The concerns an evaluation skill holds are domain-specific and documenting them in a shared catalog creates either the illusion of a universal framework or the burden of adapting every lens to every domain.

## Scope

Scope is domain-specific. Skill evaluation scopes to files and their references. Documentation evaluation scopes to a file type across systems. Governance scopes to a dependency chain.

Scope also declares accepted arguments beyond `--target`. Arguments that don't fit the skill's domain are rejected with guidance. Document accepted arguments and their effect on scope.

## Protocol

The evaluation process — what the orchestrator receives, how it plans execution, how findings are returned and acted on.

The orchestrator receives the scoped target set from a domain-specific source (navigator tool, path list, or whatever the domain prescribes) and either dispatches a single spawned agent over the whole set or spawns an agent for the first sub-group and continues it cycle-by-cycle via `Continue {agent-ref} with:`. Per-cycle checkpointing is appropriate when the orchestrator needs to intervene between sub-groups — for example, when changes at an earlier level might affect how later levels should be evaluated.

After each cycle (or at the end of a whole-set pass):

1. The agent returns findings in report-only form — each finding carries file path, location, what is wrong, why, and a proposed fix or an explicit `needs judgment` flag
2. The orchestrator classifies each finding against `evaluation-triage.md`
3. Defects are auto-applied directly to disk; Observations are surfaced to the user
4. The orchestrator decides whether to continue the agent for the next cycle, exit to user for judgment, or present a final report

If the target set evolves during evaluation (e.g., frontmatter corrections reorder a dependency chain), the orchestrator re-queries its domain source and restarts the pass. Partial findings accumulated before the restart are presented to the user for reference but not auto-applied, since the correction may have changed what counts as valid.

## Report-Only Agent

The spawned agent does not classify findings, apply fixes, or reason about triage. It reads, evaluates, and reports. The orchestrator owns triage (via `evaluation-triage.md`) and application. This separation is load-bearing:

- Decoupling evaluation from classification lets the orchestrator apply uniform triage across all domains without requiring each agent to re-implement it
- Keeping the agent report-only means its returns can be audited against a small, stable format
- The orchestrator can interrupt between cycles without the agent holding stale classification state

## Evaluation Criteria File

Every evaluation skill carries its own evaluation criteria file alongside SKILL.md (e.g., `_evaluation-criteria.md`). The file is read by the spawned agent at the start of its execution and defines:

- The reading disposition — what stance the agent holds as it walks the target set
- What to surface — the active checks and friction cues the agent watches for
- Domain-specific anomaly conditions that force an early return from the traversal, if any
- The finding return format — file, location, what, why, proposed fix or needs judgment

The criteria file is customized to the domain. Two evaluation skills targeting different things do not share criteria — governance evaluation looks for things skill evaluation does not, and vice versa.

## Skill Structure

Evaluation skills follow the standard SKILL.md convention with the following additions:

- Scope section documents accepted arguments and how targets are discovered
- Protocol section describes orchestrator flow and per-cycle handling
- Rules section documents the report-only agent invariant and other load-bearing invariants specific to the skill

## Report

Every evaluation skill produces:

1. **Scope** — what was evaluated (files, levels, groups)
2. **Applied Defects** — grouped by file, each with location and applied fix
3. **Observations** — surfaced when present, each with full context so the user can judge; presentation is interactive, not a final-report section, because Observations typically require the skill to exit to user for judgment
4. **Status** — terminal outcome of the invocation (clean, defects applied, observations outstanding, anomaly restart)
