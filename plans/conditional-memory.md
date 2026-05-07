# Conditional memory loading

Investigate a mechanism where rules declare a trigger condition (file pattern, skill invocation, agent type, declared task-shape) and only load when relevant — replacing the always-on memory model that pays per-rule token cost on every spawned agent.

## Goal

Per-rule auto-load conditioned on the active task. A spawned agent doing JD parsing doesn't pay for `process-flow-notation.md` or `testing.md` unless its work touches those concerns; an agent authoring a workflow does.

## Output

Likely two-sided:

- Plugin-side machinery — manifest-level declaration of trigger conditions per rule (frontmatter fields like `trigger-when: editing-skill-md` or similar)
- Claude Code-side support — the runtime memory loader honoring those triggers when deciding which memory files to load into a fresh agent context

## Sequence

1. Survey the current memory-loading mechanism in Claude Code — what determines which `.claude/rules/*.md` files load? Are there hooks?
2. Identify minimal trigger surface that would meaningfully reduce token floor without losing rule coverage
3. Prototype on the plugin side using existing extension points (e.g., SessionStart hook)
4. If the prototype shows promise but needs runtime support, file the request with Anthropic
5. Roll out trigger conditions on the rules whose load cost is largest (process-flow-notation, testing, design-principles individual files)

## Decisions

None locked yet — this is design space.

## Open questions

- Is there a Claude Code hook or manifest field that gates per-file memory loading today? If not, can it be approximated client-side via SessionStart?
- What trigger taxonomy is sharp enough to fire reliably without becoming its own configuration burden? (file path, skill name, agent type, declared task scope, ...)
- Per-rule cost matters most for the heaviest rules. Would a simpler "lazy rules" approach — load only when explicitly referenced by another loaded rule — cover the cost-dominant cases without a full trigger system?

## Status

Likely subsumed by the `discovery-model` workstream — see `plans/discovery-model.md` and `logs/decision/discovery-model.md`. The discovery model achieves the same outcome (per-rule trigger-conditioned loading) without requiring Anthropic-side coordination; it does so by moving artifact-triggered guidance off the always-on memory floor entirely and routing on-demand via a small always-on trigger router. Re-evaluate this plan after the discovery substrate lands; close if redundant.
