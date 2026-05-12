# Project Root Structure

Layout extensions specific to project root. Inherits the universal `system-structure` convention; adds workstream tracking, log curation, and project-only entry-point files. Subsystems do not adopt these — they belong only at the repository root.

## Forward-looking work tracking

The project root carries persistent workstream tracking on top of the universal system structure:

- `plans/` — strategy docs for active or upcoming workstreams. Each file describes goal, output, sequence of work, locked decisions, and open questions for one workstream. Persists across sessions; rewritten as the workstream evolves; deleted when the workstream resolves.
- `TASKS.md` — persistent task tracker at project root. Each entry links to a `plans/` file when context is non-trivial, or to a decision document when the task is awaiting input. Sections by status: in-progress, pending, upcoming, done.

`TASKS.md` is distinct from session-scoped tracking (e.g. `TaskCreate`). Those manage the current session's checklist; `TASKS.md` persists across sessions and survives context clears.

Plans are operational artifacts — operated on and disposed when the workstream completes — not log entries. They support `TASKS.md` and live alongside it at project root.

## Logs

Project-curated knowledge artifacts captured during work — `logs/<type>/` per the `log.md` rule. Types include `decision/`, `friction/`, `idea/`, `problem/`, `pattern/`, `research/`. Logs are project-root concerns; subsystems do not maintain their own log directories.

## Document separation extensions

In addition to the universal mappings in `system-structure`, project root adds:

| Content | Where it lives |
|---|---|
| Forward-looking strategy | `plans/<workstream>.md` |
| Active work tracking | `TASKS.md` |
| Decisions, friction, ideas, problems, patterns, research | `logs/<type>/` per the `log.md` rule |

## Filename case extensions

Project-root-only all-caps entry points (in addition to the three-document-model docs covered by `system-structure`):

- Persistent task tracker: `TASKS.md`
- Project-root community-health and planning conventions: `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `ROADMAP.md`, `MARKETPLACE-STANDARDS.md`

Project-root-only lowercase contents (in addition to the universal lowercase list in `system-structure`):

- Plan documents (`plans/<workstream>.md`)
- Log entries under `logs/<type>/` — content *of* the logs system
