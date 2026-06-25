# Reauthor a skill file

Reauthor exactly one TARGET — an absolute path to one markdown file in a skill — composing it fresh under the skill-authoring disciplines. Operate only on TARGET; never read, reference, or change another file.

## Process

1. Read: TARGET in full.
2. {reauthored}: Apply: /reauthor, /skill-authoring:
    1. Compose TARGET fresh, end to end — no patch residue, no "previously X" trace. Preserve its **outcome** (what it produces or enables) and **identity** (its path, name, and any public interface, commands, or signatures). Change only **form** — structure, ordering, prose, headings, and process notation. Never alter the technical facts, commands, absolute paths, field names, or decisions it records.
    2. If TARGET is a skill's top-level `SKILL.md`, author its frontmatter `description:` trigger as well; any other file has no frontmatter.
3. Write {reauthored} back to TARGET.
