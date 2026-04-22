# SQLite WAL for agent databases

## Purpose

Agent-facing infrastructure (navigator, future coordination tools) needs a database.

## Context

Agent-facing infrastructure (navigator, future coordination tools) needs a database. Requirements:
- File-based, no server — portability, git-friendly project structure
- CLI-accessible — agents interact through commands
- Handles concurrent writes gracefully — multiple agents may operate simultaneously
- Good at both inserts and reads — push data, query facts
- Python stdlib or near-stdlib — minimal dependencies

## Options Considered

**SQLite** — file-based, stdlib (`sqlite3`), excellent read performance, broad tooling support. Limitation: write concurrency is serialized; WAL mode + `busy_timeout` mitigate but do not eliminate contention under heavy concurrent writes.

**DuckDB** — file-based embedded database with proper concurrent write handling and columnar storage. Optimized for OLAP (analytics) rather than OLTP (transactional inserts). Better for analytical queries but not ideal for agents pushing individual records.

**Embedded modes of traditional databases** — SQLite's concurrency limitations are specific to its architecture, not inherent to file-based databases. Other embedded engines exist but add dependency weight.

## Decision

SQLite with WAL mode and `busy_timeout`. Concurrent write contention is a theoretical concern that has not materialized in practice — agent workflows are sequential within a session, and cross-session writes are infrequent.

## Consequences

- Enables: zero-dependency database via Python stdlib, single-file portability, broad tool compatibility
- Constrains: if agent coordination scales to heavy concurrent writes across sessions, may need to revisit engine choice
- Mitigation: WAL mode provides read concurrency; `busy_timeout` handles transient write contention
