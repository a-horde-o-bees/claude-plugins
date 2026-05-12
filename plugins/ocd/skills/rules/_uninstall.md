# Uninstall

> Workflow component for the `uninstall` verb of /ocd:rules. Removes deployed rule files from the chosen scope so they no longer auto-load.

### Variables

- {args} — CLI args: `<name>... --scope <user|project>` or `--all --scope <user|project>`

### Rules

- `--scope` is required (deny-by-default); prompt if missing
- Without explicit targets and without `--all`, walk the user through deployed-rules selection

### Process

1. Parse {args}; extract {scope}, {targets}, {all}.
2. If {scope} missing:
    1. AskUserQuestion — `user` vs `project`
    2. {scope} = user's answer
3. If neither {all} nor any {target} given:
    1. bash: `uv run -m scripts.rules status --scope {scope}` — surface what's currently deployed
    2. Render deployed rules as a lettered list per [[confirm-shared-intent]]: `Q1 Which rules to remove?` with `A) <name>`, `B) ...`, plus a final `all` option
    3. Accept letters, bare names, or `all`
    4. {targets} = resolved list; or {all} = true
4. Confirm with the user — show {targets} (or `--all`), {scope}, what will be removed
5. Invoke — bash: `uv run -m scripts.rules uninstall {targets} --scope {scope}` (or `--all` in place of {targets})
6. Surface the per-file transition output

### Report

- Scope uninstalled from
- Files removed (with `current → absent` transitions)
- If nothing was deployed at {scope}: report that and skip
