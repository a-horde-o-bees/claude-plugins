# Session branching wrapper: use rewind/fork as context management for O(C + NF) multi-file agent workflows

## Purpose

Current multi-file agent workflows spawn N independent agents that each redundantly load the full criteria stack. Cost is N × (C + F). Session branching could reduce this to C + (N × F).

Core insight: Claude Code session rewind clears context (validated experimentally). Session branching can be used as programmatic context management.

Implementation: external orchestrator (not a skill — skills run within single sessions). Options: Claude API directly, Agent SDK, or headless Claude Code automation.

Constraint: /rewind is interactive-only — no programmatic invocation. The checkpoint persistence on disk may be exploitable but the interactive lock is a constraint to work around.
