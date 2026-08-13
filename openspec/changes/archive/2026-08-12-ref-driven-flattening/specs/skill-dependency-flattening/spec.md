# skill-dependency-flattening Delta

## MODIFIED Requirements

### Requirement: Marker region

A SKILL.md SHALL contain at most one flatten region, delimited by a bare START line and a bare STOP line: `<!-- flatten-skills START -->` … `<!-- flatten-skills STOP -->`. The region SHALL live inside a `## Dependencies` section positioned as the last section of the body; hand-authored content between the heading and the START line is source. Everything between the marker lines is generated content; the source layer of the file is everything outside the region plus the marker lines themselves.

#### Scenario: Source view survives region stripping

- WHEN the content between START and STOP is deleted
- THEN the file remains valid source and a refresh reconstitutes the region from the source layer's references

#### Scenario: Multiple regions rejected

- WHEN a SKILL.md contains more than one START/STOP region
- THEN the tool exits with an error identifying the file

#### Scenario: Payload-bearing START line rejected

- WHEN a START line carries any payload after `START` (including the retired JSON form)
- THEN the tool exits with an error identifying the file as malformed

### Requirement: Refresh regenerates the whole region

Refresh SHALL first build the dependency graph across all processed skills from their references, then rewrite each region in full: the flat, deduplicated transitive closure of the declaring skill's dependencies, each unit appearing exactly once. Units SHALL be ordered topologically — every unit precedes every unit it references, with ties broken by order of first reference appearance in the host source — so a reader always finds referenced content further down. Refresh keeps no incremental state; every run regenerates every region from source layers alone, so refresh is idempotent and order-independent.

#### Scenario: Shared transitive dependency deduplicated

- WHEN skill A references B and C, and both B and C depend on D
- THEN A's region contains B, C, and D once each, with D below both B and C

#### Scenario: Dependent ordered above its dependency regardless of appearance order

- WHEN skill A references /b before /a in its prose, and skill a depends on b
- THEN A's region emits the a unit above the b unit

#### Scenario: Circular dependency

- WHEN the dependency graph contains a cycle
- THEN the tool exits with an error naming the cycle, and writes no regions

### Requirement: Component extraction

A dependency's component SHALL be its SKILL.md minus frontmatter and minus its entire `## Dependencies` section — heading, hand-authored reference list, and marker region. The dependency relationships the section declares are realized by the host's closure itself; extraction never reads another skill's generated content as input.

#### Scenario: Dependent-of-dependent extraction

- WHEN skill A references B, and B's SKILL.md carries a `## Dependencies` section with an ambient list and a materialized region
- THEN the B unit inlined into A contains neither B's Dependencies heading nor its list nor its region, and B's dependencies enter A's region as separate deduplicated units

### Requirement: Freshness check

A check mode SHALL recompute every file from its source layer and byte-compare against disk, exiting nonzero and naming each stale or malformed skill, and writing nothing. Staleness includes an outdated region body, a `## Dependencies` section that is not the last section, a missing section when references exist, and an unlinked bare reference.

#### Scenario: Stale region detected

- WHEN a dependency's source component changed after the host's last refresh
- THEN check exits nonzero naming the host skill

#### Scenario: Hand drift detected

- WHEN an author adds a bare `/skill-name` reference or a section after `## Dependencies` without running refresh
- THEN check exits nonzero naming the host skill

## REMOVED Requirements

### Requirement: JSON declaration

**Reason**: The JSON payload was a second declaration surface that could drift from the prose that motivates each dependency; references in the source layer are now the single declaration form.

**Migration**: The one-time suite pass strips START payloads to the bare form and authors the references; the tool carries no parser for the retired payload — a payload-bearing START line is simply malformed. Ambient dependencies with no natural prose site are listed as reference list items under `## Dependencies` above the START marker.

## ADDED Requirements

### Requirement: Reference-derived declaration

The tool SHALL derive a skill's dependencies from `/skill-name` references in its source layer: any slash-prefixed token outside fenced code blocks that names a sibling skill folder. References to the skill's own name (its invocation surface) SHALL NOT declare a dependency. A reference already wrapped as a markdown link counts identically to a bare one.

#### Scenario: Scoped reference in prose

- WHEN a host's source says "Apply /concise-prose to the commit summaries" and concise-prose is a sibling skill
- THEN concise-prose enters the host's dependency closure

#### Scenario: Ambient reference as list item

- WHEN a host lists `- /markdown-authoring` under `## Dependencies` above the START marker
- THEN markdown-authoring enters the closure with no prose site required

#### Scenario: Self-invocation surface exempt

- WHEN the git skill's source says "Bare `/git` lists the verbs"
- THEN no dependency on git is declared and the reference is left unlinked

### Requirement: Reference linking

Refresh SHALL rewrite every dependency-declaring reference in the source layer to an in-file anchor link whose text preserves the slash form — `[/skill-name](#skill-name)` — targeting the unit's demoted title heading. The rewrite SHALL be convergent: already-linked references are left unchanged, so refresh remains idempotent. References inside inlined units to skills present in the same closure SHALL be rewritten the same way during emission.

#### Scenario: Bare reference linked on refresh

- WHEN a host's source contains a bare `Apply /concise-prose to summaries`
- THEN after refresh the source reads `Apply [/concise-prose](#concise-prose) to summaries` and a second refresh changes nothing

#### Scenario: Unit-internal reference resolves in host

- WHEN an inlined dependency's own body references another skill in the closure
- THEN the emitted unit links that reference to the sibling unit's anchor in the same file

### Requirement: Dependencies section placement

When a skill's source layer contains dependency-declaring references, refresh SHALL ensure a `## Dependencies` section exists containing the marker region, appending the section at end of file when missing and relocating it to the end when other sections follow it. Hand-authored content between the heading and the START marker SHALL be preserved as source.

#### Scenario: Section appended for a first reference

- WHEN an author adds `Apply /concise-prose …` to a skill with no flatten region
- THEN refresh appends `## Dependencies` with a populated marker region at end of file

#### Scenario: Section relocated to end

- WHEN `## Dependencies` is followed by another H2 section
- THEN refresh moves the entire section (hand content and region) to end of file, leaving other sections' relative order unchanged

### Requirement: Post-materialization link check

After computing a file, the tool SHALL verify that every rewritten anchor resolves to a heading present in the materialized file, and SHALL treat any unresolved `/name`-shaped reference outside fences and self-invocation surfaces as an error, naming the file and the reference. Nothing is written when any file errors.

#### Scenario: Typo'd reference caught

- WHEN a host references `/concise-pros` and no such sibling skill exists
- THEN the tool exits with an error naming the host and the unresolved reference

#### Scenario: Dead anchor caught

- WHEN a linked reference targets an anchor no heading in the materialized file produces
- THEN the tool exits with an error naming the host and the link
