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

2. If {scope} missing: {scope}: AskUserQuestion — `user` vs `project`

3. If neither {all} nor any {target} given:
    1. {catalog}: bash: `uv run --directory <skill-base> -m scripts.rules list`
    2. Render {catalog} in chat as a lettered list per [[confirm-shared-intent]]: `Q1 Which rules to install?` with `A) <name> — <description>`, `B) ...`, plus a final `all` option
    3. {reply}: accept user's response as letters, bare rule names, or `all`
    4. If {reply} is `all`: {all}: true
    5. Else: {targets}: rule names resolved from {reply}

4. {approval}: AskUserQuestion — confirm or cancel; show {targets} (or `--all`), {scope}, and what's about to deploy

5. If {approval} is cancel: Exit to user: install cancelled

6. {result}: bash: `uv run --directory <skill-base> -m scripts.rules install {targets} --scope {scope} [--force]` (or `--all` in place of {targets})

7. Surface {result} to the user.

8. If any file in {result} ended `divergent` (no `--force` passed): tell the user to re-run with `--force` to overwrite the drifted copy.

### Report

- Scope deployed to
- Files deployed and state transitions (`absent → current`, `divergent → current`, `current → current`)
- Any divergent files left untouched when `--force` was not passed
