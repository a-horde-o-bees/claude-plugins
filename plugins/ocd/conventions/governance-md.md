---
pattern: [".claude/rules/*.md", ".claude/conventions/*.md"]
depends:
  - .claude/conventions/markdown.md
  - .claude/rules/ocd-design-principles.md
---

# Governance File Conventions

Content and structure standards for rules and conventions — the files that govern agent behavior and file content.

## Frontmatter

YAML frontmatter is required. Fields define how the governance system discovers and orders these files.

### pattern (required)

Declares which files this governance entry applies to. The navigator matches file paths against these patterns using `fnmatch`.

Single pattern as quoted string:

```yaml
pattern: "*.py"
```

Multiple patterns as flow-style YAML list:

```yaml
pattern: ["test_*.*", "*_test.*", "conftest.*"]
```

Rules that apply universally use `pattern: "*"`. Conventions use patterns specific to their target file type. Path patterns (e.g. `.claude/rules/*.md`) match against the full project-relative path; basename patterns (e.g. `*.py`) match against the filename alone.

### depends (optional)

Lists governance dependencies — other governance files this entry builds on. YAML block list of paths relative to project root.

```yaml
depends:
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/markdown.md
```

Dependencies are governance relationships only — they define evaluation order and coherence checking in the governance chain. Tool references, implementation details, and runtime dependencies do not belong here.

## Body Structure

Rules define behavioral triggers with gate conditions — when to do what. Conventions define content standards with concrete requirements — what a conforming file contains.

Both follow the markdown convention for heading, purpose statement, and blank line separation.
