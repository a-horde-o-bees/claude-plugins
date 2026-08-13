# skill-dependency-flattening Delta

## ADDED Requirements

### Requirement: Non-skill host files

Any markdown file MAY be a flatten host when the invocation supplies an explicit skills root for reference resolution. For a host that is not itself a sibling skill of that root, `${CLAUDE_SKILL_DIR}` occurrences in inlined units SHALL be rewritten to the absolute path of the dependency's folder under the skills root, since no dispatcher binds the variable outside a skill invocation. All other behavior — reference verification and linking, section placement, topological ordering, the link check, and freshness checking — applies to non-skill hosts unchanged.

#### Scenario: User CLAUDE.md as host

- WHEN `~/.claude/CLAUDE.md` references /confirm-shared-intent and the tool runs with the skills root supplied
- THEN the reference is linked, the unit is materialized under a `## Dependencies` section at end of file, and check mode reports the file stale when the skill's source changes

#### Scenario: Bundled-file reference in a unit inlined outside the suite

- WHEN a dependency's body references `${CLAUDE_SKILL_DIR}/scripts/tool.py` and the host is not a skill
- THEN the materialized unit references the absolute path `<skills-root>/<dependency>/scripts/tool.py`
