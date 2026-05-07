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

1. If --scope missing: AskUserQuestion — `user` vs `project` (2 options fits the tool cleanly)
2. If neither --all nor any {target} given:
    1. bash: `ocd-run setup rules list` — surfaces the catalog with one-line taglines
    2. Render the catalog in the assistant response as a lettered list per `confirm-shared-intent`: `Q1 Which rules to install?` with `A) <name> — <tagline>`, `B) <name> — <tagline>`, etc., plus a final `all` option
    3. Accept the user's reply as letters (e.g. `A, F, Q`), bare rule names, or `all`. For full-purpose detail on any item, point at `ocd-run setup rules show <name>`.
    4. {targets} = list of resolved rule names from the user's choice; or `--all` if the user picks `all`
3. Confirm with the user — show {targets} (or `--all`), {scope}, and what's about to deploy
4. bash: `ocd-run setup rules install {targets} --scope {scope} [--force]` (or `--all` in place of {targets})
5. Surface the CLI output to the user — per-file `absent → current` / `current → current` / `divergent → current` transitions
6. If any file remained `divergent` (no --force): tell the user to re-run with `--force` to overwrite

### Report

- Scope deployed to
- Files deployed and their state transitions
- Any divergent files left untouched (when --force was not passed)
