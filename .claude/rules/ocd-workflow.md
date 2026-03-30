# Workflow

Execution discipline for agent task processing.

## Command Approval

Bash commands are governed by `.claude/settings.json` (project) and `~/.claude/settings.json` (user). Hooks enforce constraints that override approval — keep rules and settings in sync. Key constraints:

- Working directory must remain project root — no `cd`, `pushd`, `popd`; use absolute paths or tool flags (`git -C <path>`)
- Compound commands (`&&`, `||`, `;`, `|`) are supported — each part is checked independently against approval patterns; all parts must pass
- Use relative paths from project root for `.claude/` scripts; use `git -C <path>` for submodule operations

## Agents

- Minimize agent count — each agent independently loads context and rediscovers project, so fewer agents means less token overhead; default to single agent processing tasks sequentially within one context

## Testing

- Run only tests directly affected by current changes, scoped to narrowest relevant test file; run broader suites only when explicitly requested

## Decisions

- Record architectural decisions in `decisions/` when alternatives were considered and rejected, or when reasoning is not derivable from code or conventions
- Do not record implementation details, choices dictated by convention, or standard patterns obvious from reading code
- Update existing decision files when direction changes — reorganize to reflect current understanding, do not append conflicting entries

## Code Practices

- Never take a simple path that leaves a foundation unstable — determine the correct solution and execute it, even if it changes everything; shortcuts that avoid foundational fixes accumulate into increasingly fragile systems that cost more to fix later than they saved
