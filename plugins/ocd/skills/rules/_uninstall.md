# Uninstall

> Workflow component for the `uninstall` verb of /ocd:rules. Removes deployed rule files from the chosen scope so they no longer auto-load.

### Variables

- {args} — CLI args: `<name>... --scope <user|project>` or `--all --scope <user|project>`

### Rules

- `--scope` is required (deny-by-default); prompt if missing
- Without explicit targets and without `--all`, walk the user through deployed-rules selection

### Process

1. Parse {args}; extract {scope}, {targets}, {all}.

2. If {scope} missing: {scope}: AskUserQuestion — `user` vs `project`

3. If neither {all} nor any {target} given:
    1. {deployed}: bash: `uv run --directory <skill-base> -m scripts.rules status --scope {scope}`
    2. Render {deployed} as a lettered list per [[confirm-shared-intent]]: `Q1 Which rules to remove?` with `A) <name>`, `B) ...`, plus a final `all` option
    3. {reply}: accept user's response as letters, bare rule names, or `all`
    4. If {reply} is `all`: {all}: true
    5. Else: {targets}: rule names resolved from {reply}

4. {approval}: AskUserQuestion — confirm or cancel; show {targets} (or `--all`), {scope}, what will be removed

5. If {approval} is cancel: Exit to user: uninstall cancelled

6. {result}: bash: `uv run --directory <skill-base> -m scripts.rules uninstall {targets} --scope {scope}` (or `--all` in place of {targets})

7. Surface {result} to the user.

### Report

- Scope uninstalled from
- Files removed (with `current → absent` transitions)
- If nothing was deployed at {scope}: report that and exit
