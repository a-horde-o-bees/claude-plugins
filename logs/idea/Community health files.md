# Community health files

Add `SECURITY.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md` at project root when external contributors start showing up. Optional polish; not a release blocker.

## Context

Migrated from the former `claude-marketplace--diff.md` audit's Open-items list when the diff doc retired into `MARKETPLACE-STANDARDS.md`. The standards doc covers everything in the alignment audit except this one deferred item.

## Why deferred

Community health files populate GitHub's Community Standards checklist and link from issue/PR templates. Their signal value is primarily social — they tell external contributors that a project has a reporting channel, contribution process, and behavioral norms. For a personal experimental project with no external contributors, they'd currently signal a community that doesn't exist.

Cost to add is low (an hour or two of boilerplate) but timing matters: adding them before there's any community to govern is premature.

## When to reach for this

- An external contributor files the first PR or issue — adopt `CONTRIBUTING.md` to scope the process.
- A security report arrives by email — adopt `SECURITY.md` with GitHub Security Advisories as the reporting channel.
- The project gains enough visibility to warrant a behavioral norm — adopt `CODE_OF_CONDUCT.md` using Contributor Covenant v2.1 (pointer-style file to sidestep content-filter issues with the full covenant text).

## Shape when added

Per the earlier methodology discussion:

- **SECURITY.md** — supported versions (latest tag only; no backports), reporting channel (GitHub Security Advisories + optional email), response expectation (best-effort, no SLA).
- **CONTRIBUTING.md** — pointer document. Links to README for setup, CLAUDE.md for conventions, `rules/ocd/testing.md` for test expectations. One-paragraph PR process note.
- **CODE_OF_CONDUCT.md** — short adoption of Contributor Covenant v2.1 by URL reference rather than reproducing the full text (avoids content-filter trips during generation). Names the enforcement contact.

## Related

- `rules/ocd/system-docs.md` filename-case rule confirms these belong in all-caps at project root.
- Pattern doc §21 notes ~6/54 adoption of a community-health bundle — rare but signals "serious project."
