# Evaluation Instructions

Evaluate scope against criteria catalog by focus area. Follow project Discovery instructions to understand project conventions before evaluating.

## Focus Areas

Evaluate all applicable focus areas sequentially within scope.

### Structure and Dependencies

Evaluate code structure and dependency patterns for convention violations and architectural smells. Focus on how code is organized, how modules depend on each other, and whether structure follows standard practices.

Criteria categories:
- Unnecessary Indirection
- Scattered Responsibility
- Redundant Operations
- Dependency Direction
- Structural Readiness
- Complexity and Cohesion

### Conventions and Safety

Evaluate code-level conventions and safety patterns. Focus on naming, error handling, type safety, and whether code follows standard practices for its language.

Criteria categories:
- Convention Violations
- Cargo-Cult Patterns
- Naming and Discoverability
- Error Handling and Failure Semantics
- Security and Input Validation

### Documentation and Ergonomics

Evaluate documentation accuracy and agent ergonomics. Focus on whether documentation matches reality, whether agents can orient without reading source code, and whether interfaces are discoverable.

Criteria categories:
- Stale Artifacts
- Agent Ergonomics
- Output and Format Anti-patterns

Additionally answer: can an agent arriving at this scope determine what operations are available without reading source code? Check navigator entries, CLI help text, naming clarity, and documentation currency.

### Architecture (project scope only)

Evaluate project-level architectural decisions — structural patterns that span entire project. Code-level quality is handled by other focus areas; this evaluates decisions that created units and the connections between them.

Criteria categories:
- Project Architecture

Phase 1 — map structural decisions: package structure, import resolution, dependency management, test infrastructure, tooling compatibility.

Phase 2 — evaluate each structural decision against Project Architecture criteria.

Phase 3 — report with current architecture summary, findings, trade-off assessments.

## Per-Finding Report Format

For each finding:
1. State criteria category
2. Describe what was found with specific file paths and line references
3. Explain what the conventional alternative would be
4. Assess trade-off — justified in context or creating friction?
5. Recommend specific action

Do not invent findings to fill categories. Report only what is actually observed. Skip categories with no issues.

## Overall Assessment

Classify scope as one of:
- **conventional** — follows standard practices
- **unconventional-but-justified** — deviations exist but trade-offs are acceptable
- **unconventional-with-friction** — deviations create ongoing cost
