# skill-authoring

Tooling for authoring new skills with project authoring discipline applied inline. Two companion skills: `skill-composer` composes new skills from exemplar sources via goal-driven dialogue with drift tracking; `skill-creator` creates new skills from scratch with the same disciplines layered on top of Anthropic's skill-creator. Both apply PFN + progressive-disclosure + description-authoring + workflow-vs-script at every authoring moment. Fills the unoccupied niche between `/plugin install` (bundle-atomic) and direct standalone install (`npx skills`).

Each composed skill is **self-contained**: `composition.md` (the recipe + provenance), embedded source skills (the ingredients during development), and `SKILL.md` (the deployed output) all live together in one folder. Cross-machine sharing is automatic — the skill folder carries everything it needs.

## Setup

```
/plugin install skill-authoring
```

Restart the session after install so the skills are discoverable. `uv` is a soft prerequisite — install via [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) when missing. All scripts are stdlib-only otherwise.

## Skills in this plugin

| Skill | Purpose |
|---|---|
| [`skill-composer`](skills/skill-composer/SKILL.md) | Compose new skills from one or more exemplar source skills via goal-driven dialogue, with drift tracking against pinned commits |
| [`skill-creator`](skills/skill-creator/SKILL.md) | Create new skills from scratch (interview → draft → iterate → optimize trigger → package), composed on top of Anthropic's skill-creator with PFN + progressive-disclosure + description-authoring + workflow-vs-script disciplines applied inline |

### Composer verbs

| Verb | Purpose |
|---|---|
| `compose new --destination <user\|project\|path>` | Open new-composition workflow. Agent collects name + sources + goal via dialogue, writes composition.md scaffold + live SKILL.md + workflow components directly. |
| `compose refine <name> --destination <user\|project\|path>` | Re-enter an existing composition. Script auto-runs `git ls-remote` per source for drift detection; agent surfaces drift and drives refinement of the live skill in place. |
| `compose list [--destination <user\|project\|path>] [--drift]` | Walk deployed compositions. With `--drift`, runs `git ls-remote` per source to report upstream drift. |

There is no separate `compose build` step — `compose new` produces both composition.md (intent) and the live skill files in the same flow.

### Creator verbs

| Verb | Purpose |
|---|---|
| `new <name>` | Interview the user, scaffold a live skill folder applying every authoring discipline inline. |
| `refine <name>` | Run the test-evaluate-iterate loop on an in-progress skill; on user satisfaction, run description optimization + packaging. |
| `list` | Enumerate in-progress skills across destinations. |

## Storage layout

```
<destination-parent>/<name>/        # composed and created skills both
├── SKILL.md                          # what Claude Code loads (PFN-structured body)
├── composition.md                    # recipe + provenance + pinned commits (composer-managed only)
├── sources/                          # embedded exemplars during active development (composer-managed)
│   ├── <source-slug-a>/              # sparse-checkout at pinned commit
│   └── <source-slug-b>/
├── _<verb>.md                        # PFN-structured workflow files
└── scripts/                          # skill's own implementation
```

`sources/` is present during composition development; `compose purge-sources` reclaims disk after finalization (pinned commits in composition.md persist; `compose refine` auto-rehydrates).

## What this plugin doesn't do

For installing unmodified upstream skills, use **Vercel's `npx skills`** ([skills.sh](https://skills.sh)) — symlinks into `~/.claude/skills/`, auto-fresh via upstream. skill-authoring focuses specifically on **goal-driven composition + from-scratch creation** with project disciplines applied inline; install is a different problem with mature tooling.

For atomic plugin-bundle install, `/plugin install <bundle>@<marketplace>` is the official Claude Code path. skill-authoring isn't an alternative there either.

The differentiation:

| Use case | Tool |
|---|---|
| Install one upstream skill, kept as-is | Vercel's `npx skills` |
| Install a plugin bundle | `/plugin install` |
| **Design a new skill from exemplars with authoring discipline applied + drift tracking** | **`/skill-authoring:skill-composer`** |
| **Create a new skill from scratch with authoring discipline applied inline** | **`/skill-authoring:skill-creator`** |

## Cross-machine portability

Composed skill folders are self-contained — `git init` any subdirectory of `<destination-parent>/` and push to your remote of choice. New machine: clone, the deployed compositions work immediately. No plugin-level sync verbs needed.

For project-scope compositions, `<project>/.claude/skills/<name>/` rides along with the project's git history naturally.

## License

MIT — see `LICENSE`.
