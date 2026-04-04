# Skill Evaluation Lenses

Domain-specific criteria for each lens when evaluating skills.

## Conformity

Evaluate against governance files matched by `governance-for`. Key conventions for skills:

- **skill-md** — frontmatter fields, body structure (Route, Workflow, Rules), orchestration vs execution boundary, component extraction, file enumeration, user interaction boundary
- **evaluation-skill-md** — only for `evaluate-*/` skills; lenses section, scope, protocol, shared infrastructure references

Cite specific convention requirements with each finding.

## Efficacy

### Defects

- Unbound or unassigned variables — variable referenced but never assigned, or assigned in unreachable branch
- PFN notation errors — If/Else if chain violations, missing colon suffixes, incorrect indentation semantics
- Missing flow control — unreachable steps, branches with no assignment before consumption, missing Else in chains that require it
- Conditions that do not match stated intent — condition text contradicts what surrounding steps expect
- Cross-references to nonexistent targets — step numbers, section names, file paths, CLI commands that do not exist
- Component files referenced but missing from skill directory

### Observations

- Ambiguity that has not caused a defect but could under different execution
- Redundancy that could drift out of sync between source and restated location
- Simplification opportunities where fewer steps could achieve same outcome

## Quality

### Skill-Specific Criteria

- **Workflow encapsulation** — is the workflow self-contained? Could an agent given only the workflow + rules execute without referencing other sections?
- **Route clarity** — does the route clearly map every target type to a workflow? Are there ambiguous fallthrough cases?
- **Component extraction** — should any workflow content be extracted to `_*.md` files? Is SKILL.md approaching size limits?
- **Agent spawn discipline** — are agent spawns justified? Could inline execution achieve the same result?
- **CLI invocation completeness** — are CLI commands full executable commands with interpreter, path, and all flags?
- **Error path coverage** — do failure cases (exit code 1, missing files, invalid input) have explicit handling?
- **Unnecessary indirection** — pass-through steps that add no value
- **Scattered responsibility** — operations that should be single CLI calls assembled as multi-step sequences

## Prior Art

Evaluate the skill's approach against established patterns:

- Does the workflow structure follow standard orchestration patterns (dispatch, fan-out/fan-in, pipeline)?
- Are there well-known solutions for the problem this skill solves?
- Does the skill reinvent infrastructure that existing tools provide?
- If the approach deviates from standard patterns, is the deviation justified by constraints or requirements?
