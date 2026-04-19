# Close

Park an open feature sandbox — remove the sibling worktree while preserving the `sandbox/<feature>` branch on origin. The feature can be re-activated later with `open`. Close refuses to proceed with uncommitted or unpushed work in the sibling; the push state is the trigger that distinguishes "ready for later resume" from "work at risk of loss."

### Variables

- {verb-arg} — positional value: feature id

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} is empty: Exit to user: close requires a feature id
    2. {feature-id} = {verb-arg}
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Preconditions — sibling must exist, be on the expected branch, be clean, and be pushed.

5. Verify preconditions:
    1. If {sibling-path} does not exist: Exit to user: no sibling worktree at {sibling-path} — nothing to close
    2. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
    3. If {status-json}.branch ≠ {branch}: Exit to user: sibling is on {status-json}.branch, expected {branch}
    4. If not {status-json}.clean: Exit to user: uncommitted changes in {sibling-path} — commit or stash before closing
    5. If not {status-json}.pushed: Exit to user: {branch} is ahead of origin — push before closing (`git -C {sibling-path} push origin {branch}`)

> Integration acknowledgment — close is where the user signals whether the branch is ready for unpack. Unpack is mechanically dumb; it merges dev into main as-is. All reintegration judgment must already be done on the branch.

6. Ask user about integration state:
    1. AskUserQuestion:
        - question: "Closing {branch}. What's this branch's state? Unpack will merge as-is; no integration happens at unpack time — so 'ready' must mean the integration work is already complete on this branch."
        - options:
            - "Ready for unpack" — description: "Rebased against latest main, all external references reintegrated against current conventions, verified to work. A subsequent unpack will merge cleanly without further work."
            - "Still in progress" — description: "Work or integration still pending. Branch persists for another open/close cycle; unpack would be premature."
            - "Cancel close" — description: "Abort close; sibling remains."
    2. If user selected "Cancel close": Exit to user: close cancelled — sibling remains at {sibling-path}
    3. {integration-state} = "Ready for unpack" or "Still in progress" depending on user's selection

> Remove the sibling worktree. Keep the branch — close is reversible via `open`.

7. Remove sibling worktree:
    1. bash: `ocd-run sandbox worktree-remove {sibling-name}`

8. Return to caller:
    - closed: {branch}
    - integration state: {integration-state}
    - branch persists on local and origin; re-activate with `/ocd:sandbox open {feature-id}`
