# a-horde-o-bees Claude Code Skills

One Claude Code plugin — `skills` — bundling agent authoring and interaction
discipline with a git development-cycle router.

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
- **Git development cycle** — `git`, one router fronting verbs for `commit`,
  `push`, `ci`, the PR lifecycle (`pr-open`/`pr-status`/`pr-merge`/`pr-cleanup`),
  `checkpoint`, `release`, and repo-health `doctor`.
- **Transcripts** — query Claude Code session history as structured data.

Most skills are invoked bare (e.g. `/concise-prose`) and trigger on their own
description. The git router dispatches to one verb (`/git <verb>`, or bare
`/git` to pick from a menu); its verbs chain each other through the development
cycle.

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

## License

MIT. See [LICENSE](LICENSE).
