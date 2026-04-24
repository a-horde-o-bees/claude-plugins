---
name: ocd-pdf
description: Export markdown files to PDF using WeasyPrint.
argument-hint: "--src <file> [--src <file> ...] [--dest <dir>] [--set-css [<preset | path>]]"
allowed-tools:
  - Bash(mkdir:*)
  - Bash(rm:*)
  - Bash(cp:*)
  - Bash(ls:*)
  - Bash(ocd-run:*)
---

# /pdf

Export markdown files to PDF using WeasyPrint — a purpose-built CSS-to-PDF engine that produces correct text layers (no missing spaces, no garbled characters on copy/paste). Replaces the Puppeteer/Chromium pipeline.

Stylesheet selection is filesystem-driven: exactly one template subfolder in `.claude/ocd/pdf/templates/` holds the active stylesheet and any assets it references (fonts, images). The directory IS the config — inspectable, replaceable, no JSON to parse. Each template is fully self-contained.

## Rules

- Does not modify source markdown files
- PDF is a generated artifact — always overwrites existing PDFs
- Exactly one template subfolder in `.claude/ocd/pdf/templates/` at any time, containing exactly one `.css` file plus any assets it references
- Each template is fully self-contained — no layering on base stylesheets; asset URLs are resolved relative to the CSS file, so fonts and images must sit as siblings

## Built-in Presets

| Preset | Description |
|--------|-------------|
| `github` | GitHub-flavored markdown with print optimizations |
| `compact` | Dense single-page layout for resumes, cover letters, and recommendation letters — Roboto font, tight margins, tracked-uppercase section headings |

Presets are complete, self-contained templates shipped as folders under `${CLAUDE_PLUGIN_ROOT}/systems/pdf/templates/`. Copy one into `.claude/ocd/pdf/templates/` as a starting point, then modify it for your needs.

Custom: place your own template folder (one `.css` plus any assets it references) in `.claude/ocd/pdf/templates/`. It is the sole stylesheet applied — include everything you need.

## Dependencies

Requires `weasyprint` and `markdown` Python packages. Install into any Python environment accessible from the project:

```
uv pip install weasyprint markdown
```

## Workflow

### CSS Setup

1. If --set-css:
    1. If {set-css} is `github` or `compact`:
        1. bash: `mkdir -p .claude/ocd/pdf/templates`
        2. bash: `rm -rf .claude/ocd/pdf/templates/*`
        3. bash: `cp -r ${CLAUDE_PLUGIN_ROOT}/systems/pdf/templates/{set-css} .claude/ocd/pdf/templates/`
        4. Exit to user — confirm preset installed
    2. If {set-css} is a path:
        1. Verify {set-css} exists and is a directory containing exactly one `.css` file
        2. bash: `mkdir -p .claude/ocd/pdf/templates`
        3. bash: `rm -rf .claude/ocd/pdf/templates/*`
        4. bash: `cp -r {set-css} .claude/ocd/pdf/templates/`
        5. Exit to user — confirm custom template installed
    3. If --set-css has no value:
        1. AskUserQuestion: "Which stylesheet would you like to use for PDF export?"
            - `github` — GitHub-flavored markdown with print optimizations
            - `compact` — dense layout for resumes/letters (Roboto, tight margins, uppercase section headings)
            - Custom — place your own template folder in `.claude/ocd/pdf/templates/`
        2. If user selects a preset: go to step 1.1
        3. If user selects custom: Exit to user — tell them to place their template folder at `.claude/ocd/pdf/templates/<name>/` (one `.css` plus any assets) and re-invoke

### CSS Resolution

2. bash: `mkdir -p .claude/ocd/pdf/templates`
3. If `.claude/ocd/pdf/css/` exists: Exit to user — legacy flat layout detected at `.claude/ocd/pdf/css/`; rerun with `--set-css <preset>` to migrate, or move your CSS into `.claude/ocd/pdf/templates/<name>/` manually and remove the old `css/` folder
4. {template-dirs} = list subdirectories of `.claude/ocd/pdf/templates/`
    1. If 0 subdirectories: go to step 1.3 — present stylesheet options via AskUserQuestion
    2. If 2+ subdirectories: Exit to user — only one template subfolder allowed in `.claude/ocd/pdf/templates/`; list the folders found and ask which to keep
    3. If 1 subdirectory: {template-dir} = that subdirectory's absolute path
5. {css-files} = list `.css` files directly under {template-dir}
    1. If 0 files: Exit to user — template folder {template-dir} contains no `.css` file
    2. If 2+ files: Exit to user — template folder {template-dir} contains multiple `.css` files; exactly one is required
    3. If 1 file: {stylesheet} = that file's absolute path

### Export

6. If not --src: Exit to user — respond with skill description and argument-hint
7. {dest} = {dest} if --dest provided, else source file's parent directory
8. If --dest provided: bash: `mkdir -p {dest}`
9. For each --src:
    1. Verify {src} exists
    2. {src-base} = source filename with `.md` replaced by `.pdf`
    3. If --dest: {out} = {dest}/{src-base}
    4. Else: {out} = source directory/{src-base}
    5. Convert — bash: `ocd-run pdf --src {src} --css {stylesheet} --dest {out}`
    6. Report result

### Report

Per file: source path, output PDF path, success/failure.
