# Worktree isolation leaks to main

Agents spawned with `isolation: "worktree"` sometimes write files to the main working tree instead of the worktree checkout. The worktree then appears empty and is auto-cleaned, while the changes persist on main. This defeats the isolation purpose — concurrent agents can conflict, and the orchestrator cannot review or merge worktree changes independently.

## Observed behavior

6 agents spawned with `isolation: "worktree"`. 2 correctly wrote to their worktrees (uncommitted changes present, worktrees survived cleanup). 4 wrote to the main working tree instead — worktrees were auto-cleaned as empty, but new/modified/deleted files appeared on main.

## Impact

- Concurrent agents can clobber each other's work on main
- Orchestrator cannot selectively merge or reject worktree results
- Partial or failed decompositions leak to main and must be manually reverted
- No predictable way to know which agents will respect worktree isolation

## Suspected root cause

Unknown. May be a Claude Code runtime issue with how worktree paths are communicated to agents, or agents may resolve paths from environment variables that point to the main working tree rather than the worktree checkout.
