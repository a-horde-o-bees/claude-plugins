# Compose list

> Workflow component for the `list` verb of compose. Walks composition.md files at the requested destination(s) and reports a one-line summary per composition: name, source count, deployed status (does SKILL.md exist?). With `--drift`, additionally runs `git ls-remote` per source per composition and reports per-source drift inline.

## Arguments

`[--destination <user|project|path>] [--drift]`

- `--destination` — which destination to enumerate. Default: both `user` and `project`. Pass an explicit path to list compositions at a custom destination.
- `--drift` — opt in to network drift check. Without this flag, emits filesystem-derived state only (no network calls). With it, runs `git ls-remote` per source — slower but reflects current upstream.

## Process

1. {report}: bash: `uv run --directory <skill-base> -m scripts.compose list [--destination <user|project|path>] [--drift]`

2. Surface {report} to the user.

> The script walks each requested destination's `<destination-parent>/*/composition.md` files, parses frontmatter, checks whether SKILL.md exists alongside (reports `deployed` or `draft`), and emits name + source count + deployed status. With `--drift`, runs `git ls-remote <url> <ref>` per source and indents drift detail.

> When `project` is requested but cwd isn't inside a git checkout (and `CLAUDE_PROJECT_DIR` is unset), project is silently skipped. Malformed composition.md frontmatter is reported inline rather than crashing the listing.

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

When no compositions exist at any requested destination: `no skills deployed by skill-composer at the requested destination(s)`.
