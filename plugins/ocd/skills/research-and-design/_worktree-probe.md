# Worktree Probe

Pattern for validating a research assumption empirically — run a minimal prototype in an isolated git worktree against real project artifacts, observe the result. Replaces the mental-dry-run failure mode where theoretical designs survive review only because nothing was executed.

### Variables

- {assumption} — statement the probe tests (e.g., "ast.get_docstring reliably extracts docstrings from every .py file in the project")
- {session-id} — current research session identifier

## Pattern

```
1. Define the probe:
    1. Minimal script that exercises the assumption
    2. Clear pass/fail criterion (script output matches expectation, or an exception is raised, etc.)
    3. Realistic input drawn from actual project artifacts (not fabricated test cases)
2. Dispatch probe in a worktree:
    1. Spawn (isolation: "worktree"):
        1. Write the probe script under `/tmp/` in the worktree
        2. Execute the script against selected project artifacts
        3. Capture stdout, stderr, exit code, and any side effects
        4. Return:
            - Pass/fail verdict per criterion
            - Raw output excerpts
            - Unexpected observations worth reporting
3. Persist probe output:
    1. Write result to `${CLAUDE_PLUGIN_DATA}/research-and-design/{session-id}/probes/{assumption-id}.md`
    2. Include: probe script verbatim, output, verdict, timestamp
4. Reintegrate:
    1. Update {state-path} assumption entry with validation status and pointer
    2. If falsified: surface to user; may reopen related questions
```

## Push Blocking

Worktree isolation prevents modification of the main working tree but does not prevent pushes. Before any probe that could trigger git operations, block push on the worktree origin — the same mechanism `evaluate-skill` uses:

```bash
git -C {worktree-path} config remote.origin.pushurl "file:///dev/null"
```

Unblock after probe completes, successful or failed.

## Probe Kinds

### Capability probe

Tests whether a tool or API behaves as assumed. Example: run `ast.get_docstring(ast.parse(open(f).read()))` across every `.py` file in the project and count how many return empty strings — validates that ast parsing works for the corpus.

### Prompt probe

Tests whether an LLM prompt produces the expected shape of output against real input. Example: run the claim-extraction prompt against `lib/governance/architecture.md` and count how many claims are extracted, what types they are, and whether claim_text spans are actually substrings of input. Catches prompt drift before committing to the prompt in a skill.

### Integration probe

Tests end-to-end behavior of a proposed mechanism. Example: scaffold the discovery CLI as a stub that returns a hardcoded system DAG; verify the parent orchestrator reads it correctly. Isolates interface design from full implementation.

### Negative probe

Tests an assumption's failure path. Example: deliberately inject a file with unusual syntax into the corpus and verify the proposed skill degrades gracefully rather than crashing. Counters the positive-only evidence bias.

## Anti-Patterns to Reject

- Probes that don't actually run code ("read the source and conclude") — this is mental dry-run; not a probe
- Probes against fabricated data instead of real project artifacts — doesn't validate against reality
- Probes without clear pass/fail criteria — outcome is ambiguous
- Probes that could damage main working tree if they fail — always in a worktree

## Cleanup

Worktrees are ephemeral. The Cleanup step of the parent Workflow removes any worktree still open at end of session. Probe output persists under scratch; worktree itself does not.
