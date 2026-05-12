# Install

> Workflow component for the `install` verb of /ocd:rules. Deploys rule canonicals as always-on agent guidance at the chosen scope.

### Variables

- {args} — CLI args: `<name>... --scope <user|project> [--force]` or `--all --scope <user|project> [--force]`

### Rules

- `--scope` is required (deny-by-default); prompt if missing
- Without explicit targets and without `--all`, walk the user through catalog selection
- `--force` overwrites deployed copies that have drifted from the canonical

### Process

1. Parse {args}; extract {scope}, {targets}, {force}, {all}.
2. If {scope} missing:
    1. AskUserQuestion — `user` vs `project`
    2. {scope} = user's answer
3. If neither {all} nor any {target} given:
    1. bash: `uv run -m scripts.rules list` — surface the catalog
    2. Render in chat as a lettered list per [[confirm-shared-intent]]: `Q1 Which rules to install?` with `A) <name> — <description>`, `B) ...`, plus a final `all` option
    3. Accept the user's reply as letters, bare rule names, or `all`
    4. {targets} = resolved list of rule names; or {all} = true if user picked `all`
4. Confirm with the user — show {targets} (or `--all`), {scope}, and what's about to deploy
5. Invoke — bash: `uv run -m scripts.rules install {targets} --scope {scope} [--force]` (or `--all` in place of {targets})
6. Surface the per-file transition output to the user
7. If any file remained `divergent` (no `--force`): tell the user to re-run with `--force` to overwrite

### Report

- Scope deployed to
- Files deployed and state transitions (`absent → current`, `divergent → current`, `current → current`)
- Any divergent files left untouched when `--force` was not passed
