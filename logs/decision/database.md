---
log-role: reference
---

# Database

Decisions governing the database layer — engine choice and referential-integrity patterns that apply across every agent-facing database in the project.

## SQLite with WAL mode for agent databases

### Context

Agent-facing infrastructure (navigator, future coordination tools) needs a database. Requirements:

- File-based, no server — portability, git-friendly project structure
- CLI-accessible — agents interact through commands
- Handles concurrent writes gracefully — multiple agents may operate simultaneously
- Good at both inserts and reads — push data, query facts
- Python stdlib or near-stdlib — minimal dependencies

### Options Considered

**SQLite** — file-based, stdlib (`sqlite3`), excellent read performance, broad tooling support. Limitation: write concurrency is serialized; WAL mode + `busy_timeout` mitigate but do not eliminate contention under heavy concurrent writes.

**DuckDB** — file-based embedded database with proper concurrent write handling and columnar storage. Optimized for OLAP (analytics) rather than OLTP (transactional inserts). Better for analytical queries but not ideal for agents pushing individual records.

**Embedded modes of traditional databases** — SQLite's concurrency limitations are specific to its architecture, not inherent to file-based databases. Other embedded engines exist but add dependency weight.

### Decision

SQLite with WAL mode and `busy_timeout`. Concurrent write contention is a theoretical concern that has not materialized in practice — agent workflows are sequential within a session, and cross-session writes are infrequent.

### Consequences

- **Enables:** zero-dependency database via Python stdlib, single-file portability, broad tool compatibility
- **Constrains:** if agent coordination scales to heavy concurrent writes across sessions, may need to revisit engine choice
- **Mitigation:** WAL mode provides read concurrency; `busy_timeout` handles transient write contention

## Star schema cascades via FK introspection

### Context

MCP database servers expose CRUD tools to agents. Agents create, read, update, and delete records across related tables. When a parent record is deleted, child records referencing it via foreign keys become orphans — violating referential integrity and leaving stale data agents may later read.

The blueprint research database surfaced this during integration testing: deleting an entity failed with a FK constraint because child records (entity_urls, entity_notes, etc.) still referenced it. The unit tests never caught this because they called Python functions directly, bypassing the MCP transport where agents encounter it.

As MCP databases become the standard architecture across plugins, the data model and its behavioral guarantees need to be explicit.

### Options Considered

**Schema-level CASCADE** — declare `ON DELETE CASCADE` on FK columns. SQLite handles cleanup automatically. Limitation: behavior is invisible in application code; requires schema migration on existing databases; no hook point for business logic during cascade.

**Hardcoded child tables** — application code lists known child tables and deletes them before the parent. Limitation: breaks when schema evolves; every new FK relationship requires updating the delete function.

**Dynamic FK introspection** — application code uses `PRAGMA foreign_key_list` to discover all tables referencing the target, then recursively deletes depth-first. Adapts automatically to schema changes; no hardcoded table names.

### Decision

Dynamic FK introspection at the MCP server layer. The delete operation discovers child relationships from schema metadata and cascades depth-first before deleting the parent. This applies to both single-record and bulk deletes.

The data model is an **Aggregate Star Schema**:

- **Star schema** defines the structure — a central entity table with satellite tables joined via foreign keys
- **Aggregate** defines ownership — every FK relationship implies the parent owns the child records; the root entity and all reachable children form a consistency boundary
- **Ownership cascade** defines delete behavior — deleting a root cascades through the entire ownership tree; no orphans survive
- **Junction tables** (many-to-many) are owned by both sides — deleting either parent removes the junction row

### Consequences

- **Enables:** schema evolution without updating delete logic; consistent orphan prevention across all MCP databases; agents can safely delete without knowing the full relationship graph
- **Constrains:** all FK relationships are treated as ownership; no "soft reference" FKs where the child should survive parent deletion
- **Constrains:** if a future schema requires non-ownership references, introduce a mechanism to distinguish reference types (e.g., nullable FKs for soft references vs non-nullable for ownership)

## Schema-aware init contract via tools.db.rectify

### Context

DB-backed systems (navigator, needs-map) duplicated ~30 lines of init orchestration each: schema check → no-op or backup-then-rebuild. Auto-init blanket-called every system's `init(force=True)`, which unconditionally wiped the DB even when the schema was already current — producing a "Deployed — reinstall navigator.db" derivative commit on every checkpoint.

The duplication mirrored the file-deployment problem already solved by `setup.deploy_files` (declare src+dst; helper handles compare-before-write). DB-backed systems lacked the equivalent helper.

### Options Considered

**Per-system orchestration with shared primitives only** — `tools.db` exposes schema_signature/schemas_match/write_backup; each system writes its own if-current-noop / if-divergent-backup-rebuild flow. Rejected: 30-line orchestration duplicated across systems; new DB system arrivals re-write the same flow.

**Template DB stored as binary artifact alongside SCHEMA constant** — comparison becomes file-vs-file. Rejected: binary diff opaque in PRs, dual source-of-truth (SCHEMA constant + template file), template must be regenerated when SCHEMA changes.

**Centralized rectify helper, system declares what** — mirrors `setup.deploy_files`. Each system passes `(db_path, schema_builder, rel_path, force=…)`; helper owns the inventory + no-op + backup + rebuild flow. Adopted.

### Decision

`tools.db.rectify(db_path, schema_builder, rel_path, force)` is the canonical entry point. `tools.db.reset_db(...)` is the always-destructive companion for the per-system `reset` CLI verb. Schema comparison uses PRAGMA introspection (`schema_signature`) — whitespace/quoting/default-expression insensitive by construction; auto-indexes from PRIMARY KEY/UNIQUE constraints filtered out. Canonical signature is memoized per schema_builder via `@functools.cache` — first call ~15ms, subsequent ~0.2ms.

Force semantics shift from "blanket destructive" to "surgical":

- absent → build, emit `absent → current`
- current → no-op, emit `current → current`
- divergent → backup to timestamped sibling + wipe + rebuild, emit `divergent → reinstalled` plus backup entry
- divergent + not force → raise `InitError` directing the caller to force or to the system's `reset` verb

`init(force=True)` does NOT wipe data when schema matches; `reset` is the explicit destructive verb separate from init.

### Consequences

- **Enables:** healthy DBs no-op on every `/checkpoint`; the per-checkpoint navigator.db reinstall churn vanishes; new DB-backed systems get the contract for free by passing `(path, builder, rel)` rather than re-implementing orchestration; data loss across forced rebuilds requires affirmative `--force` invocation against actually-divergent state
- **Constrains:** schema_builder must be deterministic (true today; would break if init had branching behavior); DB-backed systems requiring non-standard force semantics need a separate helper, not a flag on rectify
- **Auto-init simplification:** `scripts/auto_init.py` no longer maintains a project-level pre-sync backup-and-restore mechanism; each system owns its backup discipline through `tools.db.write_backup`. Auto-init aggregates backup paths into an end-of-run summary
