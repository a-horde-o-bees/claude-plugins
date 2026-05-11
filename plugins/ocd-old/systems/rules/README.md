# rules

Always-on agent guidance for the ocd plugin. Each rule template is a markdown file that Claude Code auto-loads into every session when deployed at user or project scope.

## How it works

Templates live in `templates/` as the source of truth. Installing a rule deploys its template to the chosen scope:

- **User scope** — `~/.claude/rules/ocd/<rule>.md`. Auto-loads in every project.
- **Project scope** — `<project>/.claude/rules/ocd/<rule>.md`. Auto-loads only in that project.

Each rule is independent. Users can pick any subset to install at either scope, and the same rule may live at one scope, both, or neither.

## Usage

Through the setup skill:

```
/ocd:setup rules                                    # rules' usage
/ocd:setup rules list                               # catalog with one-line taglines
/ocd:setup rules show <rule>                        # full body of one rule
/ocd:setup rules install <rule> --scope project     # install one rule at project
/ocd:setup rules install --all --scope user         # install every rule at user
/ocd:setup rules uninstall <rule> --scope project   # remove one
/ocd:setup rules status                             # report install state per scope
```

`<rule>` is the basename of any file in `templates/` (with or without `.md` extension). Use `--all` to operate on every template.

## Available rules

Run `/ocd:setup rules list` to scan the catalog and `/ocd:setup rules show <name>` for any rule's full body.

## License

MIT
