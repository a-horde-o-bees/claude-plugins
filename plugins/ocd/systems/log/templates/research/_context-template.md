# Context

Supporting information sources that inform a research subject — outside of examples of the target. Specs, SDK docs, blog posts, talks, papers, datasets, code references, discussion threads, transcripts — whatever sources contributed to the research's framing or evidence base.

## What Qualifies

- A source with information that shaped how the research interprets samples or framed the questions being asked.
- A reference that may need re-citation in `RESEARCH.md` or `ANALYSIS.md`.
- An external artifact that could move or disappear and is worth archiving locally so the research stays grounded if upstream changes.

## What Does Not Qualify

- Per-entity evidence that's an example of the research target → that's a sample, goes under `<subtopic>-samples/`.
- Working notes, hypotheses, or in-flight state from the researcher → research-wave files at the subject root, or directly in `RESEARCH.md` drafts.

## Free-Form Body

Context files are not template-structured. Different source types have different value shapes:

- A spec page — normative requirements and section IDs
- A blog post — arguments, framings, quoted positions
- A talk — timestamps, slides, demo points
- A paper — methodology, findings, citations
- A dataset — shape, distribution, anomalies
- A code reference — patterns and edge cases handled
- A discussion thread — decisions and dissent

Capture each source in whatever shape its value takes. Body is unconstrained.

## Frontmatter

The one universal across all source types is citation and relevance. Every context file opens with YAML frontmatter:

```yaml
---
source: <url or full citation>
captured: <YYYY-MM-DD>
type: <free-form: blog post, spec, video, code, paper, dataset, transcript, ...>
relevance: <one line — why this is in the research's context>
---
```

- `source` lets `RESEARCH.md` cite the upstream when synthesizing
- `captured` flags drift risk for sources that may have moved on
- `type` enables filtering across context (`grep` by type, query by category)
- `relevance` forces a justification at capture time — context isn't free-floating; it's there because it informs the research

## Filename

Kebab-case slug describing the source. Type-prefixed where helpful so a directory listing groups related sources visually:

- `mcp-specification.md`, `python-sdk-readme.md`, `fastmcp-docs.md`
- `blog-<author>-<topic>.md` for community write-ups
- `paper-<first-author>-<short-title>.md` for academic sources
- `talk-<speaker>-<event>.md` for talks and presentations
- `<host>-mcp-docs.md` or similar for ecosystem reference docs

Subjects may declare their own filename conventions when a domain has natural categories. Keep the scheme stable across all context files in the subject.

## Lifecycle

Captures may go stale as upstream sources evolve. Re-capture or note staleness when re-citing in `RESEARCH.md` if the source's content has materially changed. Delete when the research no longer references the source — subsumed, obsolete topic, or the source proved irrelevant.

Users own deployed copies — they can edit, extend, or add sources. Context files are evidence/background, not an execution dependency for any skill.
