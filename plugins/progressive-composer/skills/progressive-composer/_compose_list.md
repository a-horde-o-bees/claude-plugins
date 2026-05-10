# Compose list

Walk `<scope>/.claude/skills/*/composition.md` at user and/or project scope and report a one-line summary per deployed skill: name, type (install vs composed), source count, build status, last_build timestamp. With `--drift`, additionally runs `git ls-remote` per source per composition and reports per-source drift.

## Arguments

`[--scope <both|user|project>] [--drift]`

- `--scope` — which scope(s) to enumerate. Default `both`.
- `--drift` — opt in to network drift check. Without this flag, list reports last-known status from composition.md frontmatter only (no network calls). With it, runs ls-remote per source — slower but always accurate.

## Process

1. Invoke — bash: `uv run -m scripts.compose list [--scope <both|user|project>] [--drift]`

2. The script walks each requested scope's `<scope>/.claude/skills/*/composition.md` files. For each:
    - Parses frontmatter
    - Reports name, type, source count, build_status, last_build (when present)
    - If `--drift` is set, runs `git ls-remote <url> <ref>` per source and reports drift inline as indented detail lines

3. When project-scope is requested but the working directory is not inside a git checkout, project-scope is silently skipped (project_dir unresolvable).

4. When a composition.md has malformed frontmatter, the corresponding line reports the parse error rather than crashing the listing.

## Output

Without `--drift`:

```
user-scope:
  - markdown-formatter (composed, 2 sources, built, last build 2026-05-10T14:00:00Z)
  - slack-formatting (install, 1 source, built, last build 2026-05-09T10:00:00Z)

project-scope:
  - project-helper (composed, 3 sources, draft)
```

With `--drift`:

```
user-scope:
  - markdown-formatter (composed, 2 sources, built, last build 2026-05-10T14:00:00Z)
      drift: https://github.com/anthropics/skills.git:slack-formatting@main abc12345 → def67890
  - slack-formatting (install, 1 source, built, last build 2026-05-09T10:00:00Z)
```

When no skills are deployed at any requested scope, prints `no skills deployed by progressive-composer at the requested scope(s)`.
