---
name: md-to-pdf
description: Export markdown files to PDF styled with GitHub-flavored CSS.
argument-hint: "--src <file> [--src <file> ...] --dest <dir>"
allowed-tools:
  - Bash(command -v *)
  - Bash(mkdir *)
  - Bash(md-to-pdf *)
  - Bash(mv *)
  - Bash(dirname *)
  - Bash(basename *)
---

# /md-to-pdf

Export markdown files to PDF styled with GitHub-flavored CSS. Uses the globally-installed `md-to-pdf` CLI (which writes each PDF next to its source), then moves each result to the requested destination directory.

## Rules

- Does not modify source markdown files

## Workflow

1. If not --src: Exit to user: skill description and argument-hint
2. If not --dest: Exit to user: `--dest` is required; specify output directory
3. Verify `md-to-pdf` installed — bash: `command -v md-to-pdf`
    1. If not found: Exit to user: install with `npm i -g md-to-pdf`
4. Ensure destination directory exists — bash: `mkdir -p {dest}`
5. For each --src:
    1. Verify {src} exists
    2. {src-dir} = bash: `dirname {src}`
    3. {src-base} = bash: `basename {src} .md`
    4. Convert — bash: `md-to-pdf {src} --stylesheet ${CLAUDE_PLUGIN_ROOT}/skills/md-to-pdf/github-markdown-light.css --stylesheet ${CLAUDE_PLUGIN_ROOT}/skills/md-to-pdf/print-supplement.css --body-class markdown-body`
    5. Move PDF to destination — bash: `mv {src-dir}/{src-base}.pdf {dest}/`
    6. Report result

### Report

Per file: source path, output PDF path, success/failure.
