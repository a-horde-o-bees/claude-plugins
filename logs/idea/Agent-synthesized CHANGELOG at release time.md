---
tags: ["priority:high"]
---

# Agent-synthesized CHANGELOG at release time

Add a `release` verb to the `/ocd:git` skill that crawls git history since the last tag, spawns an agent to synthesize a Keep-a-Changelog entry (grouping by topic, deconflicting cross-commit overrides, categorizing Added/Changed/Fixed), writes a draft for operator review, and — after the operator accepts — tags and pushes the release. Joins the existing `commit` and `push` verbs; release is a git-repository-level operation that belongs with the rest of the git skill surface.

## Why this shape

Our commit messages already carry meaningful topics in the project's `Topic — subject + body` style, but don't follow conventional-commit syntax (`feat:`, `fix:`). That rules out mechanical tools like `git-cliff` and `release-please` without a restructure of commit discipline. Agent synthesis handles our format directly and — crucially — handles the deconfliction case that mechanical tools don't: when a feature is added, refactored, then retired across multiple commits, the CHANGELOG should reflect the *net state*, not three separate entries across Added/Changed/Removed.

## Generalization

`/ocd:git release` sits alongside `commit` and `push` as a third verb — same generalization level, no plugin-specific assumptions. Version bump stays out of scope because that's manifest-specific (our `plugin.json` vs another project's `package.json`, `Cargo.toml`, etc.). Operators run their project-specific bump as a pre-step, then invoke the release verb. Two sub-verbs under `release`:

- `/ocd:git release synthesize [--from <tag>] <version>` — reads `git log <last-tag>..HEAD`, passes commits + diffstat to an agent with instructions to produce a `## [<version>] — <date>` section in Keep-a-Changelog format. Writes draft to `/tmp/changelog-<version>.md`. Operator reviews, edits, and pastes into `CHANGELOG.md`.
- `/ocd:git release tag <version>` — assumes CHANGELOG is ready; stages CHANGELOG + any manifest bump, commits as `release v<version>`, creates annotated tag, pushes main + tag.

## Deconfliction — the load-bearing property

Mechanical commit-log tools can't see across commits. If commit A adds feature X, commit B refactors X, commit C retires X — `git-cliff` produces three entries. An LLM reasoning over the full set produces one: either "Removed: feature X" (if retirement is the final state) or nothing (if X was never released).

Concrete this session: we added the patterns system to the pattern doc's Decisions subsections, then migrated it out and retired the patterns plugin system entirely. An agent synthesizing a v0.2.0 CHANGELOG from this session's commits should produce a single "Changed: patterns now live as log types (`logs/patterns/`, `logs/research/`)" entry, not a sequence of Added-then-Removed bullets.

## `[Unreleased]` lifecycle

Drop it. No between-release accumulation, no reversed-decision messiness, no drift between human-curated and synthesized content. Replace `[Unreleased]` with a one-line pointer:

```markdown
## [Unreleased]

Populated at release time by `/ocd:git release synthesize`. See git log for in-flight changes.
```

Single source of truth: git history + the agent synthesizer at release time.

## Prerequisite work

1. Thin `scripts/release.sh` — keep the manifest bump, drop the "next steps" CHANGELOG instructions (superseded). Or retire the script entirely and let operators edit `plugin.json` directly before invoking `/ocd:git release`.
2. Update `CHANGELOG.md`'s `[Unreleased]` to the pointer form.
3. Add `release` verb (with `synthesize` and `tag` sub-verbs) to `plugins/ocd/systems/git/`. No new system; join the existing commit+push infrastructure.
4. Author the synthesis prompt carefully — needs grouping-by-topic, deconfliction, Keep-a-Changelog categorization, and a signal-to-flag-ambiguity discipline so the operator sees uncertain calls rather than confidently-wrong synthesis.
5. Exercise on v0.2.0 when it approaches. First real use validates whether the prompt produces usable drafts.

## Trade-offs

- **Non-determinism** — same commit set may produce different wordings on different runs. Mitigated by operator review (the draft isn't the final CHANGELOG until operator accepts).
- **Token cost at release time** — LLM call per release cut. Low concern since releases are rare (v0.1.0 just shipped; v0.2.0 months out at most cadences).
- **Requires domain context in the prompt** — the agent needs to understand what "user-facing change" means for this project (e.g. is a commit-message tweak user-facing? no). Domain context flows through the prompt at release time.

## Prior thinking consumed

This idea folds in the reasoning from the deleted `Release cutting skill or process.md` log. That log asked "skill or documented process?" and landed on "documented process." This refinement answers: documented process + an agent-synthesis helper that lives as a verb on an existing skill (`/ocd:git release`, joining `commit` and `push`). Not a contradiction — the skill verb automates the mechanical and analytical pieces while operator judgment stays in the loop at review time.

## When to build

Defer until v0.2.0 approaches. Current priority surfaces because the `[Unreleased]` CHANGELOG gap flagged this session has no clean resolution without this — manual CHANGELOG maintenance between releases is the overhead we're trying to eliminate, so retroactive CHANGELOG authoring at v0.2.0 time needs this helper in place.
