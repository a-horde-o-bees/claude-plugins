---
created: 2026-04-11T23:47:37.971851+00:00
---

# Backfill decision history from transcripts; known gap includes script execution model (shebangs/chmod vs python3 prefix)

Several architectural decisions lack the reasoning behind them — only the final choice is documented. Backfilling requires extracting context from past session transcripts.

The transcript extraction script is in ~/projects/msp-psa-aggregator/.claude/scripts/ (to be imported).

Known gaps:
- Script execution model — why shebangs + chmod was abandoned for python3 prefix invocation
- Any conventions/rules where only the "what" is documented but the "why" and "what was tried" are missing
