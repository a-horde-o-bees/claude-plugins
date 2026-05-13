# Rebuild

> Workflow component for the rebuild skill. Three-agent orchestration: extract, compose, verify. Each agent runs in an isolated spawned context so the rebuild composes free of the orchestrator's session history and the agent's own prior reads. The orchestrator never reads `{artifact}` directly — only the agents do, each in their own scoped context.

### Variables

- {artifact} — file path, section heading, function, frontmatter field, or other addressable scope named by the user

### Rules

- Identity = scope + role + callable surface + declared rules + accumulated edge-case knowledge. Form changes; function doesn't.
- Spawn isolation is load-bearing — the orchestrator never reads `{artifact}`'s content; the composer never receives a path to the original. Mechanical, not advisory.
- Verifier reports findings; orchestrator triages them. Identity defects halt; structural changes gate on user; observations surface and proceed.
- Empty diff is a no-op.
- `_rubric.md` is loaded in unison by the composer and the verifier — patterns apply together, not as sequential waves.

### Process

1. If {artifact} is ambiguous (multiple files match, scope unclear, target doesn't resolve uniquely): Exit to user — present candidate interpretations as Q# with lettered options; ask which to rebuild.

2. {workspace}: `tmp/rebuild-workspace`
3. {basename}: filename portion of {artifact}
4. {extract-path}: `{workspace}/{basename}.extract.md`
5. {compose-path}: `{workspace}/{basename}.fresh`

6. bash: `mkdir -p {workspace}`

7. Spawn:
    1. Call: `_extract.md` ({artifact}: {artifact}, {extract-path}: {extract-path})
    2. Return to caller: one-line confirmation that {extract-path} was written

8. Spawn:
    1. Call: `_compose.md` ({extract-path}: {extract-path}, {compose-path}: {compose-path})
    2. Return to caller: one-line confirmation that {compose-path} was written

9. {verification}: Spawn:
    1. Call: `_verify.md` ({original-path}: {artifact}, {compose-path}: {compose-path}, {extract-path}: {extract-path})
    2. Return to caller: the structured verification report

10. If identity defects in {verification} are non-empty:
    1. {retry-compose}: Spawn:
        1. Call: `_compose.md` ({extract-path}: {extract-path}, {compose-path}: {compose-path}, {corrective-guidance}: identity-defect entries from {verification})
        2. Return to caller: one-line confirmation that {compose-path} was rewritten
    2. {verification}: Spawn:
        1. Call: `_verify.md` ({original-path}: {artifact}, {compose-path}: {compose-path}, {extract-path}: {extract-path})
        2. Return to caller: the structured verification report

11. Triage {verification}:
    1. If diff summary is empty: Exit to user — "{artifact} already conforms to its declared discipline; no rebuild needed."
    2. If identity defects are still non-empty after the retry: Exit to user — present both pre-retry and post-retry defects verbatim; recommend understanding the spec gap or composer drift before re-invoking. Do not write.
    3. If structural changes are non-empty: Exit to user — present structural changes; gate on user approval. If approved, proceed; if not, exit without writing.
    4. Else: proceed with observations to surface in the final report.

12. bash: `cp {compose-path} {artifact}`

13. Return to caller:
    - Artifact rebuilt: {artifact}
    - Structural changes: list (empty when only inline changes were made)
    - Observations: from verification report
    - Retry occurred: yes/no — note when the retry path fired
    - Workspace retained at: {workspace} — clear manually if no longer needed
    - <rebuild-complete>

14. Error Handling:
    1. If any spawned agent fails to produce its output file: Exit to user — name which phase failed, show the agent's return message, retain workspace for inspection
    2. If triage exits at step 11.2 or 11.3: workspace is retained at {workspace} for inspection; no cleanup
