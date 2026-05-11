---
log-role: reference
---

# Pattern

Reusable workflow shapes, methodology references, and architectural templates codified from experience or research. Patterns are stable reference material that skills and agents consult when executing, and that future sessions consult to stay consistent with how the project approaches recurring work.

## What Qualifies

A workflow shape, methodology, or architectural template that:

- Captures a coherent approach to a recurring task or structural concern.
- Stays stable across the specific instances that apply it. A pattern is the "how we approach this class of work," not the record of any one application.
- Earns its place by being consulted more than once, or by being sharp enough that a future session should reliably match it.

## What Does Not Qualify

- Documented outcomes of a single task → decision (captures rationale for one choice) or a commit message
- Observations of a specific defect → problem
- Exploratory "what if" thoughts → idea
- Research findings across a population of samples → research
- Rules (behavioral triggers) → `.claude/rules/` governance
- Conventions (content standards for a file type) → `.claude/conventions/` governance

A pattern differs from a rule or convention: rules fire on behavioral triggers, conventions govern file content. Patterns describe coherent approaches that are referenced when planning or authoring, not enforced at tool-call time.

## Entry Structure

After the title and purpose statement, include whichever of these sections serve the pattern:

- **When to use** — conditions that signal the pattern applies. Sharp-enough to disambiguate from adjacent patterns.
- **Process / Shape** — the pattern itself. Steps if it's a workflow; structure if it's an architectural template; methodology if it's analytical.
- **Pitfalls** — failure modes observed when the pattern is applied poorly.
- **Anti-patterns** — approaches that look like the pattern but fail in specific ways.
- **See also** — sibling patterns, upstream rules, research sources.

Section set varies with the pattern's nature. Methodology patterns lean on Process + Pitfalls; architectural patterns lean on Shape + When to use; analytical patterns lean on Methodology + See also.

## Lifecycle

Semi-permanent — like decisions, patterns do not expire when "acted on." A pattern stays in place as long as it's referenced or applied. Update entries when the pattern's shape evolves. Delete only when the pattern is obsolete or has been subsumed by a sibling.

Patterns are user-editable reference material — a consumer of the plugin who has opted into the patterns log owns their deployed copies. Skills and rules that reference pattern content do so as *pointers*, not as execution dependencies; a missing or edited pattern file must not break any skill.
