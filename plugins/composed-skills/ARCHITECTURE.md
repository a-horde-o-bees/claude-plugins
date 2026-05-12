# composed-skills architecture

Internal design reference for maintainers. User-facing documentation lives in `README.md`.

## Purpose

This bundle exists to make composed skills shareable and installable. `skill-authoring:skill-composer`'s default `--destination` keywords (`user`, `project`) write a composition straight into a consumer's Claude Code skills directory — correct for personal use, wrong for sharing. This plugin shell is the third destination: `--destination plugins/composed-skills/skills` from the project root puts a composition into a path that the standard install tooling (`/plugin install`, `npx skills`) can publish to other machines and other users.

## Layers

```
plugins/composed-skills/
├── .claude-plugin/
│   └── plugin.json                      # plugin manifest (name, version, skills entry)
├── README.md                            # consumer overview
├── ARCHITECTURE.md                      # this file
├── LICENSE                              # MIT
└── skills/                              # one subdirectory per composed skill
    └── <name>/                          # composed via skill-authoring:skill-composer
        ├── SKILL.md
        ├── composition.md
        ├── sources/                     # optional; sparse-checked at pinned commits
        ├── _<verb>.md                   # PFN workflow files (added during refinement)
        └── scripts/                     # composition's Python (when applicable)
```

The plugin shell carries no Python, no bin scripts, no MCP servers — it is pure packaging. All the substance lives in `skills/<name>/`, and each composed skill is independently understandable from its own files.

## How a composed skill enters this bundle

1. Author invokes `skill-authoring:skill-composer`'s `compose new --destination plugins/composed-skills/skills` from the project root
2. The agent collects name + intent + Surface + sources via dialogue, writes `composition.md`
3. `compose add-source` sparse-checks each exemplar into `skills/<name>/sources/<slug>/` and pins commits
4. The agent fills in the Goal, Surface, and Sources body sections
5. `compose build` scaffolds the initial SKILL.md + `scripts/__init__.py`
6. Agent refines SKILL.md directly + creates `_<verb>.md` workflow files matching the Surface entries
7. Commit lands on main; downstream consumers pick it up via `/plugin install` or `npx skills`

The plugin manifest's `skills: ["./skills/"]` glob means new compositions become discoverable automatically — no need to edit `plugin.json` per skill.

## Sources subdirectory lifecycle

`sources/` is **present during active development** to let the agent re-read exemplars when refining the composition. After finalization, `compose purge-sources` reclaims disk; the pinned commits stay in `composition.md` frontmatter so `compose refine` can auto-rehydrate against the same upstream snapshots.

For consumers installing the bundle, `sources/` may or may not be present depending on whether the maintainer purged it before committing. Consumers don't need it — they consume `SKILL.md`. Maintainers refining via `compose refine` will auto-rehydrate when needed.

## Bundle-level versioning

`composed-skills` follows the same `x.y.z` semver convention as other plugins in this marketplace (per `components/versioning.md`). Pre-commit hook auto-bumps `z` on commits that touch `skills/<name>/` (the same rule that bumps `ocd` and `skill-authoring:skill-composer`). Tagged releases bundle a snapshot of every skill at that point; downstream consumers on the stable channel pin to a tag and update deliberately.

## Drift between bundle releases and composition state

A composed skill's `composition.md` records pinned commits against upstream sources. If an upstream source drifts after the bundle is released, the consumer's installed copy of the skill still works — it pins what was vendored. The maintainer's `compose refine` workflow surfaces drift in their working copy; whether to refresh the skill is a deliberate design decision per skill, not an automatic upgrade.

## What this bundle doesn't do

- It is not a tool — it has no verbs, no scripts. It is packaging only.
- It does not enforce a theme — `composed-skills/skills/` accepts compositions of any domain. Thematic split (e.g., separate bundles for python-skills, frontend-skills) can happen later via `marketplace.json` if the bundle grows large enough to warrant subdivision.
- It does not auto-curate — a skill stays in the bundle until manually removed. Removal pattern: `git rm -r skills/<name>/` + commit. Downstream consumers get the removal on next install/update.
