---
name: description-authoring
description: Use whenever writing a description for any artifact at any scale — directory, file header, section head, docstring (function/class/module), skill frontmatter, navigator entry, tool help text, commit subject, log entry opener, schema title — where a reader decides engage-vs-skip from the description alone.
---

# Description Authoring

A description is the line a reader uses to decide engage-or-skip — often the only thing they have. Readers are users, other agents, or downstream tools. A vague one makes the content effectively invisible.

## Directives

**Substance**
- Describe what the artifact is for, not how it does it — its responsibility or the outcome it produces, never the method behind it. "Rank search results by relevance" is a what; "rank results with TF-IDF scoring" is a how.
- Convey two things: what the artifact covers and what kind of thing it is (e.g. directory, module, CLI, config, rule, schema, section, function).
- Weave both into fluent prose — never expose them as labeled fields or split halves. "Retry and backoff helpers for outbound HTTP calls," not "Scope: HTTP retries. Role: helper module." The reader should see no seam.
- Match the abstraction to the artifact's size — a directory's coverage is coarser than a file's, a package's coarser than a function's.
- Third person.

**Length**
- Run as long as granularity requires, no longer — the quality tests below decide when it's enough, not a word budget. Most descriptions are one sentence; a broad or multi-faceted artifact may run to a few. Don't pad toward a paragraph, don't compress past distinguishability.

**Exclude**
- How it works — the method, steps, or approach it uses (for a skill, the technique it teaches; not only code).
- Content listing — section, function, or class names.
- History — why it exists, what it replaced, when it was added.

**Consistency**
- The same artifact described at any boundary reuses one description — single source of truth.

## Quality tests

- Interchangeable with another artifact's description → too vague.
- Would change when internals are refactored though the responsibility holds → too detailed.
- Would fit equally at a different scale → wrong granularity.
