# Phase A research-migration agent

You are processing a batch of sample-file paths as part of Phase A of the research-corpus retrofit. Each batch contains 1+ absolute paths under `logs/research/<subject>/samples/`. For each file you read it, understand it, rewrite it cleanly, and accumulate per-section semantic observations across the batch. Both deliverables go in the YAML reply.

This is **not** a regex pass. The mechanical bullet-to-subheading conversion was tried and produced shallow observations that don't help template design. This time the agent reads the section's substance, decides what sub-purpose it really conveys, writes a clean version, and records what the section seems to be *about* across the batch.

## Per-file rewrite

> **Path discipline.** All paths in the batch are absolute paths. Pass them verbatim to Read and Write. Cwd may be a different worktree on a different branch — relative-path interpretation would write to the wrong tree.

For each path:

1. **Read the entire file.** No partial reads.

2. **Identify each level-2 section's substance.** For each `## <section>` block, determine what sub-purposes it actually conveys for *this* repo — not what label happened to be used. A section may have:
    - Stable sub-purposes shared across the corpus (e.g. "language(s) + version constraints", "framework/SDK in use" under section 1)
    - Open enumeration (e.g. section 10 lists whatever hosts the README mentions)
    - Freeform observations (e.g. section 17 "notable structural choices" — whatever stood out)

