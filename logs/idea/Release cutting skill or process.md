# Release cutting skill or process

## Purpose

Codify the release-cutting workflow established during the v0.1.0 release into a repeatable process — either as a skill (`/ocd:release`) or as documented procedure in CLAUDE.md.

## Context

The v0.1.0 release was cut manually through a series of steps coordinated across two branches. The steps worked well but were ad-hoc — a future release would require re-deriving them. Capturing the pattern prevents drift and ensures consistency across v0.2.0, v0.3.0, etc.

## Steps performed for v0.1.0

1. **Scope decision** — determined what ships (ocd plugin) vs what's deferred (blueprint, adhd, purpose-map, audit skills)
2. **Alignment pass** — conformed remaining skills and conventions to locked-down governance; no governance changes during alignment
3. **Branch creation** — created `v0.1.0` branch from `main` at the point where all in-scope work was complete
4. **Dev content stripping** — removed content not ready for consumers from the release branch (blueprint plugin, purpose-map, in-progress audit skills)
5. **Documentation regeneration** — rebuilt README.md and architecture.md on the release branch to reflect release scope only (single plugin, stripped features)
6. **Residue cleanup** — found and removed stale cross-references to stripped content
7. **Version bump** — bumped `plugin.json` version to `0.1.0`
8. **Tag** — tagged the final release commit as `v0.1.0`
9. **Push** — pushed both branch and tag to origin
10. **Main branch README update** — added a "Releases" section to `main` README pointing consumers to the latest stable release branch
11. **GitHub Release page** — created a GitHub Release for the tag with a summary of what's included, install instructions, and what's on main but not in the release

## Best practices for ongoing releases

- **Release branches are snapshots, not long-lived.** Cut the branch, strip, tag, push. Don't merge back into the release branch after cutting — fixes go on main and ship in the next release.
- **Main README always points to latest stable.** Update the "Releases" section link when a new release ships.
- **GitHub Release page per version.** Each tagged release gets a Release page with: what's included, install instructions, and what's new since the prior release (changelog-style for v0.2.0+).
- **Strip, don't stub.** Remove unshipped plugins and tools entirely from the release branch rather than leaving empty directories or "coming soon" placeholders.
- **Documentation regeneration is mandatory after stripping.** README and architecture.md on the release branch must reflect only what shipped — stale references to stripped content confuse consumers.
- **Version bump happens on the release branch, not main.** Main uses `z`-increment versions for dev commits. The `y`-increment (public release) only appears on the release branch.
- **Smoke test after tagging.** Before creating the GitHub Release, verify the install flow works: `marketplace add ...#vX.Y.Z`, `plugin install`, init, status.

## Skill vs documented process

Two options, not yet decided:

**Option A: `/ocd:release` skill** — automates the mechanical steps (branch creation, version bump, tag, push, GitHub Release creation). Scope decisions and content stripping remain manual. The skill handles the ceremony after the human decisions are made.

**Option B: Documented process in CLAUDE.md** — a checklist the developer follows manually. Lower investment, sufficient if releases are infrequent (quarterly or less).

Recommendation: start with Option B (checklist) for v0.2.0. If the pattern stabilizes and releases become frequent, promote to a skill.
