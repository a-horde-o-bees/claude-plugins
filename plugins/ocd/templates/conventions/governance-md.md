---
includes:
  - ".claude/rules/*.md"
  - ".claude/conventions/*.md"
excludes:
  - "architecture.md"
  - "README.md"
governed_by:
  - .claude/rules/ocd/markdown.md
  - .claude/rules/ocd/design-principles.md
---

# Governance File Conventions

Content and structure standards for rules and conventions — the files that govern agent behavior and file content.

## Frontmatter

YAML frontmatter is required. Fields define how the governance system discovers and orders these files.

### includes (required)

Declares which files this governance entry applies to. The navigator matches file paths against these patterns using `fnmatch`.

Single pattern as quoted string:

```yaml
includes: "*.py"
```

Multiple patterns as block-style YAML list:

```yaml
includes:
  - "test_*.*"
  - "*_test.*"
  - "conftest.*"
```

Rules that apply universally use `includes: "*"`. Conventions use patterns specific to their target file type.

Matching modes:

- **Basename**: `*.py` matches any `.py` file regardless of directory depth
- **Path with wildcard prefix**: `**/servers/*.py` matches `servers/*.py` at any depth in the directory tree. Use `**/` prefix when the target directory may be nested (e.g. under `plugins/`)
- **Full path**: `.claude/rules/*.md` matches files at exactly that project-relative path

### excludes (optional)

Patterns for files that should not match this governance entry even when they match `includes:`. Same format and matching rules as `includes:`.

```yaml
includes: "**/servers/*.py"
excludes:
  - "__init__.py"
  - "_helpers.py"
```

### governed_by (optional)

Lists governance entries this file builds on. Defines evaluation ordering — which governance entries must be stable before this one is evaluated. YAML block list of paths relative to project root.

```yaml
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/markdown.md
```

Governance relationships only — they define evaluation order and coherence checking in the governance chain. Tool references, implementation details, and runtime dependencies do not belong here.

## File Granularity

A governance file groups content that shares its governance contract — the `includes` pattern, `excludes` patterns, `governed_by` dependencies, and auto-load behavior declared in its frontmatter. A file's boundary is where the governance contract shifts, not where a reader perceives a topic break.

- A single governance file carries multiple sections when all sections share the governance contract the file declares
- Before splitting a governance file because "it's getting long": check whether the sections share the contract. If yes, the file is cohesive even at length — size-driven splits belong to Composability, which fires at context-capacity limits
- Before bundling new content into an existing governance file: verify the content shares `includes`, `excludes`, `governed_by`, and auto-load behavior. If any differs, it belongs in a different file
- Before writing new governance content: read both rule-side and convention-side framing before committing to either bucket. Guidance that fires regardless of which file is touched belongs in a rule; guidance that applies only when working with a specific file type belongs in a convention — reading only one side's framing risks putting the content in the wrong place
- Runtime-consumed governance files stay in their own file even when the governance contract could be merged with a sibling. Skills and tools read governance files directly by path at execution time — skill invocations do not participate in the `includes`/`excludes` lookup. A runtime consumer reading content needs a single file whose whole content is its input, not a section extracted from a larger document. Before merging such a file into another convention: check whether any skill or tool reads it directly at runtime; if yes, keep it separate. The evaluation triage criteria is one example — it is a convention that evaluation skills must honor, and the skill executor reads it directly to apply classification logic

## Body Structure

Rules define behavioral triggers with gate conditions — when to do what. Conventions define content standards with concrete requirements — what a conforming file contains.

Both follow the markdown convention for heading, purpose statement, and blank line separation.
