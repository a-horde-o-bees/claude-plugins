# /ocd:setup rules uninstall

Remove deployed rule files from the chosen scope so they no longer auto-load into sessions.

## Arguments

`<target> [<target> ...] --scope <user | project>` or `--all --scope <user | project>`

- `<target>` — rule basename without `.md`; pass multiple to remove several at once
- `--all` — remove every deployed rule at the chosen scope; mutually exclusive with named targets
- `--scope` — required; deny-by-default

## Workflow

1. If no arguments: present usage and run `ocd-run setup rules status` to show what's currently deployed
2. If --scope missing: ask the user which scope to uninstall from
3. If neither --all nor any {target} given: list rules deployed at {scope} via `ocd-run setup rules status --scope {scope}`, ask the user which to remove — accept multiple via lettered selection or `all`. Translate the user's choice into either a list of named targets or `--all`.
4. Confirm with the user — show {targets} (or `--all`), {scope}, what will be removed
5. bash: `ocd-run setup rules uninstall {targets} --scope {scope}` (or `--all` in place of {targets})
6. Surface the CLI output — per-file `current → absent` transitions

### Report

- Scope uninstalled from
- Files removed
- If nothing was deployed at {scope}: report that and skip
