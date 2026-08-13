# Design — no baked install paths

Durable vs ephemeral decides the substitution policy: apply-over-queue's payload bakes absolute paths because it lives for one run under the orchestrator that wrote it; a non-skill host (a CLAUDE.md) outlives the install that flattened it, so install-dependent paths are forbidden outright rather than raced with refreshes. Refusal is an error at build time naming the dependency — the author either drops the bundled-file reference from the dep, or cites the skill instead of flattening it.
