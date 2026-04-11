"""Default log types bootstrapped on first init.

Each entry maps a type name to its routing instructions — the agent-facing
guidance that explains when to reach for this log type and what qualifies.
The bootstrap is idempotent: re-running init against an already-populated
types table is a no-op. User edits to type instructions survive re-init
because only missing types are inserted.
"""

DEFAULT_TYPES = [
    {
        "name": "decision",
        "instructions": (
            "Non-obvious choices where alternatives were considered and rejected, "
            "or where the reasoning is not derivable from code or conventions. "
            "The goal is preventative — keep future work from re-exploring "
            "rejected alternatives.\n\n"
            "What qualifies: a choice worth preserving for a future session that "
            "will not have access to the conversation where it was made.\n\n"
            "What does NOT qualify: implementation details visible in the code, "
            "choices dictated by convention, standard patterns obvious from "
            "reading the source. If a fresh agent can derive the answer from the "
            "code, it is not a decision.\n\n"
            "Capture rationale: the summary alone is rarely enough. Include "
            "detail_md with context (what prompted it), options (alternatives "
            "with trade-offs), the decision (what was chosen and why), and "
            "consequences (what this enables and constrains). A decision without "
            "rationale devolves into a setting — future agents cannot tell "
            "whether the conditions still hold.\n\n"
            "Lifecycle: kept current with project state, not preserved as a "
            "historical archive. Update entries when direction changes; remove "
            "entries when the decision is no longer relevant."
        ),
    },
    {
        "name": "friction",
        "instructions": (
            "Process gaps encountered during work: a rule the system forced you "
            "to violate, a missing capability, a broken process step, unexpected "
            "state, or a runtime issue where investigating inline would derail "
            "the current task.\n\n"
            "Every friction encounter is a Fix-or-Log decision. Make the choice "
            "actively — never default to logging.\n\n"
            "Fix now when the current context is better equipped than a future "
            "session would be: the fix is clear from current context, the "
            "spider-web of related information informing the discovery would be "
            "lost to deferral, and the fix is simple enough that doing it now "
            "won't derail the current task.\n\n"
            "Log and continue when the fix would derail current work (requires "
            "investigation, touches unrelated systems, demands design decisions "
            "beyond current scope), the friction is simple enough to describe "
            "and act on later without needing current context, or the fix "
            "depends on work outside the current task.\n\n"
            "When logging: add a system:<name> tag naming the system the "
            "friction is about, not the workflow that surfaced it. Friction "
            "with navigator discovered during evaluate-governance goes to "
            "system:navigator, not system:evaluate-governance.\n\n"
            "Lifecycle: friction is a queue, not an archive. Call log_remove "
            "when the underlying cause is fixed and verified."
        ),
    },
    {
        "name": "problem",
        "instructions": (
            "Observed defects or issues noticed mid-work that need investigation "
            "later. Concrete, unexpected, and wrong — not rule violations (those "
            "are friction), not exploratory ideas (those are ideas).\n\n"
            "What qualifies: a defect the current context noticed but cannot "
            "immediately address — wrong output, broken invariant, inconsistent "
            "state, performance regression, incorrect behavior that the present "
            "task does not have scope to fix.\n\n"
            "What does NOT qualify: rule violations the system flagged (those "
            "are friction), ideas for new capabilities (those are ideas), or "
            "settled choices with rationale (those are decisions).\n\n"
            "Capture fast — a three-second log beats a ten-minute detour. Use "
            "detail_md only when substantial context (reproduction steps, "
            "constraints observed, suspected root cause) would be lost in a "
            "one-line summary.\n\n"
            "Lifecycle: problems are a queue. Call log_remove when the problem "
            "is resolved or moved to an external tracker."
        ),
    },
    {
        "name": "idea",
        "instructions": (
            "Exploratory ideas, future work, and improvement suggestions. "
            "Project-scoped ideas tied to the current codebase that should be "
            "captured for later without breaking flow.\n\n"
            "What qualifies: a capability not yet built, a refactor worth "
            "exploring, an optimization worth investigating, a direction worth "
            "pursuing. Speculative or concrete — both belong here as long as "
            "they apply to this project.\n\n"
            "What does NOT qualify: observed defects (those are problems), rule "
            "violations (those are friction), settled choices (those are "
            "decisions). User-specific knowledge (preferences, personal context) "
            "belongs in Claude memory, not here. Cross-project ideas not tied to "
            "any particular codebase also belong in memory.\n\n"
            "Capture fast — a three-second log beats a ten-minute detour. Use "
            "detail_md only when substantial context (approaches explored, "
            "blockers, prerequisites) would be lost in a one-line summary.\n\n"
            "Lifecycle: ideas are a holding area. Call log_remove when an idea "
            "is acted on, rejected, or moved to an external tracker."
        ),
    },
]
