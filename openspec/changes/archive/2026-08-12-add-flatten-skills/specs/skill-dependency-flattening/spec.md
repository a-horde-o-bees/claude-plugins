## Purpose

Deterministic build-time composition of skills: a skill declares dependencies on sibling skills, and a flatten tool materializes their full bodies into a marker-delimited generated region inside its SKILL.md, so the loaded skill never relies on model-mediated invocation or runtime preprocessing to see the text it depends on.

## ADDED Requirements

### Requirement: Marker region

A SKILL.md SHALL contain at most one flatten region, delimited by a START line carrying a JSON declaration and a bare STOP line: `<!-- flatten-skills START {"deps": ["<name>", ...]} -->` … `<!-- flatten-skills STOP -->`. The region MAY appear anywhere in the body. Everything between the marker lines is generated content; the source layer of the file is everything outside the region plus the marker lines themselves.

#### Scenario: Source view survives region stripping

- WHEN the content between START and STOP is deleted
- THEN the file remains valid source: the declaration on the START line is intact and a refresh reconstitutes the region

#### Scenario: Multiple regions rejected

- WHEN a SKILL.md contains more than one START/STOP region
- THEN the tool exits with an error identifying the file

### Requirement: JSON declaration

The START line's payload SHALL be a JSON object parsed with a standard JSON parser. The `deps` key holds an ordered list of dependency skill folder names; names MAY contain any characters representable in a JSON string, including spaces.

#### Scenario: Malformed declaration

- WHEN the START line's payload is not valid JSON or lacks a `deps` list
- THEN the tool exits with an error identifying the file and the payload

### Requirement: Refresh regenerates the whole region

Refresh SHALL first build the dependency graph across all declared skills, then rewrite each region in full: the generated content is a `## Dependencies` heading followed by the flat, deduplicated transitive closure of the declaring skill's dependencies, each unit appearing exactly once. Refresh keeps no incremental state; every run regenerates every region from source layers alone, so refresh is idempotent and order-independent.

#### Scenario: Shared transitive dependency deduplicated

- WHEN skill A declares deps on B and C, and both B and C depend on D
- THEN A's region contains B, C, and D once each

#### Scenario: Circular dependency

- WHEN the dependency graph contains a cycle
- THEN the tool exits with an error naming the cycle, and writes no regions

### Requirement: Component extraction

A dependency's component SHALL be its SKILL.md minus frontmatter and minus its own flatten region (marker lines included). Extraction never reads another skill's generated content as input.

#### Scenario: Dependent-of-dependent extraction

- WHEN skill A depends on B, and B's SKILL.md contains a materialized region
- THEN the B unit inlined into A contains only B's source component, and B's dependencies enter A's region as separate deduplicated units

### Requirement: Uniform heading demotion

Every inlined unit SHALL be emitted at the same heading level: the unit's H1 title becomes an H3 under the generated `## Dependencies` H2, and its H2 sections become H4, uniformly.

#### Scenario: Section cross-reference resolves in host

- WHEN a host skill's source cites a section of a declared dependency (e.g. "concise-prose § Anti-staleness")
- THEN the referenced section is present in the host's materialized file under the demoted unit

### Requirement: Bundled-file path rewriting

When inlining a dependency whose body references its own bundled files via `${CLAUDE_SKILL_DIR}/…`, the tool SHALL rewrite those occurrences to `${CLAUDE_SKILL_DIR}/../<dependency-folder>/…`, so the runtime's substitution in the host resolves to the sibling-installed dependency folder.

#### Scenario: Dependency with companion files

- WHEN a dependency's body references `${CLAUDE_SKILL_DIR}/scripts/tool.py`
- THEN the host's materialized region references `${CLAUDE_SKILL_DIR}/../<dependency-folder>/scripts/tool.py`

### Requirement: Freshness check

A check mode SHALL recompute every region from source layers and byte-compare against the file on disk, exiting nonzero and naming each stale or malformed skill, and writing nothing.

#### Scenario: Stale region detected

- WHEN a dependency's source component changed after the host's last refresh
- THEN check exits nonzero naming the host skill

### Requirement: Marker parsing is fence-aware

Marker-shaped lines inside fenced code blocks SHALL be treated as literal text, not directives, in both refresh and check.

#### Scenario: Skill documenting the marker syntax

- WHEN a skill's body shows a START/STOP marker pair inside a fenced code block as an example
- THEN the tool neither parses it as a region nor counts it toward the one-region limit

### Requirement: Comment-terminator guard

The tool SHALL reject a declaration payload or generated region content containing the sequence `-->`, since it would terminate the HTML comment marker early or corrupt region boundaries.

#### Scenario: Dependency body containing the terminator

- WHEN a dependency's component contains `-->` outside a context the tool can safely emit
- THEN refresh exits with an error naming the dependency and the offending content
