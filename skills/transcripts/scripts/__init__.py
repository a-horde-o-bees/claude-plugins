"""transcripts skill — internal package.

Data is the events table (one row per JSONL event, idempotent on file+line)
plus two derived views: events_with_gaps (exchange + gap_s columns) and
chat_messages (filtered to user/assistant text). Re-runs of ingest only add
newly-appended lines from active transcripts.

CLI entry is __main__.py — invoke via `python -m scripts` from the skill
directory (the parent of this package).
"""
