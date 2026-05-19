# `cd` in Bash invocations persists CWD across calls

## What happened

Used `cd /home/dev/.claude/projects/-home-dev-projects-claude-plugins/memory && ls && rm -f *.md && ls` to clean up memory files. The `cd` succeeded; the rm worked. But subsequent Bash and Write calls from this session inherited the changed CWD.

When the next Write tool call fired (wiping CLAUDE.md), its PreToolUse hook at `.claude/hooks/guard_derived.py` failed:

```
PreToolUse:Write hook error: [python3 .claude/hooks/guard_derived.py]:
python3: can't open file '/home/dev/.claude/projects/-home-dev-projects-claude-plugins/memory/.claude/hooks/guard_derived.py':
[Errno 2] No such file or directory
```

The hook command resolves `.claude/hooks/guard_derived.py` relative to the bash CWD. The `cd` from the prior call had made CWD the memory dir, so the relative path resolved into the wrong location.

## Why this matters

- The harness's tool description explicitly says: "The working directory persists between commands, but shell state does not." Easy to forget the persistence applies to CWD.
- Project hooks frequently use relative paths assuming CWD = project root. Any `cd` away breaks them silently until the next hook fires.
- The error message points at a file path that looks like a different error (missing script) rather than the actual cause (wrong CWD).

## How to apply

- **Never use `cd` in Bash invocations.** Use absolute paths instead, regardless of how much shorter the relative path would be.
- When a tool batch needs many ops in one directory, prefix each with the full path rather than `cd && op1 && op2`.
- If a hook fails with a path that looks weirdly nested, suspect CWD drift first.

## Recovery

`cd /home/dev/projects/claude-plugins && pwd` to confirm restoration. Subsequent calls then work as expected.

## Related

- The principle was previously captured in `feedback_no_cd_in_bash.md` (user memory, deleted this session as part of memory cleanup). The lesson stands even though the memory file is gone — this log preserves it in project scope.
- Bash tool docs in the harness system prompt: "Try to maintain your current working directory throughout the session by using absolute paths and avoiding usage of `cd`."
