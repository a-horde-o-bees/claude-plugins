---
name: composability
description:
---

# Composability

Build small pieces that combine naturally. Monolithic components that cannot be consumed independently become bottlenecks — impossible to test, migrate, or fix in isolation.

- Tools do one thing and can be called in any order — no implicit sequencing between independent operations
- Data models separate concerns into independent tables — each queryable and migratable without affecting others
- Files stay small enough for agents to consume in a single context
