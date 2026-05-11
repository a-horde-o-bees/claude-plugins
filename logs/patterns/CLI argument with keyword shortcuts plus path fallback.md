---
log-role: reference
---

# CLI argument with keyword shortcuts plus path fallback

An argument shape for CLI verbs where the value usually means one of two or three common things, but occasionally needs to be an arbitrary path. Accept `keyword` for the common cases AND any other value treated as a path. The keyword forms stay the easy default; the path form unlocks flexibility without forking the API.

## When to use

- A CLI argument has two or three canonical "modes" plus a long-tail "anything else" case.
- Splitting into `--mode <a|b>` + `--path <p>` would create awkward mutual exclusion.
- Most invocations are the easy cases; the path form is the escape hatch.

## Pattern

Argument definition:

- Drop `choices=...` constraints.
- Accept any string.
- Resolution function checks for known keywords first, falls back to treating the value as a path:

```python
def resolve(value: str, project_root: Path) -> Path:
    if value == "<keyword-a>":
        return <keyword-a-resolved>
    if value == "<keyword-b>":
        return <keyword-b-resolved>
    path = Path(value)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()
```

Help text names all three forms; documentation gives an example of the path case.

## Pitfalls

- Keyword names that could plausibly be paths. Pick keywords that wouldn't accidentally exist as a real path (`user`, `project` are safe; `lib` or `bin` might collide).
- Forgetting that relative paths need an anchor. Pick the anchor deliberately (project root vs cwd vs caller-supplied).

## Anti-patterns

- `--mode <a|b>` plus separate `--path <p>` with mutex logic — two flags for one decision.
- `--keyword-or-path` snake-case naming that telegraphs the implementation choice — the user shouldn't have to understand the resolution to use it.

## Worked example

`progressive-skill-composer`'s `--destination` accepts `user`, `project`, or any path:

```
compose new --destination user                              # ~/.claude/skills/
compose new --destination project                           # <project>/.claude/skills/
compose new --destination plugins/composed-skills/skills    # <project>/plugins/composed-skills/skills/
compose new --destination /tmp/scratch-skills               # /tmp/scratch-skills/
```

See `logs/decision/progressive-skill-composer.md` § *Destination forms — user, project, or any path* for the design discussion.
