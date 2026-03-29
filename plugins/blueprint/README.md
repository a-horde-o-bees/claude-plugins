# blueprint

Structured competitive research and implementation planning. Bootstraps new projects by studying comparable examples through four phases: scoping, deep research, analysis, and implementation blueprint.

## Dependencies

Requires the **ocd** plugin for agent-authoring rules and plugin infrastructure.

## Setup

```
/plugin install ocd
/plugin install blueprint
/ocd-init
/blueprint-init
```

Restart Claude session after init to load rules. Run `/ocd-status` to verify both plugins.

`/blueprint-init` deploys the agent-authoring rule and initializes the research database at `.claude/{plugin_name}/research/research.db`.

## Usage

```
/blueprint-research [scope description]
```

Optional scope description seeds Phase 1. Without arguments, skill detects state from `docs/blueprint.md` and proposes next phase.

## Phases

| Phase | Name | Type | What It Does |
|-------|------|------|------------|
| 1 | Scoping | Design | Define scope, assessment criteria, domain knowledge; discover and assess entities |
| 2 | Deep Research | Execution | Research each entity thoroughly; capture atomic notes in SQLite |
| 3 | Analysis | Execution | Cross-entity pattern analysis; derive measures; produce findings and interpretation |
| 4 | Implementation Blueprint | Design | Dependency-ordered implementation plan; hands off to progress tracking |

Design phases include refinement loops. Execution phases run sequential agents with checkpointing.

## Research Database

SQLite database tracks entities, notes, measures, provenance, and structured source data. All operations through `research` — agents never access the database directly.

Entity roles:
- **example** (default) -- comparable sites to study
- **directory** -- crawlable listings yielding examples
- **context** -- knowledge sources informing the project

## Optional: Browser Automation

For JavaScript-rendered directories and dynamic content, configure an MCP server:

```
claude mcp add playwright -- npx @playwright/mcp@latest
```

For concurrent browser sessions:

```
claude mcp add playwright-parallel -- npx playwright-parallel-mcp
```

## License

MIT
