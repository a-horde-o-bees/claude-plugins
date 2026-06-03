# Skill Linting Criteria

The checkable criteria a project skill linter enforces over skill folders and their plugin manifests. The `skill-linter` skill runs checks against this list. Each criterion notes whether its check is ready or pending.

## Cross-plugin invocation resolution

Every cross-plugin `/<skill>` invocation in a skill body resolves to a skill in the same plugin or in a plugin declared in this plugin's `plugin.json` dependencies. Invocations resolving to upstream skills outside this repo are out of scope. [script: `scripts/check_plugin_deps.py` — pending]

Pending research: the resolution model is unsettled. `/skill` resolution is global at runtime, so static analysis can't infer from the invocation alone whether a declared dep is required — always-on skills, namespace-qualified vs. bare invocations, and project-level wrappers each complicate the contract. Until the model is settled the check runs on demand here, not in pre-commit.

## Recognized skill-folder contents

A skill folder is `SKILL.md` plus, optionally: `_<verb>.md` component files, `assets/`, `scripts/`, `sources/` (vendored upstream), and a **`tests/`** subfolder carrying the skill's own verification (e.g. a runnable harness + README). `tests/` and `sources/` are not part of the skill's invocation surface — checks that scan skill bodies (e.g. cross-plugin resolution) skip both. A future folder-structure check must treat `tests/` as allowed, not extraneous.
