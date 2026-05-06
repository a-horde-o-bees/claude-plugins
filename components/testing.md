# Project testing

How to run the test suite from this repository. Test-authoring discipline lives in the `testing.md` rule under rules/templates/.

## All tests

```
bin/project-run tests
```

Scope flags:

- `--plugin <name>` — single plugin's suite
- `--project` — project-level tests only

Unknown flags forward verbatim to pytest:

```
bin/project-run tests --plugin ocd --run-agent -v
```

A leading `--` separator is also accepted.

## Tests at a clean ref

```
bin/project-run sandbox-tests --ref <ref>
```

Runs the suite in a detached worktree at the given ref. The worktree is always removed before return.

## Layout

- Project tests in `tests/`
- Per-plugin tests under `tests/plugins/<plugin>/` isolated by `pythonpath`
- Plugin pytest configs at `tests/plugins/<plugin>/pyproject.toml` under `[tool.pytest.ini_options]`
- Project pytest config at root `pyproject.toml`
