---
name: md-to-pdf
description: Export markdown files to professionally formatted PDF using GitHub-standardized CSS styling.
argument-hint: "--src <file> [--src <file> ...] --dest <dir>"
allowed-tools:
  - Bash(command -v *)
  - Bash(mkdir *)
  - Bash(md-to-pdf *)
  - Bash(mv *)
---

# /md-to-pdf

Export markdown files to PDF using md-to-pdf with GitHub-standardized CSS styling.

## Trigger

User runs `/md-to-pdf`.

## Route

1. If not --src: Exit to user — respond with skill description and argument-hint
2. If not --dest: Exit to user — `--dest` is required; specify output directory
3. Verify `md-to-pdf` is available — bash: `command -v md-to-pdf`
    1. If not found: Exit to user — `md-to-pdf` is required; install with `npm i -g md-to-pdf`

## Workflow

1. Ensure destination directory exists — bash: `mkdir -p {dest}`
2. For each --src:
    1. Verify {src} exists
    2. Convert — bash: `md-to-pdf {src} --stylesheet ${CLAUDE_PLUGIN_ROOT}/skills/md-to-pdf/github-markdown-light.css --stylesheet ${CLAUDE_PLUGIN_ROOT}/skills/md-to-pdf/print-supplement.css --body-class markdown-body`
    3. Move PDF to destination — bash: `mv {source-dir}/{name}.pdf {dest}/`
    4. Report result

### Report

Per file: source path, output PDF path, success/failure.

## Rules

- Requires `md-to-pdf` installed globally (`npm i -g md-to-pdf`)
- md-to-pdf creates output next to source file; skill moves it to destination after conversion
- Overwrites existing PDFs with same name without prompting
- Does not modify source markdown files
