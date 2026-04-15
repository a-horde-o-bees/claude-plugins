# Worktree Isolation

Spawn an agent into a disposable git worktree for safe execution of state-modifying operations. The agent operates on an isolated branch — all file changes, commits, and skill invocations stay contained without affecting the main working tree. Structural containment, not instruction-based — the agent cannot accidentally modify main because it physically works in a separate checkout.

## Pattern

```
1. Block git push — bash: `git config remote.origin.pushurl "file:///dev/null"`
2. Spawn agent with isolation: "worktree":
    1. Execute operations in worktree
    2. Observe results
    3. Return to caller:
        - Findings, output, or observations
3. Unblock git push — bash: `git config --unset remote.origin.pushurl`
4. Process returned results
5. Worktree auto-cleans if agent made no changes; otherwise path and branch are returned
```

## Agent Capabilities

Tested empirically (2026-04-12). Worktree agents have access to most tools with one critical exception.

| Category | Available | Notes |
|---|---|---|
| Built-in tools | Yes | Bash, Read, Write, Edit, Glob, Grep, ScheduleWakeup |
| ToolSearch | Yes | Can load deferred tools on demand |
| MCP tools | Yes | Server-based; navigator, blueprint, OAuth connectors all reachable |
| Skill tool | Yes | Can invoke skills natively; skill runs inside worktree context |
| LSP, WebFetch, WebSearch | Yes | Via ToolSearch |
| TaskCreate/Update | Yes | Via ToolSearch |
| **Agent tool** | **No** | Cannot spawn sub-agents from within a worktree |

## Containment Properties

- **Branch isolation** — agent runs on `worktree-agent-{id}` branch, not main
- **File isolation** — all reads and writes happen in `.claude/worktrees/agent-{id}/`
- **Commit isolation** — commits land on the worktree branch only; main HEAD is unaffected
- **Skill isolation** — skills invoked via Skill tool execute entirely within the worktree
- **MCP isolation** — MCP servers are reachable but operate on worktree file paths
- **No sub-agent spawning** — Agent tool is unavailable; agent must do all work itself, including steps that would normally be delegated via `Spawn agent with:`

## What Is NOT Contained

- **Remote operations** — `git push` from a worktree still reaches the remote unless push is blocked (see Push Blocking section)
- **External APIs** — HTTP calls, webhook triggers, and other network operations execute normally
- **MCP write operations** — MCP servers that write to shared databases (not the worktree filesystem) affect real state

## When to Use

- Exercising skill pathways to verify behavior matches documentation
- Running state-modifying operations in a safe sandbox
- Testing CLI tools that produce observable output for comparison against claims
- Any evaluation that needs runtime evidence without risking the working tree

## When Not to Use

- Read-only analysis (static evaluation, conformity checking) — worktree overhead is unnecessary
- Operations requiring sub-agent delegation — Agent tool is unavailable in worktrees
- Operations that must actually reach a remote — push blocking makes the worktree a dead end for remote interaction

## Handling Limitations

### No Agent Tool

When skill workflows contain `Spawn agent with:` steps, the worktree agent executes those steps itself rather than delegating. Pre-instruct the agent: "Execute all agent-spawn steps yourself within your own context rather than delegating."

### User Interaction Gates

Skills with `Exit to user` or `AskUserQuestion` path gates represent branching routes. Two strategies:

- **Path gate** (user choice determines which workflow branch executes) — spawn separate worktree agents, one per branch, each pre-loaded with the "user's answer" for that path
- **Terminal interaction** (exit on completion or error) — agent records what would have been presented and continues evaluation

### Push Blocking

The skill executor blocks push globally before spawning worktree agents and unblocks after all agents return. This is skill-executor-controlled — the worktree agent does not need to do anything.

```
1. Block git push — bash: `git config remote.origin.pushurl "file:///dev/null"`
2. Spawn worktree agents
3. Unblock git push — bash: `git config --unset remote.origin.pushurl`
```

Any `git push` attempt while blocked fails loudly with `fatal: '/dev/null' does not appear to be a git repository` — expected safety behavior, not an error. The worktree agent should expect push failures and record them as "push blocked by worktree isolation" rather than investigating or working around them.

Push is blocked globally (main repo and all worktrees) for the duration of the evaluation. Since the skill executor waits for all agents before unblocking, this does not interfere with normal workflow.

One edge case: the agent could add a new remote and push to it. Low risk since skills reference `origin`, but workflows that add remotes would bypass the block.

Why skill-executor-controlled: `git config --worktree` resolves scope from the current working directory. Worktree agents' Bash tools may not always run from the linked worktree path, causing `--worktree` to write to the main worktree's config instead of the linked worktree's. Skill-executor-controlled global blocking avoids this CWD sensitivity entirely.

### Loop and Infinite Recursion

Skills with convergence loops or recursive patterns risk unbounded execution. Instruct the agent with explicit bail criteria: iteration cap, or exit when recognizing repeated state.
