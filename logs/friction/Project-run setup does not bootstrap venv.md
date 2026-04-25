# Project-run setup does not bootstrap venv

`bin/project-run tests` fails on a fresh checkout (or fresh sibling worktree) with a corrective message telling the user to `uv venv` themselves, instead of the project's `setup` verb doing it as part of "configure local dev settings."

## Scope

`bin/project-run setup` documents itself as "configure project-local dev settings (git hookspath, etc.)" (`tools/__main__.py:41`), and `setup_project()` in `tools/setup/_orchestration.py` runs idempotent project-local setup steps. Today it only configures `git core.hookspath`. The venv resolver in `tools/testing/_venv.py:28` raises with corrective text "bootstrap with `uv venv`" — relying on the user to run a separate command rather than threading it through `setup`.

Surfaced when running `bin/project-run tests --project` in a sandbox sibling worktree. Worktrees share the object store but not `.venv/`, so every new sibling needs the venv materialized; the friction recurs once per sibling.

## Fix direction

Fold venv bootstrap into `setup_project()`:

- `uv venv` to create `.venv/` if absent (idempotent — uv exits cleanly if it exists)
- `uv sync` to install the dev dependency group declared in `pyproject.toml`
- Verify `uv` is on PATH first; if not, surface a corrective install command per the *System and Global Tool Dependencies* convention

`setup` then becomes the single bootstrap path: hookspath + venv + deps in one verb. The `_venv.resolve_project_venv` corrective message can update to point at `bin/project-run setup` instead of raw `uv venv`.
