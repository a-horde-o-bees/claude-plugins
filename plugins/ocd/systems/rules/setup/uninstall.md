# /ocd:setup rules uninstall

Remove deployed rule files from the chosen scope so they no longer auto-load into sessions.

## Arguments

`<target> --scope <user | project>`

- `<target>` — rule basename without `.md`, or `all` to remove every deployed rule at the chosen scope
- `--scope` — required; deny-by-default

## Workflow

1. If no arguments: present usage and the rules currently deployed at each scope
2. If --scope missing: ask the user which scope to uninstall from
3. If {target} missing or invalid: list rules deployed at {scope} and ask the user which to remove — accept multiple via lettered selection or `all`
4. Confirm with the user — show {target}, {scope}, what will be removed
5. bash: `ocd-run setup rules uninstall {target} --scope {scope}`
6. Surface the CLI output — per-file `current → absent` transitions

### Report

- Scope uninstalled from
- Files removed
- If nothing was deployed at {scope}: report that and skip
