---
name: ocd-pdf
description: Export markdown files to PDF using WeasyPrint.
argument-hint: "--src <file> [--src <file> ...] [--dest <dir>] [--set-css [<preset | path>]]"
allowed-tools:
  - Bash(mkdir *)
  - Bash(rm *)
  - Bash(cp *)
  - Bash(ls *)
  - Bash(ocd-run *)
---

# /pdf

Export markdown files to PDF using WeasyPrint — a purpose-built CSS-to-PDF engine that produces correct text layers (no missing spaces, no garbled characters on copy/paste). Replaces the Puppeteer/Chromium pipeline.

Stylesheet selection is filesystem-driven: exactly one `.css` file in `.claude/ocd/pdf/css/` is used as the complete stylesheet. The directory IS the config — inspectable, replaceable, no JSON to parse. Each stylesheet is fully self-contained.

## Rules

- Does not modify source markdown files
- PDF is a generated artifact — always overwrites existing PDFs
- Exactly one `.css` file in `.claude/ocd/pdf/css/` at any time
- Each CSS file is fully self-contained — no layering on base stylesheets

## Built-in Presets

| Preset | Description |
|--------|-------------|
| `github` | GitHub-flavored markdown with print optimizations |
| `compact` | Dense single-page layout for resumes, cover letters, and recommendation letters — Roboto font, tight margins, tracked-uppercase section headings |

Presets are complete, self-contained stylesheets. Copy one to `.claude/ocd/pdf/css/` as a starting point, then modify it for your needs.

Custom: place your own complete `.css` file in `.claude/ocd/pdf/css/`. It is the sole stylesheet applied — include everything you need.

## Dependencies

Requires `weasyprint` and `markdown` Python packages. Install into any Python environment accessible from the project:

```
uv pip install weasyprint markdown
```

## Workflow

### CSS Setup

1. If --set-css:
    1. If {set-css} is `github` or `compact`:
        1. bash: `mkdir -p .claude/ocd/pdf/css`
        2. bash: `rm -f .claude/ocd/pdf/css/*.css`
        3. bash: `cp ${CLAUDE_PLUGIN_ROOT}/subsystems/pdf/{set-css}.css .claude/ocd/pdf/css/`
        4. Exit to user — confirm preset installed
    2. If {set-css} is a file path:
        1. Verify path exists and ends with `.css`
        2. bash: `mkdir -p .claude/ocd/pdf/css`
        3. bash: `rm -f .claude/ocd/pdf/css/*.css`
        4. bash: `cp {set-css} .claude/ocd/pdf/css/`
        5. Exit to user — confirm custom CSS installed
    3. If --set-css has no value:
        1. AskUserQuestion: "Which stylesheet would you like to use for PDF export?"
            - `github` — GitHub-flavored markdown with print optimizations
            - `compact` — dense layout for resumes/letters (Roboto, tight margins, uppercase section headings)
            - Custom — place your own `.css` file in `.claude/ocd/pdf/css/`
        2. If user selects a preset: go to step 1.1
        3. If user selects custom: Exit to user — tell them to place their CSS file at `.claude/ocd/pdf/css/` and re-invoke

### CSS Resolution

2. bash: `mkdir -p .claude/ocd/pdf/css`
3. {css-files} = list `.css` files in `.claude/ocd/pdf/css/`
    1. If 0 files: go to step 1.3 — present stylesheet options via AskUserQuestion
    2. If 1 file: {stylesheet} = that file's absolute path
    3. If 2+ files: Exit to user — only one CSS file allowed in `.claude/ocd/pdf/css/`; list the files found and ask which to keep

### Export

4. If not --src: Exit to user — respond with skill description and argument-hint
5. {dest} = {dest} if --dest provided, else source file's parent directory
6. If --dest provided: bash: `mkdir -p {dest}`
7. For each --src:
    1. Verify {src} exists
    2. {src-base} = source filename with `.md` replaced by `.pdf`
    3. If --dest: {out} = {dest}/{src-base}
    4. Else: {out} = source directory/{src-base}
    5. Convert — bash: `ocd-run subsystems.pdf --src {src} --css {stylesheet} --dest {out}`
    6. Report result

### Report

Per file: source path, output PDF path, success/failure.
