# Idempotency

Operations are safely re-runnable — repeated execution converges to the same state without destroying or duplicating prior work. Agent workflows retry frequently — any operation that changes behavior on repeated invocation causes cascading failures. Design every write operation to converge on retry.

- Init operations detect existing state and skip gracefully
- Upsert over insert — handle the "already exists" case by design
- Diff-based operations (e.g., dependency install, template sync) converge to the same state regardless of how many times they run
