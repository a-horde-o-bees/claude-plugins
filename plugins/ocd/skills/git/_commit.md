# Commit

> Commit working tree changes grouped by topic. Each commit is one coherent topic for readable history.

> Fully automated. When grouping is ambiguous, keep changes together rather than splitting incorrectly.

### Dependencies

1. {dependencies}:
    - [[description-authoring]]
    - [[concise-prose]]
    - [[honesty]]
2. For each {dependency} in {dependencies}:
    1. {found}: bash: `find ~/.claude <project>/.claude -path "*dependencies/{dependency}.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`
    2. If {found} is empty:
        1. {scope}: `<project>` if `<skill-base>` starts with `<project>`, else `~`
        2. bash: `cp <skill-base>/_dependencies/{dependency}.md {scope}/.claude/dependencies/{dependency}.md`
        3. {path}: the cp target
    3. Else: {path}: first of {found} — prefer user-scope; `rules/dependencies/` over plain `dependencies/`; user-scope skills skip project matches
    4. Read {path} if not in context

### Rules

- Group for readable history: single commit when all changes are one coherent topic or grouping is ambiguous; multi-commit only when topics are clearly separable
- No minimum commit size — a single-file change is a valid commit if it's a distinct topic
- Commit messages describe end-state results, not the change journey
- Untracked files group with related changes; surface to user only when suspicious (generated directories, credentials, build artifacts)
- Stage specific files by name; never `git add -A` or `git add .`
- Commit order: dependencies first, consumers after
- Never amend previous commits unless the user explicitly requests it
- Never force-push or run destructive git operations

### Process

1. Analyze working tree:
    1. bash: `git status` — collect modified, deleted, untracked files
    2. If no changes: Exit to user: clean working tree
    3. bash: `git diff --stat` — understand scope of changes
    4. bash: `git log --oneline -5` — capture recent commit message style

2. {suspicious-untracked}: untracked files matching suspicious patterns (large generated directories missing from `.gitignore`, credentials, build artifacts)
3. If {suspicious-untracked} non-empty: surface to user before committing — confirm whether to include, exclude, or .gitignore

4. {commit-groups}: group changes by topic — consider:
    - Tests with code (test files group with code they test)
    - Configuration with implementation (config changes group with consuming code)
    - Related directories (files in the same directory likely share a topic)

    Single group when changes are one coherent topic or grouping is ambiguous; multi-group only when topics are clearly separable. Multi-group ordering: dependencies first, consumers after.

5. {commit-messages}: draft one message per {commit-groups} entry following project's recent commit message style; describe end-state results

6. {co-author}: bash: `git config --get user.claude-coauthor`

7. For each {group} in {commit-groups}:
    1. bash: `git add <files-in-group>`
    2. {message}: corresponding entry from {commit-messages}; if {co-author} is `true`, append `Co-Authored-By:` trailer with current model name and `<noreply@anthropic.com>`
    3. bash: `git commit -m "{message}"`

8. {final-status}: bash: `git status --short`

### Report

Return to caller:

- Per-commit: topic, files included, message
- Summary: total commits made
- {final-status}: remaining changes if any, or `clean tree`
