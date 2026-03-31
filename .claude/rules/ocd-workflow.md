# Workflow

How to operate in this project. Project-specific patterns implementing design principles.

## Working Directory

Working directory must remain project root for the entire session. Use absolute paths or tool flags instead of changing directories.

- No `cd`, `pushd`, `popd` — use `git -C <path>` for submodule operations
- Use relative paths from project root for `.claude/` scripts
- Compound commands (`&&`, `||`, `;`, `|`) are supported — each part checked independently against approval patterns

## Agents

- Minimize agent count — each agent independently loads context and rediscovers project; default to single agent processing tasks sequentially within one context
- Agents inherit tools and permissions from settings.json

## Testing

- Run only tests directly affected by current changes, scoped to narrowest relevant test file
- Run broader suites only when explicitly requested

## Decisions

Record in `decisions/` when alternatives were considered and rejected, or when reasoning is not derivable from code or conventions. Each decision file follows the structure:

- **Context** — what problem or question prompted the decision
- **Options Considered** — alternatives evaluated with trade-offs
- **Decision** — what was chosen and why
- **Consequences** — what this enables, constrains, and how to mitigate risks

Do not record implementation details, choices dictated by convention, or standard patterns obvious from reading code. Update existing files when direction changes — reorganize to reflect current understanding, do not append conflicting entries. Remove decision files when the decision is no longer relevant — superseded by a newer decision, or the code it governed no longer exists.

## Conventions

Check conventions before creating or modifying files:

```
python3 $(cat .claude/ocd/.plugin_root)/run.py skills.conventions list-matching <file> [<file> ...]
```

Pass all target file paths in a single call. If output is non-empty, read and follow returned convention files before proceeding.

## Naming

- Skill frontmatter `name` field uses plugin-name prefix — `ocd-navigator` not `navigator`; surfaces plugin name during search

## Package Structure

All packages (skills, plugin infrastructure) use standard Python entry points:
- `__main__.py` — agent-facing CLI; invoked via `python3 run.py <package> <command>`
- `__init__.py` — facade; public interface that `__main__.py` imports via `from . import *`

Hook scripts are standalone modules invoked individually by hooks.json — no facade or `__main__.py`.

## Interpreter

- `python3` not `python` — explicit interpreter version
- No shebangs, no execute permissions — scripts are invoked via interpreter prefix
