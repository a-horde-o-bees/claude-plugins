# Release Synthesize

> Spawned-agent component: reads commits in {commit-range}, produces a Keep-a-Changelog entry with cross-commit deconfliction, and recommends a next version per the project methodology's bump-axis rules.
>
> Runs in isolated context — only the inputs it needs. Cross-commit deconfliction collapses add→refactor→retire chains to net-state rather than three separate entries. Defaults to Keep a Changelog 1.1.0 when {methodology} is silent on a question.

## Variables

- {commit-range} — git log range to read (e.g., `v0.1.0..HEAD`, or `HEAD` for first release)
- {current-version} — current manifest version string; the synthesizer applies the bump rule against this
- {methodology} — content of the project's `.claude/ocd/git/release.md`; defines CHANGELOG format, what counts as user-facing, and bump-axis decision rules

## Rules

- Apply cross-commit deconfliction — add → refactor → retire chains produce one net-state entry, not a sequential history
- Categorize per the methodology's CHANGELOG format (Keep a Changelog default: Added / Changed / Fixed / Removed); include only categories that have entries
- Skip non-user-facing commits — internal refactors, test infrastructure, doc fixes that don't change behavior, version-bump-only commits. Surface ambiguous calls explicitly rather than silently dropping or including
- Each entry is one line summarizing the net change; a few sentences if elaboration is needed
- Section heading: `## [{recommended-version}] - YYYY-MM-DD` (today's UTC date)
- Entries reference user-facing artifacts (skill names, MCP tools, file paths consumers see), not internal modules or private symbols
- Do not invent changes; every entry must trace to actual commits in {commit-range}
- Apply the methodology's bump-axis decision rules to recommend the next version — categorized changes are input, rules decide the axis. Surface uncertainty explicitly when categories straddle axes (e.g., Removed entries that may or may not be user-visible breaks)

## Process

1. Read commit history:
    1. {git-log-raw}: bash: `git log {commit-range} --format="%H%n%s%n%b%n--ENDCOMMIT--"` — full subjects + bodies
    2. {commits}: parsed list of {hash, subject, body} tuples from {git-log-raw}

2. {diffstat-raw}: bash: `git log {commit-range} --stat --format="%H %s"` — file-level scope per commit; used to weight which commits introduce user-facing surface area vs internal-only
3. Group commits by topic:
    1. The project's commit-message convention is `Topic — subject`; the prefix word groups commits naturally (e.g., "Transcripts —", "Principles —", "Docs —")
    2. Group by prefix; if no clear prefix, group by file scope from {diffstat-raw}

4. Apply cross-commit deconfliction within each group:
    1. Add → refactor → retire chains: if a feature was added in commit A and removed in commit C with intermediate commits B touching it, net state is "removed" (or "not present in this release at all")
    2. Add → enhance chains: if commits A and B both add to the same surface, combine into one entry capturing the final shape
    3. Rename chains: the entry describes the final name with a note about the rename if user-visible

5. Categorize per Keep-a-Changelog (or methodology's preference):
    - **Added** — new user-facing capabilities (skills, verbs, MCP tools, hooks, rules, conventions, configurations, file types)
    - **Changed** — modifications to existing user-facing behavior (renamed verbs, restructured output, new defaults, breaking interface changes)
    - **Fixed** — defect repairs visible to users (tool that previously errored now works, etc.)
    - **Removed** — capabilities that no longer exist
    - Skip categories with no entries

6. Recommend the next version:
    1. Read the methodology's bump-axis decision rules (e.g., "y bump for new user-facing capabilities; x bump for breaking changes; z bump for fixes only")
    2. Map the categorized changes from step 5 against those rules — pick the highest-precedence axis any category triggers (typically: x > y > z)
    3. {recommended-version}: apply the bump to {current-version} per the methodology's reset rules (e.g., "y bump resets z to 0")
    4. {bump-axis-rationale}: one or two sentences naming which categories drove the chosen axis (e.g., "y-bump: two Added entries for new user-facing capabilities; no Removed or breaking Changed entries triggered x")

7. Compose the CHANGELOG section. Apply /description-authoring and /concise-prose:
    1. Heading: `## [{recommended-version}] - YYYY-MM-DD`
    2. Optional one-line lead paragraph if the release has a coherent theme (e.g., "Skill-orchestrated reports + Q#/letter prompt convention")
    3. Categorized bullets per step 5
    4. Bullets concise but specific — name the thing, name the user-visible effect
    5. {changelog-entry}: composed markdown section

8. Flag ambiguity. Apply /honesty:
    1. If commits suggest a change but the user-facing effect is unclear: include the bullet annotated with `(needs review: <reason>)` so the operator catches it during the review gate
    2. If bump-axis decision is ambiguous (e.g., a Changed entry could be breaking or non-breaking): pick the more conservative axis (higher impact = larger bump) and flag the rationale with `(needs review: ...)`

    > Better to surface uncertainty than to confidently mis-categorize or mis-bump.

9. Return to caller:
    - {recommended-version}: computed next version per methodology rules
    - {bump-axis-rationale}: one-or-two-sentence justification for the chosen axis
    - {changelog-entry}: composed markdown section
    - {commits-considered}: count of commits in {commit-range}
    - {commits-deconflicted}: count of pairs/chains that collapsed
    - {ambiguity-flags}: count of `(needs review: ...)` entries

## Report

Return the recommended version, bump-axis rationale, and composed CHANGELOG section as the primary deliverables. Surface deconfliction and ambiguity counts so the caller knows how much synthesis judgment was applied.
