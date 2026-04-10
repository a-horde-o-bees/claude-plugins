---
matches:
  - ".claude/rules/*.md"
  - ".claude/conventions/*.md"
excludes:
  - "architecture.md"
  - "README.md"
governed_by:
  - .claude/conventions/markdown.md
  - .claude/rules/ocd-design-principles.md
---

# Governance File Conventions

Content and structure standards for rules and conventions — the files that govern agent behavior and file content.

## Frontmatter

YAML frontmatter is required. Fields define how the governance system discovers and orders these files.

### matches (required)

Declares which files this governance entry applies to. The navigator matches file paths against these patterns using `fnmatch`.

Single pattern as quoted string:

```yaml
matches: "*.py"
```

Multiple patterns as block-style YAML list:

```yaml
matches:
  - "test_*.*"
  - "*_test.*"
  - "conftest.*"
```

Rules that apply universally use `matches: "*"`. Conventions use patterns specific to their target file type. Path patterns (e.g. `.claude/rules/*.md`) match against the full project-relative path; basename patterns (e.g. `*.py`) match against the filename alone.

### excludes (optional)

Patterns for files that should not match this governance entry even when they match `matches:`. Same format and matching rules as `matches:`.

```yaml
matches: "servers/*.py"
excludes:
  - "__init__.py"
  - "_helpers.py"
```

### governed_by (optional)

Lists governance entries this file builds on. Defines evaluation ordering — which governance entries must be stable before this one is evaluated. YAML block list of paths relative to project root.

```yaml
governed_by:
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/markdown.md
```

Governance relationships only — they define evaluation order and coherence checking in the governance chain. Tool references, implementation details, and runtime dependencies do not belong here.

## Body Structure

Rules define behavioral triggers with gate conditions — when to do what. Conventions define content standards with concrete requirements — what a conforming file contains.

Both follow the markdown convention for heading, purpose statement, and blank line separation.
