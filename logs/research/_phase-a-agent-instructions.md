# Phase A research-migration agent

You are processing a batch of sample-file paths as part of Phase A of the research-corpus retrofit. Each batch contains 1+ file paths under `logs/research/<subject>/samples/`. For each file you restructure it in place (idempotent) and accumulate per-section observations across the batch. Return both at the end.

## Per-file restructuring (idempotent)

For each path in the batch:

> **Path discipline.** All paths in the batch are absolute paths. Pass them verbatim to Read, Edit, and Write. Do NOT interpret them as relative to cwd; do NOT translate or rewrite path prefixes. Cwd may be a different worktree on a different branch — relative-path interpretation would write to the wrong tree.

1. **Read the file once** at the absolute path given.

2. **Normalize level-1.** If the file's first heading line is `# <entity-id>` (any text other than `# Sample`), Edit it to `# Sample`. If already `# Sample`, skip.

3. **Convert bullet-with-colon items to subheadings.** Across every level-2 section, find every line of the form `- **<Name>**: <content>` (or the unbolded `- <name>: <content>` shape) and Edit each to:

    ```
    ### <Name>

    <content>
    ```

    Nested bullets that follow a converted line stay as content under the new subheading. If the section already contains `### ` subheadings (idempotent re-run), skip conversion in that section.

4. **Move on to the next file.** Do not re-read or re-verify after writing.

## Observation accumulation (across the batch)

While processing, record for each level-2 section observed in the batch:
- which subject the section belongs to
- the section name (level-2 heading text)
- how many of this batch's files contained the section
- the sub-purpose names (level-3 heading text after restructuring) and how many of this batch's files contained each
- structural anomalies worth flagging — e.g. malformed bullets that didn't match the conversion rule, sections with no bullets at all, samples with multiple level-1 headings, anything irregular

You're observing **only this batch's files**. The orchestrator merges observations across spawns.

## Output

Return a single message containing one YAML block, then return:

```yaml
files_processed:
  - path: logs/research/<subject>/samples/<entity>.md
    level1_normalized: true|false
    bullets_converted: <integer count>

section_observations:
  - subject: <subject>
    section: <section-name>
    samples_in_batch: <integer>
    sub_purposes:
      <name>: <integer count of files in batch with this sub-purpose>
    anomalies:
      - "<one-line observation>"
```

Sub-purposes whose count == 0 across the batch are omitted. The `anomalies` list is per section; omit when empty.

## Rules

- **Idempotency** — every transformation checks current state before modifying; running the same batch twice produces no further changes
- **Scope confinement** — only modify files listed in your batch; never touch other paths
- **No verification re-runs** — the orchestrator handles idempotency across batches; do NOT do a second pass to verify yourself
- **Pure YAML reply** — no preamble, no summary prose, no commentary; the YAML block is the entire reply
