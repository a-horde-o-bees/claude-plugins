# Sandbox: ocd/research-migration

Migrate the existing `logs/research/` subjects (`claude-marketplace`, `mcp`) into the new research format and system landed by the recent `sandbox/log-research` merge.

## Pointers

- `logs/research/claude-marketplace/` — substantial 54-sample marketplace research (`consolidated.md`, `context/`, `samples/`, `resample-corrections.md`, `survey-missing-factors.md`)
- `logs/research/mcp/` — earlier research subject (`consolidated.md`, `context/`, `samples/`, `scripts/`)
- `logs/research/_template.md`, `logs/research/_samples-template.md`, `logs/research/_scripts/` — current templates and shared scripts at the research-type root
- `plugins/ocd/systems/log/templates/research/` — source templates (canonical; deployed copies live under `logs/research/`)
- Merge commit `92793f6 Merge pull request #6 from a-horde-o-bees/sandbox/log-research` on origin/main — the change that introduced the new system; read it first to understand what shape is now expected
- `TASKS.md` — graduate this work out via a checked entry once both subjects land

## Tasks

- [ ] Read the `sandbox/log-research` merge commit (and any subsequent fixes) to characterize the new format end-to-end — template shape, samples shape, any new tooling, any directory-layout changes
- [ ] Diff current `logs/research/_template.md` and `_samples-template.md` against the new templates under `plugins/ocd/systems/log/templates/research/` — identify the structural delta that migration must absorb
- [ ] Inventory `claude-marketplace/` — files, sample count, non-conforming entries (e.g. `resample-corrections.md`, `survey-missing-factors.md`, `context/`)
- [ ] Inventory `mcp/` — same
- [ ] Decide migration strategy per subject: in-place reshape vs. rebuild from notes. Surface to user if scope is unclear
- [ ] Migrate `claude-marketplace` to new format — preserve evidence, restructure as needed
- [ ] Migrate `mcp` to new format
- [ ] Verify migrated subjects work under any new tooling the log-research merge added (e.g. parse/render/lint commands)
- [ ] Sweep cross-references — `MARKETPLACE-STANDARDS.md`, `TASKS.md`, idea logs, anywhere else that points into `logs/research/`
- [ ] Decide whether `logs/research/_scripts/` belongs under the new system or should move (e.g. into `plugins/ocd/systems/log/scripts/research/` if the new system relocates shared tooling)

## Open Questions

- What exactly changed in the log-research merge? (read the merge first, then refine this section into Tasks)
- Do the migrated subjects need a one-shot tooling pass (e.g. format conversion script), or are they small enough for hand migration?
- Are the auxiliary files in `claude-marketplace/` (`resample-corrections.md`, `survey-missing-factors.md`) part of the new format's vocabulary, or legacy artifacts to retire/repath?
