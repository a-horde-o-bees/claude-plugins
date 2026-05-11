# composed-skills

A curated bundle of skills composed via [`progressive-skill-composer`](../progressive-skill-composer/README.md). Each skill in this bundle was designed from one or more exemplar source skills with PFN + progressive-disclosure authoring discipline applied automatically, and carries its own `composition.md` recording the design intent + pinned upstream source provenance for drift tracking.

## What this bundle contains

Individual `skills/<name>/` folders, each a self-contained composed skill:

- `SKILL.md` — what Claude Code loads (the live, refined implementation)
- `composition.md` — design intent + pinned source provenance (alignment doc between exemplars and the live skill)
- `sources/<source-slug>/` — embedded exemplar skills sparse-checked at pinned commits (when present; may be purged after finalization)
- `_<verb>.md` + `scripts/` — PFN-structured workflow files and Python implementation (when applicable)

See each skill's `SKILL.md` for what it does and its `composition.md` for why it was composed the way it was.

## Install paths

| Goal | Command |
|---|---|
| Install the entire bundle | `/plugin install composed-skills@a-horde-o-bees` |
| Install one skill (Vercel) | `npx skills add a-horde-o-bees/claude-plugins --skill <name> -g` |
| Inspect without installing | Browse `skills/<name>/SKILL.md` on GitHub |

`/plugin install` pulls the whole bundle atomically. `npx skills` picks individual skills and symlinks them into `~/.claude/skills/`. Both tracks against this repo's main branch on the dev channel; pin to a tagged release with `@vX.Y.Z` on either path.

## Setup

```
/plugin install composed-skills@a-horde-o-bees
```

Restart the session after install so the new skills are discoverable. Most composed skills are stdlib-only Python under `scripts/` invoked via `uv run`; `uv` is a soft prerequisite per individual skill needs.

## Differentiation from other bundles

| Concern | Bundle |
|---|---|
| Project discipline (rules, conventions, permissions) | [`ocd`](../ocd/) |
| Skill-composition tooling itself | [`progressive-skill-composer`](../progressive-skill-composer/) |
| **The composed skills produced by that tooling** | **`composed-skills`** (this) |

This bundle is the output side of the compose workflow. Composers (people who author new skills) reach for `progressive-skill-composer`. Consumers (people who use those skills downstream) reach for this bundle.

## Authoring discipline

Every skill in this bundle was composed under the discipline encoded in `progressive-skill-composer`:

- **PFN notation** in workflow files (`_<verb>.md`) — numbered steps, indentation-scoped blocks, explicit `Call:` / `bash:` / `skill:` invocation prefixes
- **Progressive disclosure** in SKILL.md — frontmatter description as cognitive trigger; body holds Triggers + topography pointing at `_<verb>.md` workflow files (not inline procedures)
- **composition.md as alignment doc** — captures Goal, Surface (cognitive moments and their routes), and per-source Sources rationale; never a complete blueprint, always tracking current intent

See `ARCHITECTURE.md` for the bundle's internal structure.

## License

MIT — see `LICENSE`.
