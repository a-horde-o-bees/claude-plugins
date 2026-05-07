# Hook-registered file renames

Plugin-development concern: how to rename a file that's registered as a hook command in `.claude/settings.json` without locking the project out of further edits.

## The lockout

Files registered as hook commands have a soft coupling to their path — the command string is resolved at invocation time, and a dangling reference blocks every tool call whose matcher fires the hook. Renaming a hook file before updating its registration triggers a chicken-and-egg lockout: the Edit that would fix `settings.json` is itself blocked by the stale hook.

## Correct order

Update the registration first, then rename:

1. Edit `.claude/settings.json` to reference the new filename
2. Rename the hook file

## Recovery when already locked out

Restore the old path as a symlink or copy (`ln -s <new> <old>` or `cp`), update `settings.json`, then remove the temporary.

## Scope

Same discipline applies to any file path baked into `settings.json` — commands, MCP server entries, anything resolved at tool-call time.
