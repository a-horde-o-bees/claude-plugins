# Reauthor a skill file

Reauthor exactly one TARGET — the absolute path of one markdown file in a skill — composing it fresh under the skill-authoring disciplines. Operate only on TARGET; never read, reference, or change another file.

## Process

1. Read: TARGET in full.
2. `{reauthored}`: Apply /reauthor, /skill-authoring to:
    1. Compose TARGET fresh, end to end. Its **outcome** (what it produces or enables) and **identity** (path, name, public interface, commands, signatures, field names, technical facts, recorded decisions) survive unchanged; structure, ordering, prose, headings, and process notation are yours to set.
    2. If TARGET is a skill's top-level `SKILL.md`, author its `description:` trigger in the same pass — the suite's only trigger surface; leave `when_to_use`, `disable-model-invocation`, and `user-invocable` unset. No other file carries frontmatter.
3. Write `{reauthored}` back to TARGET.
