# pdf-skill-post-generation-sanity-check

## Purpose

Add structural-integrity validation to the `/ocd:pdf` skill so it flags rendering mismatches between the source markdown and the generated PDF rather than silently producing broken output.

## Context

The skill currently uses python-markdown with the `extra` extension, which collapses consecutive non-blank lines into a single paragraph. This produces silent defects — e.g., a `**From:** …\n**Date:** …\n**Re:** …` metadata block in a recommendation letter renders as one run-on paragraph rather than three separate lines. The defect is only caught when a reader opens the PDF and notices the visual problem.

Observed while iterating on Anthropic FDE application rec letters (April 2026). Same pattern showed up across six reference docs in the job-search project.

## Possible approaches

- **Generate-time pattern warnings** — regex pre-check flags suspicious source patterns (consecutive `**Label:**` paragraph lines, headings with no trailing blank line, tight multi-line blocks). Fast, cheap, doesn't require the PDF to exist.
- **Post-render diff** — extract text from the generated PDF, count paragraph-equivalents, compare against markdown paragraph count; warn on mismatch. More thorough but requires PDF text extraction (pypdf already in deps for testing).
- **Combined** — pre-check for known bad patterns, post-render diff as a defense-in-depth backstop.

## Prerequisites

- Decide error vs warning behavior — probably non-fatal warnings to stderr; the PDF still generates.
- Heuristic tuning — false-positive rate for "consecutive bold lines" needs testing (bullet lists with leading bold wouldn't trigger this since they start with `-`, but there may be other edge cases).

## Open questions

- Should the skill also support a "safe markdown" mode that auto-inserts blank lines between consecutive `**Label:**` lines? Or stay advisory-only and expect the user to fix source? Advisory probably cleaner — auto-edit of user content is surprising behavior.
