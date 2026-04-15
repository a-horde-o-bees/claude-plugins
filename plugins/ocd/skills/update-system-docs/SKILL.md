---
name: update-system-docs
description: "[in development] Maintain project documentation by deriving it from code reality. Design-only placeholder; implementation pending. See _DESIGN.md."
argument-hint: "--target project"
disable-model-invocation: true
user-invocable: false
---

# /update-system-docs

**Status: in development — do not invoke.**

This skill is a placeholder for a documentation-maintenance tool that will regenerate canonical docs (README.md, architecture.md, CLAUDE.md, SKILL.md) from a deterministic fact bundle extracted from code, apply surgical edits to non-obvious surfaces (docstrings, CLI help, MCP tool descriptions, frontmatter), and port over unverifiable prose from prior doc versions. Git diff is the review gate; unresolved questions bubble up for user judgment.

The full design — problem statement, wave-based traversal architecture, regenerate-with-port-over flow, fact bundle schema, and remaining implementation work — lives in `_DESIGN.md`.

The prior component files (prompt templates, per-system workflow, summary schema, etc.) were removed because they were partial-implementation artifacts from a mid-design state; the design intent is captured in `_DESIGN.md` and implementation will regenerate what it needs from there.

`disable-model-invocation: true` and `user-invocable: false` in frontmatter keep the skill out of auto-loading and the `/` menu until it's ready.

## Workflow

1. Exit to caller — this skill is a design-only placeholder; implementation is pending. Read `_DESIGN.md` for the full design.
