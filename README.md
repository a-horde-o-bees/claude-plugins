# a-horde-o-bees Claude Code Skills

One Claude Code plugin — `skills` — bundling agent authoring and interaction
discipline with a git development-cycle toolkit.

## Disclaimer

A personal development project: experimental, actively evolving, provided as-is
with no stability, support, or backwards-compatibility guarantees. Skills may be
added, removed, renamed, or restructured at any time. Use at your own discretion;
if something breaks, the LICENSE applies.

## What's inside

- **Authoring discipline** — `concise-prose`, `author-descriptions`,
  `author-markdown`, `author-processes`, `author-rules`, `reauthor`,
  `lint-markdown`.
- **Interaction discipline** — `honesty`, `confirm-shared-intent`.
- **Git development cycle** — `git-commit`, `git-push`, `git-ci`, `git-doctor`,
  `git-pr-open`/`-status`/`-merge`/`-cleanup`, `git-checkpoint`, `git-release`.
- **Transcripts** — query Claude Code session history as structured data.

Each skill is invoked bare (e.g. `/concise-prose`) and triggers on its own
description; the git skills also chain each other through the development cycle.

## Installation

```
/plugin marketplace add a-horde-o-bees/claude-plugins
/plugin install skills@a-horde-o-bees
```

Tracks `main` by default. Pin a tagged release with `@vX.Y.Z` on the marketplace
add. Restart the session after install so the skills register.

## Updating

```
/plugin marketplace update a-horde-o-bees
/reload-plugins
```

## Removing

```
/plugin uninstall skills
/plugin marketplace remove a-horde-o-bees
```

## Note for the maintainer

This repo is a **generated mirror** — skills are authored as live files in
`~/.claude/skills/` and published here by `scripts/publish-skills.py`. See
[CLAUDE.md](CLAUDE.md). Don't hand-edit `skills/`.

## License

MIT. See [LICENSE](LICENSE).
