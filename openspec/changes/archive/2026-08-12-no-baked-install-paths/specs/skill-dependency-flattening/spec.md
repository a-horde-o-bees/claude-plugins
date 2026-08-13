# skill-dependency-flattening Delta

## MODIFIED Requirements

### Requirement: Non-skill host files

Any markdown file MAY be a flatten host. Hosts are declared in `settings.skill-authoring.json` under a `hosts` list, read from the user scope (`~/.claude/`) and the project scope (the nearest `.claude/` directory at or above the working directory), unioned and deduplicated by resolved path; relative project entries resolve against the project root. Declared hosts SHALL join every invocation that targets the running tool's own suite root, with no per-invocation naming; invocations targeting other paths process only what they name. An explicit host argument or `--skills-root` override remains available. A host that is not a sibling skill of its suite is durable and dispatcher-less: no runtime binds `${CLAUDE_SKILL_DIR}` there, and an absolute path baked at build time rots when a plugin install is superseded. The tool SHALL therefore refuse to inline a unit containing `${CLAUDE_SKILL_DIR}` into a non-skill host, erroring with the dependency's name and writing nothing. All other behavior — reference verification and linking, section placement, topological ordering, the link check, and freshness checking — applies to hosts unchanged.

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
- THEN the tool exits with an error naming the dependency and the host, and writes nothing
