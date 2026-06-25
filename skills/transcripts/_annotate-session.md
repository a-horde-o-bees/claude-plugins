# Annotate session

Author the per-exchange **descriptions** for one transcripts session. The apply-over-queue fan-out runs this across many sessions; it also runs standalone for one. Each spawn reads and writes only its own session, so parallel runs never contend.

Descriptions only — never assign topics. Topics come from a separate global pass over every description at once; a coherent vocabulary can't be set one session at a time.

## Target contract

You are given exactly one TARGET — a transcripts session id (a queue item, or a session id for a standalone run). Operate only on TARGET. Never read, reference, or depend on another session.

## Path

The commands hard-code the absolute path `/home/dev/.claude/skills/transcripts/exchanges.py`. apply-over-queue consumes this file raw, outside the dispatcher that resolves `${CLAUDE_SKILL_DIR}`. `exchanges.py` is a standalone stdlib script — `uv run <path>` runs it from any directory.

## Process

1. {todo}: Bash: `uv run /home/dev/.claude/skills/transcripts/exchanges.py list --session TARGET --undescribed --bodies`
    — each row is an undescribed exchange: its `uuid` and a `text` array of the exchange's turns in time order, each `{role, text}` (`user` = the typed prompt and any folded interjections, `agent` = the assistant's responses). `--undescribed` excludes the keyless `(continuation)` pseudo-exchange, so {todo} never holds one.
2. If {todo} is empty: Exit process — TARGET is fully described; make no writes.
3. {descriptions}: an empty map, accumulated below.
4. For each {row} in {todo}:
    1. {description}: Apply: /description-authoring, /concise-prose:
        1. Read {row}'s `text` array in full and write a one-line summary of what the exchange did.
        2. **Past tense, always** — a completed action, since the work is done by the time it is read and the summaries feed billing reports. Lead with a past-tense verb and keep every clause past tense (`Traced the residual and patched the routing`, not `Traces…and patches…`; not the gerund `Tracing…`).
    2. Add `{row.uuid}: {description}` to {descriptions}.
5. Persist: Bash: `uv run /home/dev/.claude/skills/transcripts/exchanges.py describe --set '{descriptions}'`

> Writes land in `annotations.db` `exchange.description`, keyed by UUID — the store survives raw-DB rebuilds, re-attaching with no remap.
