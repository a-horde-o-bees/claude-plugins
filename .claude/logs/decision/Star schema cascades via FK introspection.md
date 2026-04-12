# Aggregate star schema: Dynamic FK introspection to cascade deletes through ownership tree

## Purpose

MCP database servers expose CRUD tools to agents.

## Context

MCP database servers expose CRUD tools to agents. Agents create, read, update, and delete records across related tables. When a parent record is deleted, child records referencing it via foreign keys become orphans — violating referential integrity and leaving stale data agents may later read.

The blueprint research database surfaced this during integration testing: deleting an entity failed with a FK constraint because child records (entity_urls, entity_notes, etc.) still referenced it. The unit tests never caught this because they called Python functions directly, bypassing the MCP transport where agents encounter it.

As MCP databases become the standard architecture across plugins, the data model and its behavioral guarantees need to be explicit.

## Options Considered

**Schema-level CASCADE** — declare `ON DELETE CASCADE` on FK columns. SQLite handles cleanup automatically. Limitation: behavior is invisible in application code; requires schema migration on existing databases; no hook point for business logic during cascade.

**Hardcoded child tables** — application code lists known child tables and deletes them before the parent. Limitation: breaks when schema evolves; every new FK relationship requires updating the delete function.

**Dynamic FK introspection** — application code uses `PRAGMA foreign_key_list` to discover all tables referencing the target, then recursively deletes depth-first. Adapts automatically to schema changes; no hardcoded table names.

## Decision

Dynamic FK introspection at the MCP server layer. The delete operation discovers child relationships from schema metadata and cascades depth-first before deleting the parent. This applies to both single-record and bulk deletes.

The data model is an **Aggregate Star Schema**:

- **Star schema** defines the structure — a central entity table with satellite tables joined via foreign keys
- **Aggregate** defines ownership — every FK relationship implies the parent owns the child records; the root entity and all reachable children form a consistency boundary
- **Ownership cascade** defines delete behavior — deleting a root cascades through the entire ownership tree; no orphans survive
- **Junction tables** (many-to-many) are owned by both sides — deleting either parent removes the junction row

## Consequences

- Enables: schema evolution without updating delete logic; consistent orphan prevention across all MCP databases; agents can safely delete without knowing the full relationship graph
- Constrains: all FK relationships are treated as ownership; no "soft reference" FKs where the child should survive parent deletion
- If a future schema requires non-ownership references, introduce a mechanism to distinguish reference types (e.g., nullable FKs for soft references vs non-nullable for ownership)
