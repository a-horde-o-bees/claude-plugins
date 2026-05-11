# Research Samples

Per-entity evidence files that back the consolidated findings in a research subject. Samples live under `logs/research/<subject>/samples/` and mirror the consolidated doc's purpose structure so cross-sample tallying produces comparable counts.

## What Qualifies

A sample is one data point for the research subject — one repo when studying ecosystems, one file when studying content standards, one implementation when studying a design space. The sample captures what *this specific entity* does for each purpose the subject investigates.

A sample file is not a narrative about the entity. It's evidence organized to be scanned and tallied alongside siblings.

## Entity Identifier

Each sample file is named for its entity using a filename scheme the subject declares. Keep the scheme stable across all samples in the subject:

- Ecosystem studies of repos: `<owner>--<repo>.md` (double-hyphen separator keeps the filename unambiguous when owner or repo contains hyphens).
- File studies: the file's relative path flattened, or a meaningful handle.
- Implementation studies: the implementation's canonical name.

The first sample authored in a new subject sets the scheme; later samples match.

## Entry Structure

The sample file mirrors the consolidated doc's purpose structure one-to-one. Every purpose section in the consolidated doc appears in every sample file; samples that don't capture a particular purpose mark it explicitly (see *Not captured*) rather than omitting.

Shape:

```markdown
# <entity identifier>

One-line identity line: URL, path, version, or reference pointing at the entity.

## Metadata

Summary metadata about the entity that research needs to cite — size, language, activity signals, last commit date, whatever the subject's tallying needs.

## <Purpose 1>

What the entity does for this purpose. Concrete — name files, configurations, values. Evidence is what counts; prose is overhead.

## <Purpose 2>

...

## <Purpose N>

...

## Pitfalls / Anomalies

Entity-specific observations that don't fit any purpose section — bugs, unusual choices, ecosystem-visible defects. Consumed by the consolidated doc's Pitfalls sections.

## Gaps

Purposes the sample didn't capture. Marking "not captured" explicitly lets tallying distinguish "entity does path X" from "we didn't check."
```

## Section Discipline

- **Every consolidated-doc purpose appears as a section.** Missing sections break tallying.
- **Purposes match the consolidated doc's section headings exactly** so scripts can scan for them.
- **Per purpose: observed paths with citations.** Quote the manifest, the line, the filename. Evidence makes the tally defensible; unsourced claims don't.
- **Not-captured is a valid per-purpose state.** When the research template didn't target a particular purpose or the sample's context doesn't expose it, write "Not captured" rather than silently omitting.
- **Counter-examples and negative adoption deserve explicit notes.** An entity that *deliberately* doesn't follow a convention contributes different signal from an entity that silently lacks the convention. Mark the distinction.

## Tallying Discipline

The consolidated doc's adoption counts aggregate from the samples. For a count like "14/54 repos declare non-trivial `userConfig`":

- Each sample's matching purpose section has a classifier statement ("userConfig: declared, 11 fields, 5/11 flagged `sensitive: true`").
- A tallying pass reads every sample's section, classifies each, and aggregates.
- Denominators follow applicability: counts against the full sample when a purpose applies universally, counts against the applicable subset when it applies conditionally.

Keeping classifier statements consistent across samples is what makes tallying possible. The first sample's section sets the format; later samples match.

## Refreshing Samples When Purposes Evolve

When the consolidated doc adds a new purpose (discovered in a later research wave), samples need the purpose backfilled. The refresh:

1. Add the purpose section to every sample file, even if the content is "Not captured" (the research template didn't target it).
2. For samples where the data is re-extractable, extract and classify.
3. For samples where extraction requires re-reading external sources, note "Not captured — requires re-read" and prioritize re-reading based on the purpose's adoption-count importance.

Never leave samples inconsistent with the consolidated doc's purpose set — tallying breaks silently when some samples have a purpose and others don't.

## Lifecycle

Semi-permanent. Samples accumulate as the subject grows. Delete only when the entity is genuinely removed from the research population (a repo archived and no longer relevant, a file removed from the codebase), or when a sibling sample subsumes the entity.

Users own deployed copies — they can edit, extend, or add samples beyond what the plugin shipped. The samples are the evidence pool, not an execution dependency for any skill.
