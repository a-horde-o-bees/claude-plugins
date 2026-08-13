# skill-source-conventions Delta

## REMOVED Requirements

### Requirement: No cross-skill slash references

**Reason**: The ban existed because `/skill-name` was an unverified model-mediated hop. Under reference-derived flattening the slash form is the declaration mechanism itself — verified, materialized, and anchor-linked — so the reliability problem the ban solved no longer exists.

**Migration**: Existing bare-name citations may be restored to `/skill-name` form where the host should declare and link the dependency; lint now flags only references that fail to compile.

## ADDED Requirements

### Requirement: Cross-skill references compile

A `/skill-name` reference in a skill body outside a fenced code block SHALL resolve to a sibling suite skill and, after materialization, SHALL be linked to the in-file anchor of the flattened unit. Lint SHALL report any unresolved reference as an error and any resolved-but-unlinked reference as stale. Slash text inside fenced code blocks is exempt as definitional example content, as is a skill's reference to its own invocation surface.

#### Scenario: Unresolved reference

- WHEN a skill body outside a fence contains `/no-such-skill` naming no sibling suite skill
- THEN lint reports it as an error

#### Scenario: Resolved and linked reference passes

- WHEN a skill body contains `[/concise-prose](#concise-prose)` and the materialized file contains the matching unit heading
- THEN lint does not report it

#### Scenario: Self-reference and definitional examples exempt

- WHEN the git skill's body says `/git checkpoint`, or a skill shows `/skill-name` syntax inside a fenced example
- THEN lint does not report it
