# /ocd:setup rules uninstall

Remove deployed rule files from the chosen scope so they no longer auto-load into sessions.

## Arguments

`<target> [<target> ...] --scope <user | project>` or `--all --scope <user | project>`

- `<target>` — rule basename without `.md`; pass multiple to remove several at once
- `--all` — remove every deployed rule at the chosen scope; mutually exclusive with named targets
- `--scope` — required; deny-by-default

## Workflow

1. If --scope missing: AskUserQuestion — `user` vs `project`
2. If neither --all nor any {target} given:
    1. bash: `ocd-run setup rules status --scope {scope}` — surfaces what's currently deployed
    2. Render the deployed rules in the assistant response as a lettered list per `confirm-shared-intent`: `Q1 Which rules to remove?` with `A) <name>`, `B) <name>`, etc., plus a final `all` option
    3. Accept the user's reply as letters (e.g. `A, F, Q`), bare rule names, or `all`
    4. {targets} = list of resolved rule names from the user's choice; or `--all` if the user picks `all`
3. Confirm with the user — show {targets} (or `--all`), {scope}, what will be removed
4. bash: `ocd-run setup rules uninstall {targets} --scope {scope}` (or `--all` in place of {targets})
5. Surface the CLI output — per-file `current → absent` transitions

### Report

- Scope uninstalled from
- Files removed
- If nothing was deployed at {scope}: report that and skip
