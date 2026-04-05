---
pattern: "*/evaluate-*/SKILL.md"
depends:
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/skill-md.md
---

# Evaluation Skill Conventions

Specialized SKILL.md conventions for domain-specific evaluation skills. Applies to skills with the `evaluate-` directory prefix. Supplements the general skill-md convention — evaluation skills follow both.

Evaluation skills combine multiple evaluation lenses into one structured pass for a specific domain, eliminating cycling between general-purpose tools. One invocation, one report, one coherent change set.

## Naming

Directory: `evaluate-{domain}/`. Skill name: `{plugin}-evaluate-{domain}`. Domain names the target type.

## Evaluation Lenses

Complete catalog of evaluation perspectives. Each lens is a distinct concern. Implementations select which lenses apply to their domain and document the selection in a Lenses section.

### Conformity

**Does the target follow applicable project conventions?**

Load matching conventions via navigator `governance-for`. Evaluate target content against each convention's requirements. For targets spanning dependency chains, traverse root-first — evaluate foundational documents before derived ones, carrying forward what each layer establishes.

Failure modes:

- Convention requirements not reflected in target content
- Target contradicts convention guidance
- Dependency chain traversal order incorrect or incomplete

### Efficacy

**Does the target achieve its stated purpose? Can a consumer use it correctly from cold?**

Evaluate whether an agent encountering the target for the first time could use it correctly without external context, trial and error, or user assistance.

Failure modes:

- Unbound references — names, paths, or variables referenced but never defined
- Ambiguous instructions — multiple valid interpretations with different outcomes
- Missing context — information required for correct use that isn't present or referenced
- Unreachable content — sections that can never be reached via any path
- Cross-reference gaps — referenced files, tools, or sections that don't exist

### Quality

**Does the target follow best practices for its domain?**

Evaluate structural decisions and patterns within the target's domain. What constitutes "best practice" varies by target type — implementations define domain-specific criteria.

Failure modes:

- Anti-patterns specific to the target domain
- Structural readiness — target has outgrown its natural scope
- Naming and discoverability gaps
- Error handling inappropriate for the domain

### Prior Art

**Does the implementation mirror established patterns? If deviating, is it justified?**

Evaluate whether the target reinvents something with a well-known solution. Surface standard patterns, established approaches, and widely-adopted conventions that the implementation could mirror instead.

Failure modes:

- Custom implementation of a well-known pattern without justification
- Pattern transplanted from a fitting context into one where it doesn't fit
- Missing standard structure consumers would expect for the domain
- Deviation from established conventions without documented rationale

### Coherence

**Do related targets work together correctly? Is the system internally consistent?**

Evaluate consistency across multiple related files. Targets that exist in a system — parent-child, dependency chain, cross-references — must be consistent with each other.

Failure modes:

- Parent re-explaining what child documents cover (progressive disclosure violation)
- Cross-file contradictions — same concept described differently in related documents
- Dependency chain gaps — layer references capabilities from a lower layer that don't exist
- Orphaned references — targets assume related targets that are missing

## Skill Structure

Evaluation skills follow the standard SKILL.md convention with additional required sections.

### Lenses

Declares which lenses from the catalog the skill uses. Documents any domain-specific adaptation of a lens. This is the implementation contract — what an evaluation pass covers.

### Scope

Defines what the skill evaluates and how it discovers targets. Scope is domain-specific: skill evaluation scopes to files and their references, documentation evaluation scopes to a file type across systems, governance scopes to dependency chains.

Scope also declares accepted arguments beyond `--target`. Arguments that don't fit the stack's scope are rejected with guidance. Document accepted arguments and their effect on scope.

### Protocol

The evaluation process — what the orchestrating agent receives, how it plans execution, and how findings accumulate.

The orchestrator receives the scoped file list with sizes from navigator. It examines file relationships — which files are related, which lenses need shared context across files, which can evaluate independently — and produces an execution plan. This is a judgment call, not a deterministic routing decision: file relationships and lens context requirements vary by domain and by the specific files in scope.

Execution planning considerations:

- Some lenses require the same agent to traverse the same files (shared context matters for cross-file coherence)
- Some lenses are best served by an independent agent traversing the full scope (prior art evaluation doesn't depend on conformity findings)
- Large scopes may require splitting into groups of related files, where each group is processed by one agent or through context-aware iteration — passing the remaining file list and accumulated findings to the next agent
- File sizes inform how much work fits in one agent's context, but where to split depends on file relationships the orchestrator determines

Context-aware iteration is the mechanism for when a group exceeds one agent's context. The agent processes what it can, then passes forward:

- Files not yet evaluated
- Accumulated findings so far
- Any context needed for continuity (what was established in files already evaluated)

The next agent picks up from the checkpoint with full awareness of prior findings.

### Shared Infrastructure

Triage criteria and report format are cross-cutting concerns shared across evaluation skills. Reference shared component files rather than duplicating — single source of truth.

- **Triage criteria** — classifies findings as auto-fixable (Defect) or requiring judgment (Observation)
- **Report format** — unified change set where fixes across lenses don't conflict

Shared files live alongside evaluation skill directories, not inside any single skill.

## Report

Every evaluation skill produces:

1. **Scope** — what was evaluated and which lenses were applied
2. **Findings by lens** — classified, located, with recommended action
3. **Cross-lens interactions** — where fixing one finding would affect another
4. **Change set** — unified fixes coherent across all lenses; Defects only
5. **Observations** — findings requiring user judgment, with context from all applicable lenses