3. **Rewrite the file from scratch.** Use Write with the full new contents. Shape:

    ```markdown
    # Sample

    ## <Section>
    ### <sub-purpose>

    <Paragraph or short prose. Concrete content; no padding. Preserve facts faithfully — do not invent or smooth over gaps.>

    ### <sub-purpose>

    <Content.>
    ```

    Rules for rewriting:
    - Level-1 heading is always `# Sample` (so `consolidate_section` can aggregate cross-sample by section).
    - Section headings are exactly the canonical names in the existing file (don't invent new sections; if a section is absent from the source, leave it absent).
    - Sub-purpose headings (`###`) reflect **what the content is about**, not the verbatim label the original used. Use short, canonical names — see *Canonical sub-purpose names* below.
    - Where the section is open enumeration (e.g. host integrations), use one `### <thing>` per item the source enumerated, with the supporting detail as paragraph content.
    - Where the section is freeform, omit `###` subheadings and write the observations as paragraphs (or a bulleted list when that's clearly the source's intent). Don't manufacture sub-purposes that aren't there.
    - Preserve "none noted in this repo" / "not captured" / "N/A" answers verbatim — those are signal, not absence.
    - Code blocks, inline code, links: preserve verbatim from source where they appear.
    - **Do not invent content.** If the source said "not captured", rewrite as "not captured". If a sub-purpose is absent, omit the `###` heading.
    - **Strip meta-instruction scaffolding.** Some sources contain the original prompt-template's instruction text (paragraphs describing what the section "should contain", "for each X encountered" preambles, bracketed editorial notes). These are scaffolding from when the sample was authored — strip them. Keep only concrete content about *this repo*.
    - **Consolidate source-split sub-purposes when they're not canonical.** If a source split a single canonical sub-purpose into multiple non-canonical ones (e.g. section 16 split into `### dirs`, `### config`, `### additional`, `### documentation`), consolidate into the canonical paragraph and note the split in `issues` for that section. Don't preserve the non-canonical split.
    - **Relocate cross-section content contamination.** Some sources put content from one section into another's `pitfalls observed` block (e.g. layout commentary in section-3 pitfalls, axis observations in section-13 pitfalls). When a `pitfalls observed` answer is clearly content for a different section, move it to the section it belongs to and replace the original slot with the actual pitfall (if one exists in the surrounding text) or with `none noted in this repo`. Note the relocation in the file's `notes` field.
    - **Drop within-file duplication.** When a `pitfalls observed` slot restates content already in section 20 (Gaps) or another section of the same file, replace it with `none noted in this repo` rather than preserving the duplicate. The Gap or sibling-section copy stays. Note the dedup in the file's `notes` field.

4. **Move on.** Do not re-read or re-verify after writing.

## Canonical sub-purpose names

When rewriting, prefer short canonical labels over long parenthesized variants. The existing corpus uses both forms (e.g. "how selected" vs "how selected (flag, env, separate entry, auto-detect, etc.)"). Pick the short canonical form. Below is the canonical set discovered so far per section — use these names for cross-sample consistency:

- **Identification**: `url`, `stars`, `last-commit`, `license`, `default branch`, `one-line purpose`
- **1. Language and runtime**: `language(s) + version constraints`, `framework/SDK in use`, `pitfalls observed`
- **2. Transport**: `supported transports`, `how selected`, `pitfalls observed`
- **3. Distribution**: `every mechanism observed`, `published package name(s)`, `install commands shown in README`, `pitfalls observed`
- **4. Entry point / launch**: `command(s) users/hosts run`, `wrapper scripts, launchers, stubs`, `pitfalls observed`
- **5. Configuration surface**: `how config reaches the server`, `pitfalls observed`
- **6. Authentication**: `flow`, `where credentials come from`, `pitfalls observed`
- **7. Multi-tenancy**: `tenancy model`, `pitfalls observed`
- **8. Capabilities exposed**: `tools / resources / prompts / sampling / roots / logging / other`, `pitfalls observed`
- **9. Observability**: `logging destination + format, metrics, tracing, debug flags`, `pitfalls observed`
- **10. Host integrations shown in README or repo**: one `###` per host (e.g. `Claude Desktop`, `Claude Code`, `Cursor`, `VS Code`, `Smithery`, etc.), then `pitfalls observed`
- **11. Claude Code plugin wrapper**: `presence and shape`, `pitfalls observed`
- **12. Tests**: `presence, framework, location, notable patterns`, `pitfalls observed`
- **13. CI**: `presence, system, triggers, what it runs`, `pitfalls observed`
- **14. Container / packaging artifacts**: `Dockerfile, docker-compose, Helm, systemd, brew formula, etc.`, `pitfalls observed`
- **15. Example client / developer ergonomics**: `MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs`, `pitfalls observed`
- **16. Repo layout**: `single-package / monorepo / vendored / other`, `pitfalls observed`
- **17. Notable structural choices**: freeform — no `###` subheadings, write paragraphs
- **18. Unanticipated axes observed**: freeform unless the source clearly enumerates axes (then `### <axis name>` per axis)
- **19. Python-specific** (only present in Python repos): `SDK / framework variant`, `Python version floor`, `Packaging`, `Entry point`, `Install workflow expected of end users`, `Async and tool signatures`, `Type / schema strategy`, `Testing`, `Dev ergonomics`, `Notable Python-specific choices`
- **20. Gaps**: freeform — no `###` subheadings, write paragraphs

If the source has a sub-purpose not listed above, use a short canonical-style name and flag it as a new sub-purpose in the observations YAML.

## Per-batch observation accumulation

While reading and rewriting, accumulate semantic observations per section across the whole batch. For each section that appeared in the batch, record:

- `samples_in_batch` — how many of this batch's files contained the section
- `sub_purposes_seen` — the sub-purpose labels you used in your rewrites, with file counts
- `shape` — your assessment of the section's nature: `closed-set` (stable sub-purpose vocabulary across samples) | `open-enumeration` (varying items, no fixed vocabulary) | `freeform` (prose observations, no sub-purpose vocabulary)
- `common_description` — 1-3 sentences capturing what this section *is about* across the batch's samples. What's the shared question it's answering? What's the typical content?
- `outliers` — list of `{sample, why}` for samples whose content for this section diverged meaningfully from the rest of the batch
- `issues` — list of free-form notes when the section's structure suggests a problem worth flagging for template design (e.g. "pitfalls observed appears in every section but always says 'none' — consider folding into the section's primary content", or "host integrations is genuinely unbounded in vocabulary; modeling as `### per host` is fine but expect 30+ host names across the corpus")

The orchestrator merges observations across spawns; you only see your batch.

## Output

Return a single message containing one YAML block, then return:

```yaml
files_processed:
  - path: <absolute path>
    sections_present: [<list of level-2 section names rewritten>]
    notes: <optional 1-line note about anything unusual; omit if nothing>

section_observations:
  - subject: <subject>
    section: <section name verbatim, including the leading number for sections 1-20>
    samples_in_batch: <integer>
    sub_purposes_seen:
      <canonical sub-purpose label>: <count of files in batch using it>
    shape: closed-set | open-enumeration | freeform
    common_description: |
      <1-3 sentences>
    outliers:
      - sample: <basename>
        why: <one line>
    issues:
      - "<one-line note for template design>"
```

Omit `outliers` and `issues` lists when empty. Omit `sub_purposes_seen` for freeform sections. Per-section blocks for sections not present in any batch file are omitted.

## Rules

- **Read every file in full** — partial reads cause hallucinated content
- **Faithful rewrite** — preserve facts; do not invent, smooth over, or interpret beyond what the source supports
- **No verification re-runs** — do NOT re-read after Write to "check"; the orchestrator owns idempotency
- **Scope confinement** — only modify files listed in your batch; never touch other paths
- **Pure YAML reply** — no preamble, no summary prose, no commentary; the YAML block is the entire reply
