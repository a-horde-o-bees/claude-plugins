---
log-role: queue
---

# Composed-skills bundle integration with checkpoint and release flows

The `composed-skills` plugin shell exists and `compose new --destination plugins/composed-skills/skills` is the maintainer workflow for adding new compositions. Open question: how should `/checkpoint` and `/ocd:git release` integrate with the bundle?

Concrete questions:

- **Per-skill commits vs bundle-level releases.** Each composition lands as its own commit(s). The bundle's `plugin.json` version auto-bumps per commit (per `components/versioning.md`). Should `/checkpoint` treat a new composition as a release-triggering event, or does the auto-bump alone suffice and tagged releases stay deliberate?
- **Stable channel vs dev channel for composed-skills consumers.** Consumers pinning to a tag get a snapshot of every skill at that point; dev-channel consumers track main. Is the bundle's release cadence tied to the marketplace's, or independent?
- **Drift between a composed skill's pinned upstream commits and the bundle's release.** A composition's `composition.md` pins upstream source commits. If the upstream drifts after the bundle's last tag, downstream consumers still have the pinned version. Is that desired? Should `/ocd:git release` for the bundle surface drift to the maintainer before tagging?
- **`/checkpoint` discovery of new compositions.** Does `/checkpoint` need to know when a composition is "ready to publish" vs still draft? Currently filesystem truth (SKILL.md present) is the signal — but a draft composition with composition.md and no SKILL.md is technically a non-functional skill in the bundle. Should `/checkpoint` warn about partial compositions?

Captured in `plans/composed-skills-workflow.md` under "Open: checkpoint integration" — promoted to idea log so it's queued for action when the workflow has a few real compositions exercising it.
