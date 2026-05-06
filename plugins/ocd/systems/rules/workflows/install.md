# /ocd:setup rules install

Deploy rule templates as always-on agent guidance at the chosen scope.

Each rule is an independent template that auto-loads into every Claude Code session when present at one of these locations:

- User scope: `~/.claude/rules/<plugin>/<rule>.md` — applies to every project the user works in
- Project scope: `<project>/.claude/rules/<plugin>/<rule>.md` — applies only when working in that project

## Arguments

`<target> [<target> ...] --scope <user | project> [--force]` or `--all --scope <user | project> [--force]`

- `<target>` — rule basename without `.md` (e.g. `honesty`, `purpose-statement`); pass multiple to install several at once
- `--all` — deploy every available rule template; mutually exclusive with named targets
- `--scope` — required; deny-by-default. Picks where the rules land
- `--force` — overwrite deployed copies that have drifted from the current template

## Workflow

1. If no arguments: present usage and run `ocd-run setup rules list` to surface the catalog with purposes
2. If --scope missing: ask the user which scope; offer user, project
3. If neither --all nor any {target} given: run `ocd-run setup rules list`, present the catalog, ask the user which to install — accept multiple via lettered selection or `all`. Translate the user's choice into either a list of named targets or `--all`.
4. Confirm with the user — show {targets} (or `--all`), {scope}, and what's about to deploy
5. bash: `ocd-run setup rules install {targets} --scope {scope} [--force]` (or `--all` in place of {targets})
6. Surface the CLI output to the user — per-file `absent → current` / `current → current` / `divergent → current` transitions
7. If any file remained `divergent` (no --force): tell the user to re-run with `--force` to overwrite

### Report

- Scope deployed to
- Files deployed and their state transitions
- Any divergent files left untouched (when --force was not passed)
