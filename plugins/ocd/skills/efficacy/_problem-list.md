# Problem List

Two tiers guide what evaluating agents look for. Not exhaustive — agents report any issue found regardless of whether it matches a listed example.

## Defects

Will cause incorrect execution. Deterministic to identify and fix.

- Unbound or unassigned variables — variable referenced but never assigned, or assigned in unreachable branch
- PFN notation errors — If/Else if chain violations, missing colon suffixes, incorrect indentation semantics
- Missing flow control — unreachable steps, branches with no assignment before consumption, missing Else in chains that require it
- Conditions that do not match stated intent — condition text contradicts what surrounding steps expect it to protect against
- Cross-references to nonexistent targets — step numbers, section names, or file paths that do not exist

## Observations

Require judgment to act on. Report but never auto-fix.

- Ambiguity that has not caused a defect but could under different execution
- Redundancy that could drift out of sync between source and restated location
- Simplification opportunities where fewer steps could achieve same outcome
- Wording that could be clearer without changing behavior
