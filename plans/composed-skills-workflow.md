# Composed-skills workflow

Workflow for maintaining shareable composed skills inside this monorepo using `progressive-skill-composer` + Vercel's `npx skills` (or `/plugin install`) as the install tooling.

## Why this workflow

progressive-skill-composer's default destinations (`user`, `project`) are right for most users — drop the composition straight into the consumer's Claude Code skills directory. For composed skills the **maintainer** of this repo wants to **share with others**, that default is wrong: the skill is consumed by the maintainer's downstream sessions, not authored as a redistributable artifact.

The composed-skills plugin shell is the bridge:

- composed skills are **authored** into `plugins/composed-skills/skills/<name>/` (this monorepo)
- composed skills are **installed** by anyone (including the maintainer's other machines) via standard tooling — `npx skills add a-horde-o-bees/claude-plugins --skill <name>` or `/plugin install composed-skills@a-horde-o-bees`
- composed skills are **synchronized** by the standard install/update mechanics (npm/marketplace cache + git pull)

The composition layer keeps drift tracking + source provenance regardless of which destination path it writes to.

## Folder layout

```
plugins/composed-skills/
├── .claude-plugin/
│   └── plugin.json                      # plugin manifest (created once)
├── README.md                            # plugin overview (created once)
├── ARCHITECTURE.md                      # plugin design notes (created once)
└── skills/                              # composed skills go here
    └── <name>/
        ├── SKILL.md                     # the live skill
        ├── composition.md               # design intent + source provenance
        ├── sources/                     # embedded exemplars (sparse-checked)
        │   └── <source-slug>/
        ├── _<verb>.md                   # workflow files (created during refinement)
        └── scripts/                     # composition's own Python (when applicable)
```

The plugin shell (`.claude-plugin/`, `README.md`, `ARCHITECTURE.md`) is created once by hand; subsequent compositions just add new `skills/<name>/` subdirectories.

## Compose flow

1. **Compose new** — author a new composed skill into the plugin

    ```
    uv run -m scripts.compose new --destination plugins/composed-skills/skills
    ```

    The `--destination` is a relative path that resolves under `CLAUDE_PROJECT_DIR`. The agent collects name, intent, Surface, and sources via dialogue, then writes `plugins/composed-skills/skills/<name>/composition.md`.

2. **Add sources** — sparse-check each exemplar into the composition's `sources/`

    ```
    uv run -m scripts.compose add-source <name> <url>:<skill> --destination plugins/composed-skills/skills
    ```

    Repeat per source. Pinned commits land in composition.md frontmatter.

3. **Refine** — fill in the Goal, Surface, and Sources body sections. Edit in place.

4. **Compose build** — scaffold the initial SKILL.md

    ```
    uv run -m scripts.compose build <name> --destination plugins/composed-skills/skills
    ```

    Creates `SKILL.md` + `scripts/__init__.py`. The agent fleshes out Triggers (from Surface) and creates `_<verb>.md` workflow files as the implementation matures.

5. **Commit + push** — the composition is now source-controlled. Anyone with access to the marketplace can install it.

## Consumer install paths

Once a composed skill is committed to main:

| Path | Command | What it does |
|---|---|---|
| Individual skill (Vercel) | `npx skills add a-horde-o-bees/claude-plugins --skill <name> -g` | Sparse-symlinks just `<name>/` into `~/.claude/skills/`; auto-fresh on upstream changes |
| Bundle (Claude Code) | `/plugin install composed-skills@a-horde-o-bees` | Installs the entire `composed-skills` plugin atomically |
| Manual | `git clone` + symlink/copy | For users who want neither |

`npx skills update` and `/plugin update composed-skills@a-horde-o-bees` handle synchronization downstream of the marketplace.

## Drift tracking continues to work

Even though the composition is in a monorepo (not in `<scope>/.claude/skills/`), progressive-skill-composer's drift detection works the same way:

```
uv run -m scripts.compose refine <name> --destination plugins/composed-skills/skills
```

The script reads composition.md, runs `git ls-remote` against each pinned source, and reports drift. Refinement edits happen in place; the skill files (SKILL.md, scripts/) evolve directly.

## Open: checkpoint integration

After cutting a tagged release of the marketplace, downstream consumers running on the stable channel won't see new composed skills until they update. Open design questions:

- Should `/checkpoint` auto-bump the composed-skills plugin version when any skill folder under it changes?
- Should there be a separate `/release composed-skills` flow that cuts the plugin's own release tag?
- How does `npx skills`-installed downstream behave if the marketplace cache lags the repo's main branch?

These tie into the broader release-flow design and the existing `components/versioning.md`. Defer until the workflow has a few real compositions through it.

## Open: composed-skills plugin shell

The `plugins/composed-skills/` plugin shell doesn't exist yet. Creating it is a separate step before the first composition lands there. The standard plugin scaffold:

- `.claude-plugin/plugin.json` — name `composed-skills`, version `0.0.1`, description
- `README.md` — user-facing overview (what this bundle contains, install paths)
- `ARCHITECTURE.md` — explains "this is a bundle of composed skills; each skill is its own design"
- entry in `.claude-plugin/marketplace.json` so the bundle is installable via `/plugin install`

Once that lands, `compose new --destination plugins/composed-skills/skills` becomes the working flow for shareable compositions.
