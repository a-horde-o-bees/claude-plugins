---
name: description-authoring
description: Use when writing the line a reader uses to decide engage-or-skip — an artifact's description at any scale (e.g. file header, docstring, skill frontmatter, commit subject).
---

# description-authoring

Use when writing the line a reader uses to decide engage-or-skip — an artifact's description at any scale (e.g. file header, docstring, skill frontmatter, commit subject).

Often it is the only thing the reader — user, other agent, or downstream tool — has. A vague description makes the content effectively invisible.

## Substance

- Describe what the artifact is for, not how it does it — its responsibility or the outcome it produces, never the method, steps, or approach behind it, including the technique a skill teaches. "Rank search results by relevance" is a what; "rank results with TF-IDF scoring" is a how.
- Convey two things: what the artifact covers and what kind of thing it is (e.g. directory, module, CLI, config, rule, schema, section, function).
- Weave both into fluent prose with no visible seam — never labeled fields or split halves. "Retry and backoff helpers for outbound HTTP calls," not "Scope: HTTP retries. Role: helper module."
- Lead with the key case — descriptions are read, and truncated, front-first; the first clause must carry the engage-or-skip decision on its own.
- Match the abstraction to the artifact's scale — a directory's coverage is coarser than a file's, a package's coarser than a function's.
- Third person.

## Length

- Run as long as granularity requires, no longer — the quality tests below decide when it's enough, not a word budget. Most descriptions are one sentence; a broad or multi-faceted artifact may run to a few. Don't pad toward a paragraph, don't compress past distinguishability.
- One distinctive condition outweighs many restatements. The reader — or a matcher deciding whether to engage — needs a single clause that separates this artifact from its neighbors; synonym runs and example-phrasing lists add no distinguishing power, and each restatement widens accidental matches without covering a new case. Distinct cases may be listed (`e.g.`-marked); rephrasings of one case may not.

## Exclude

- Don't list contents — section, function, or class names.
- Don't recount history — why it exists, what it replaced, when it was added.

## Consistency

- The same artifact described at any boundary reuses one description — single source of truth.

## Quality tests

- Interchangeable with another artifact's description → too vague.
- Would change when internals are refactored though the responsibility holds → too detailed.
- Would fit equally at a different scale → wrong granularity.
- Contains a phrase whose removal loses no case → a restatement; cut it.
