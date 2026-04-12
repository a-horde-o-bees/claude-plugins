# Backfill decision rationale from transcripts

## Purpose

Several architectural decisions lack the reasoning behind them — only the final choice is documented. Backfilling requires extracting context from past session transcripts.

The transcript extraction script is in ~/projects/msp-psa-aggregator/.claude/scripts/ (to be imported).

Known gaps:
- Script execution model — why shebangs + chmod was abandoned for python3 prefix invocation
- Any conventions/rules where only the "what" is documented but the "why" and "what was tried" are missing
