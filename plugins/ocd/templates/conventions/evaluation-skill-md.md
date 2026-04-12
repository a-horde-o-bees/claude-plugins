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

Directory: `evaluate-{domain}/`. Skill name: `evaluate-{domain}`. Domain names the target type.

## Holistic Reading, Not Lenses

Evaluation skills do not split their pass into independent lens traversals. A single agent reads the target set in the correct traversal order (dependency order, alphabetical, whatever the domain prescribes) and evaluates each target against every concern simultaneously per the skill's evaluation criteria file. Splitting into distinct lens passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading prevents that spiral.

Each skill describes its own concerns in its own criteria file rather than selecting from a shared lens catalog. The concerns an evaluation skill holds are domain-specific and documenting them in a shared catalog creates either the illusion of a universal framework or the burden of adapting every lens to every domain.

## Scope

Scope is domain-specific. Skill evaluation scopes to files and their references. Documentation evaluation scopes to a file type across systems. Governance scopes to a dependency chain.

Scope also declares accepted arguments beyond `--target`. Arguments that don't fit the skill's domain are rejected with guidance. Document accepted arguments and their effect on scope.

## Report-Only Agent

The spawned agent does not classify findings, apply fixes, or reason about triage. It reads, evaluates, and reports. The orchestrator owns triage (via `evaluation-triage.md`) and application. This separation is load-bearing:

- Decoupling evaluation from classification lets the orchestrator apply uniform triage across all domains without requiring each agent to re-implement it
- Keeping the agent report-only means its returns can be audited against a small, stable format
- The orchestrator can interrupt between cycles without the agent holding stale classification state

## Evaluation Workflow File

Every evaluation skill carries its own agent workflow file alongside SKILL.md (e.g., `_evaluation-workflow.md`). The file is read by the spawned agent at the start of its execution and defines:

- The reading disposition — what stance the agent holds as it walks the target set
- What to surface — a non-exhaustive inventory of active checks and friction cues the agent watches for. Frame as partial inventory, not checklist — the agent should surface friction that doesn't match any listed category rather than filtering it out
- Domain-specific anomaly conditions that force an early return from the traversal, if any
- The finding return format — file, location, what, why, proposed fix or needs judgment

The criteria file is customized to the domain. Two evaluation skills targeting different things do not share criteria — governance evaluation looks for things skill evaluation does not, and vice versa.

## Skill Structure

Evaluation skills follow the standard SKILL.md section ordering with domain-specific additions:

1. Process Model — holistic reading rationale and orchestration design (what the agent holds, how the orchestrator dispatches and triages)
2. Scope — accepted arguments and target discovery
3. Trigger
4. Route
5. Workflow — sole executable section; use PFN blockquotes for inline orchestration rationale (e.g., why defects are safe to auto-apply, why observations exit to user)
6. Rules — report-only agent invariant and other load-bearing invariants specific to the skill

Process Model covers the conceptual design at an appropriate level of abstraction. Detailed orchestration rationale lives in Workflow as blockquote context adjacent to the steps it explains, not in a separate Protocol section.

## Report

Every evaluation skill produces:

1. **Scope** — what was evaluated (files, levels, groups)
2. **Applied Defects** — grouped by file, each with location and applied fix
3. **Observations** — surfaced when present, each presented as-is from the agent's finding (file path, location, what is wrong, why, and proposed fix). Do not summarize or strip content — the user needs the full finding to make a judgment call. Presentation is interactive (exit to user), not a final-report section, because Observations typically require the skill to exit for judgment
4. **Status** — terminal outcome of the invocation (clean, defects applied, observations outstanding, anomaly restart)
