# Log: Research

Run research-corpus analysis against samples under `logs/research/<subject>/samples/`. Verbs dispatch via the `ocd-run log research` CLI — this fragment is pure routing.

## Process

1. `{remainder}` = $ARGUMENTS with the leading `research` token removed
2. If `{remainder}` is empty: Exit to user: research requires a verb — expected `check`, `count-sections`, `consolidate`, or `compliance`; see `ocd-run log research --help`
3. bash: `ocd-run log research {remainder}`
4. Present CLI output to user — no summarization or reformatting
5. Return to caller

## Report

- Exit code from the CLI — 0 on pass, 1 on any failure
- Stdout / stderr from CLI surfaced as-is so paths, chain keys, and diagnostics stay precise
