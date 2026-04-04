# Governance Evaluation Lenses

Domain-specific criteria for each lens when evaluating governance files (rules and conventions).

## Conformity

Evaluate each governance file against its own governing conventions. Rules and conventions are themselves governed — design-principles governs communication, workflow governs conventions, etc.

Key checks:
- Does the file follow the conventions matched by `governance-for`?
- For rules: does the format match other rules at the same governance level?
- For conventions: does the structure match the file type it governs?

## Efficacy

Can an agent follow this governance file correctly from a cold start?

### Rules

- Are behavioral triggers unambiguous? Could two agents interpret the same trigger differently?
- Are gate conditions concrete? (measurable, not subjective)
- Do instructions reference files by path, not by name?
- Are there circular dependencies between triggers? (trigger A requires checking B, which requires checking A)

### Conventions

- Are content standards concrete enough that conformity is deterministic? (two agents evaluating the same file would reach the same conclusions)
- Do examples clarify ambiguous standards, or are they absent where needed?
- Are there standards that contradict each other within the same convention?
- Do patterns match the intended file types? (verify fnmatch behavior)

## Coherence

Cross-level consistency evaluated with accumulated context from prior levels.

### Vertical Coherence (across dependency chain)

- Does the file contradict anything its governors establish?
- Does it extend governor concepts consistently or redefine them?
- Are governance dependencies actually used? (linked in governs table but no content references the governor)
- Are there implicit dependencies not captured? (file references concepts from another governance file without a dependency relationship)

### Horizontal Coherence (within same level)

- Do files at the same governance level use consistent terminology?
- Do overlapping patterns create conflicting guidance? (two conventions match the same file but prescribe different things)
- Are there gaps? (file types in the project with no matching convention)

### Principle Enforcement

- Does every design principle have at least one rule or convention that enforces it?
- Are there rules that don't trace back to any principle?
- Are principles specific enough to be enforceable, or are they aspirational without actionable guidance?

## Prior Art

Evaluate the governance system design after the full chain is in context:

- Does the layered structure (principles → rules → conventions) mirror established policy/governance patterns?
- Is the dependency chain depth appropriate, or is there unnecessary nesting?
- Are there standard governance structures (linter configurations, style guides, contribution guidelines) that this system should mirror?
- Does the pattern-matching approach for convention application follow established conventions (EditorConfig, ESLint, pre-commit hooks)?
- If deviating from standard patterns, is the deviation justified by the agent-first context?
