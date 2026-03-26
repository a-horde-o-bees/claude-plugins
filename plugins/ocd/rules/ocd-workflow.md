---
type: template
---

# Workflow

Execution discipline for agent task processing.

## Command Approval

Bash commands are governed by `.claude/settings.json` (project) and `~/.claude/settings.json` (user). Hooks enforce constraints that override approval — keep rules and settings in sync. Key constraints:

- Working directory must remain project root — no `cd`, `pushd`, `popd`; use absolute paths or tool flags (`git -C <path>`)
- Single-command Bash calls only — no `&&`, `||`, `;`, `|`; compound commands bypass approval pattern matching
- Use relative paths from project root for `.claude/` scripts; use `git -C <path>` for submodule operations

## Agents

- Minimize agent count — each agent independently loads context and rediscovers project, so fewer agents means less token overhead; default to single agent processing tasks sequentially within one context; multiple agents require explicit user direction or permission
- After all file-modifying agents complete, run `git diff` to review changes before presenting results to user

## Testing

- Run only tests directly affected by current changes, scoped to narrowest relevant test file; run broader suites only when explicitly requested
- Run integration tests only when user explicitly requests it

## Decisions

- Record architectural decisions in `decisions/` when alternatives were considered and rejected, or when reasoning is not derivable from code or conventions
- Do not record implementation details, choices dictated by convention, or standard patterns obvious from reading code
- Update existing decision files when direction changes — reorganize to reflect current understanding, do not append conflicting entries

## Code Practices

- Before writing new functions, check whether codebase already provides what is needed — do not duplicate existing functionality or bypass library abstractions with ad-hoc implementations
- Verify assumptions before building on them — test with minimal calls, inspect actual responses, confirm data shapes before writing transform logic
