# Setup: Permissions

Optional subflow invoked from `/ocd:setup guided` when the user opts into permissions configuration. Deploys plugin-recommended permission patterns to the chosen scope, then optionally cleans redundant patterns from the opposite scope.

## Process

1. Status — bash: `ocd-run setup permissions status`
2. Present report with scope education:

    - **Project scope** (`.claude/settings.json`) — applies to this project only; version controlled; shared with collaborators
    - **User scope** (`~/.claude/settings.json`) — applies to all projects on this machine; personal preference; not shared

3. Ask scope — AskUserQuestion with options: `["Project scope", "User scope"]`
4. If user chose "Project scope": {scope} = project
5. Else: {scope} = user
6. Install — bash: `ocd-run setup permissions install --scope {scope}`
7. Present install results
8. Analyze — bash: `ocd-run setup permissions analyze`
9. If redundancy count > 0:
    1. {other-scope} = opposite of {scope}
    2. If {other-scope} is `user`: Present warning — removing from user scope affects all projects on this machine
    3. Ask cleanup — AskUserQuestion with options: `["Clean {other-scope} scope", "Keep both"]`
    4. If cleanup chosen:
        1. Clean — bash: `ocd-run setup permissions clean --scope {other-scope}`
        2. Present clean results
