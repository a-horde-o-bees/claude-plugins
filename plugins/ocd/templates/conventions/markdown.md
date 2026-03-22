---
pattern: "*.md"
---

# Markdown Conventions

Shared patterns for markdown documentation across all file types. File-type-specific conventions are in companion files (e.g., `skill.md`, `claude-md.md`).

## File Map

Required section for any markdown file that references other files. Declares the complete manifest of file references used in the document. Placed after frontmatter and title but before the first content section.

### Format

````markdown
## File Map

### Dependencies
```
path/to/existing-file.md
path/to/existing-script.py
```

### Created
```
path/to/runtime-output.md
path/to/runtime-output.db
```
````

Two subsections:

- `### Dependencies` — files that exist in the project, referenced by this document. Paths must resolve in the file catalog.
- `### Created` — files that do not exist yet, produced at runtime by the process this document describes. These are excluded from broken-reference checking throughout the document.

Omit either subsection if the file has no entries for it. One path per line inside a fenced code block, no bullets, no comments.

### Path Consistency

Every file reference in the document body must use the same path form as declared in the File Map. If the Dependencies section declares `scripts/example.py`, all body references use `scripts/example.py` — not `example.py` or `.claude/skills/name/scripts/example.py`.
