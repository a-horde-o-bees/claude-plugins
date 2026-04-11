# Conventions

File-type-specific content standards loaded on demand when files matching their pattern are created or modified.

## How Conventions Work

Each convention is a markdown file with YAML frontmatter declaring which files it applies to. When an agent is about to create or modify a file, it calls `governance_match` with the target file paths. The navigator returns which conventions apply, and the agent reads and follows them.

Conventions are **on-demand** — they load only when relevant files are being worked on, unlike rules which are always present in every session.

## Using Conventions

Before creating or modifying files, call `governance_match` with the file paths. Read each returned convention you haven't already read in this session, then follow its requirements.

The `governance_match` tool accepts multiple file paths in one call — batch all files you're about to work on rather than calling per-file.

## Creating a Convention

1. Create a markdown file in `.claude/conventions/` with frontmatter:

```yaml
---
includes: "*.py"
governed_by:
  - .claude/conventions/python.md
---
```

2. Write content standards in the body — what a conforming file contains, not agent behavior triggers (those belong in rules).

3. Run `/ocd-init` to register the convention in the governance database.

## Frontmatter Fields

- **`includes`** (required) — file patterns this convention applies to. Basename patterns (`*.py`) match the filename; path patterns (`.claude/rules/*.md`) match the full project-relative path.
- **`excludes`** (optional) — patterns for files that should not match even when they match `includes`.
- **`governed_by`** (optional) — governance entries this convention builds on. Defines evaluation ordering — which entries must be stable before this one is evaluated.

## Relationship to Rules

Rules govern agent behavior (always loaded, fire by trigger condition). Conventions govern file content (loaded on demand, applied when matching files are created or modified). See `.claude/rules/README.md` for the rules system.

Both share the same frontmatter format and governance infrastructure. The `governance-md.md` convention in this directory defines the shared content standards for both.
