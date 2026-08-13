# skill-dependency-flattening Specification

## Purpose
Deterministic build-time composition of skills: a skill declares dependencies on sibling skills, and a flatten tool materializes their full bodies into a marker-delimited generated region inside its SKILL.md, so the loaded skill never relies on model-mediated invocation or runtime preprocessing to see the text it depends on.
## Requirements
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

A check mode SHALL recompute every file from its source layer and byte-compare against disk, exiting nonzero and naming each stale or malformed skill, and writing nothing. Staleness includes an outdated region body, a `## Dependencies` section that is not the last section, a missing section when references exist, and an unlinked bare reference.

#### Scenario: Stale region detected

- WHEN a dependency's source component changed after the host's last refresh
- THEN check exits nonzero naming the host skill

#### Scenario: Hand drift detected

- WHEN an author adds a bare `/skill-name` reference or a section after `## Dependencies` without running refresh
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

### Requirement: Non-skill host files

Any markdown file MAY be a flatten host. Hosts are declared in `settings.skill-authoring.json` under a `hosts` list, read from the user scope (`~/.claude/`) and the project scope (the nearest `.claude/` directory at or above the working directory), unioned and deduplicated by resolved path; relative project entries resolve against the project root. Declared hosts SHALL join every invocation that targets the running tool's own suite root, with no per-invocation naming; invocations targeting other paths process only what they name. An explicit host argument or `--skills-root` override remains available. For a host that is not a sibling skill of its suite, `${CLAUDE_SKILL_DIR}` occurrences in inlined units SHALL be rewritten to the absolute path of the dependency's folder, since no dispatcher binds the variable outside a skill invocation. All other behavior — reference verification and linking, section placement, topological ordering, the link check, and freshness checking — applies to hosts unchanged.

#### Scenario: User CLAUDE.md as host

- WHEN `~/.claude/CLAUDE.md` references /confirm-shared-intent and a suite-scoped invocation runs
- THEN the reference is linked, the unit is materialized under a `## Dependencies` section at end of file, and check mode reports the file stale when the skill's source changes

#### Scenario: Registered host rides every suite gate

- WHEN `~/.claude/settings.skill-authoring.json` lists the user CLAUDE.md under `hosts` and any gate runs refresh or check against the suite root
- THEN the CLAUDE.md is processed with the suite's skills as reference targets, and a stale copy fails check with no flag passed

#### Scenario: Targeted invocation stays targeted

- WHEN the tool runs against a fixture directory or a single named file
- THEN no settings-declared host is touched

#### Scenario: Duplicate declarations collapse

- WHEN the same host appears in both the user and project settings files
- THEN it is processed exactly once

#### Scenario: Bundled-file reference in a unit inlined outside the suite

- WHEN a dependency's body references `${CLAUDE_SKILL_DIR}/scripts/tool.py` and the host is not a skill
- THEN the materialized unit references the absolute path `<skills-root>/<dependency>/scripts/tool.py`

