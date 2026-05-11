# progressive-composer

Compose new skills from one or more exemplar sources via goal-driven dialogue, with PFN + progressive-disclosure authoring discipline baked into the output. Fills the unoccupied niche between `/plugin install` (bundle-atomic) and direct standalone install (`npx skills`): nothing in the ecosystem composes new skills from exemplars against a user-articulated goal.

Each composed skill is **self-contained**: `composition.md` (the recipe + provenance), embedded source skills (the ingredients during development), and `SKILL.md` (the deployed output) all live together in one folder. Cross-machine sharing is automatic — the skill folder carries everything it needs.

## Setup

```
/plugin install progressive-composer
```

Restart the session after install so the skill is discoverable. `uv` is a soft prerequisite — install via [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) when missing. All scripts are stdlib-only otherwise.

## Verbs

| Verb | Purpose |
|---|---|
| `compose new --destination <user\|project\|path>` | Open new-composition workflow. Agent collects name + sources + goal via dialogue, writes composition.md scaffold via Write tool, embeds sources via `compose add-source`. |
| `compose refine <name> --destination <user\|project\|path>` | Re-enter an existing composition. Script auto-runs `git ls-remote` per source for drift detection; agent surfaces drift and drives refinement dialogue. |
| `compose build <name> --destination <user\|project\|path> [--force]` | Materialize composition.md into a deployable SKILL.md (PFN + progressive-disclosure structured) plus `_<verb>.md` workflow scaffolds and `scripts/` package skeleton. |
| `compose list [--destination <user\|project\|path>] [--drift]` | Walk deployed compositions. With `--drift`, runs `git ls-remote` per source to report upstream drift. |

## Storage layout

```
<destination-parent>/<name>/        # composed skills
├── SKILL.md                          # what Claude Code loads (PFN-structured body)
├── composition.md                    # recipe + provenance + pinned commits
├── sources/                          # embedded exemplars during active development
│   ├── <source-slug-a>/              # sparse-checkout at pinned commit
│   └── <source-slug-b>/
├── _<verb>.md                        # PFN-structured workflow scaffolds (from compose build)
└── scripts/                          # composition's own implementation
```

`sources/` is present during development; `compose purge-sources` reclaims disk after finalization (pinned commits in composition.md persist; `compose refine` auto-rehydrates).

## What this plugin doesn't do

For installing unmodified upstream skills, use **Vercel's `npx skills`** ([skills.sh](https://skills.sh)) — symlinks into `~/.claude/skills/`, auto-fresh via upstream. progressive-composer focuses specifically on **goal-driven composition** with **drift tracking against pinned snapshots**; install is a different problem with mature tooling.

For atomic plugin-bundle install, `/plugin install <bundle>@<marketplace>` is the official Claude Code path. progressive-composer isn't an alternative there either.

The differentiation:

| Use case | Tool |
|---|---|
| Install one upstream skill, kept as-is | Vercel's `npx skills` |
| Install a plugin bundle | `/plugin install` |
| **Design a new skill from exemplars with authoring discipline applied + drift tracking** | **progressive-composer** |

## Cross-machine portability

Composed skill folders are self-contained — `git init` any subdirectory of `<destination-parent>/` and push to your remote of choice. New machine: clone, the deployed compositions work immediately. No plugin-level sync verbs needed.

For project-scope compositions, `<project>/.claude/skills/<name>/` rides along with the project's git history naturally.

## License

MIT — see `LICENSE`.
