# skill-source-conventions Specification

## Purpose
Lintable authoring rules for skill source bodies that make dependency flattening mechanical and reliable: conventional structure so demotion is uniform, portable self-references so path rewriting is a single substitution, and no model-mediated cross-skill indirection.
## Requirements
### Requirement: Conventional component structure

A skill body SHALL have exactly one H1 (the skill title) with all sections at H2, so uniform heading demotion of its component is well-defined.

#### Scenario: Deep heading in source

- WHEN a skill body contains an H3 or deeper heading outside a flatten region or fenced code block
- THEN lint reports the file

### Requirement: Portable self-references

A skill body SHALL reference its own bundled files as `${CLAUDE_SKILL_DIR}/…` rather than absolute or bare relative paths. The runtime substitutes the variable throughout skill markdown, and the flatten tool rewrites it on transplant.

#### Scenario: Hardcoded absolute path

- WHEN a skill body references a bundled file by absolute filesystem path
- THEN lint reports the reference for conversion to `${CLAUDE_SKILL_DIR}` form

### Requirement: Marker hygiene

A marker-shaped line (`<!-- flatten-skills … -->`) SHALL appear only as a real region delimiter or inside a fenced code block as a documented example.

#### Scenario: Stray marker line

- WHEN a marker-shaped line appears outside a fence but is not part of the file's single well-formed region
- THEN lint reports the file

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

