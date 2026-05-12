# Compose list

Walk composition.md files at the requested destination(s) and report a one-line summary per composition: name, source count, deployed status (does SKILL.md exist?). With `--drift`, additionally runs `git ls-remote` per source per composition and reports per-source drift inline.

## Arguments

`[--destination <user|project|path>] [--drift]`

- `--destination` — which destination to enumerate. Default: both `user` and `project`. Pass an explicit path to list compositions at a custom destination.
- `--drift` — opt in to network drift check. Without this flag, list emits filesystem-derived state only (no network calls). With it, runs ls-remote per source — slower but reflects current upstream.

## Process

1. Invoke — bash: `uv run -m scripts.compose list [--destination <user|project|path>] [--drift]`

2. The script walks each requested destination's `<destination-parent>/*/composition.md` files. For each:
    - Parses frontmatter
    - Checks whether SKILL.md exists in the same folder; reports `deployed` or `draft`
    - Reports name, source count, deployed status
    - If `--drift` is set, runs `git ls-remote <url> <ref>` per source and reports drift inline as indented detail lines

3. When `project` is requested but the working directory is not inside a git checkout (and `CLAUDE_PROJECT_DIR` is unset), project is silently skipped (project_dir unresolvable).

4. When a composition.md has malformed frontmatter, the corresponding line reports the parse error rather than crashing the listing.

## Output

Without `--drift`:

```
user:
  - markdown-formatter (2 sources, deployed)

project:
  - claude-python (5 sources, draft)
```

With `--drift`:

```
user:
  - markdown-formatter (2 sources, deployed)
      drift: https://github.com/anthropics/skills.git:slack-formatting@main abc12345 → def67890

project:
  - claude-python (5 sources, draft)
```

When no compositions exist at any requested destination, prints `no skills deployed by skill-composer at the requested destination(s)`.
