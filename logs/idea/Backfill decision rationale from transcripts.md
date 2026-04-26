# Backfill decision rationale from transcripts

Several architectural decisions lack the reasoning behind them — only the final choice is documented. Backfilling requires mining context from past session transcripts.

The extraction substrate is now in place: `/ocd:transcripts chat_export` produces simplified `<stem>_chat.json` companions beside each `~/.claude/projects/<project>/*.jsonl` source, and `/ocd:transcripts project_path` returns the directory the current session can read its own history from. Mining — querying the extracted chat for decision context — is the layer above; this idea is the unbuilt half.

Known gaps to investigate via mined transcripts:

- Script execution model — why shebangs + chmod was abandoned for python3 prefix invocation
- Conventions, rules, and architectural choices where only the "what" is documented but the "why" and "what was tried" are missing

## Possible shapes for the mining layer

- A `/retrospective`-style skill that accepts a topic and surfaces transcript fragments mentioning it, leaving classification and persistence to the user.
- A new `/ocd:transcripts mine <query>` verb that filters extracted chat by date range, project, and keyword.
- A general full-text search index over `_chat.json` files, decoupled from the transcripts skill.
