# Python dependencies

Add the package to the target plugin's `pyproject.toml` under `[project.dependencies]`. The plugin's `SessionStart` hook detects the change on next session start (via `diff -q` against the cached copy) and reinstalls into the plugin's isolated venv automatically.

Prerequisite: `uv` must be installed on the user's system.
