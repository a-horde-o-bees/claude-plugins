"""MCP server for blueprint research database.

Exposes CRUD tools with table-based routing for business logic.
Generic operations pass through to SQLite; entity-specific operations
route through existing business logic (URL normalization, dedup, stage validation).

Runs via stdio transport. Database path from DB_PATH env var.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Add the plugin root to sys.path so we can import the research package
_plugin_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_plugin_root))

from skills.research import _db as core  # noqa: E402
from skills.research._entities import register_entity, update_entity  # noqa: E402
from skills.research._notes import upsert_notes  # noqa: E402
from skills.research._measures import upsert_measures, clear_measures  # noqa: E402
from skills.research._merge import merge_entities as _merge_entities  # noqa: E402

# --- Configuration ---

DB_PATH = os.environ.get("DB_PATH", "blueprint/data/research.db")

mcp = FastMCP("blueprint-research")

# --- Schema introspection ---

# --- Database existence check ---

_NO_DB_MSG = json.dumps({
    "error": "Database not initialized.",
    "action": "Run /blueprint-init or /blueprint-research to create the database first.",
})


def _check_db() -> str | None:
    """Return error JSON if database doesn't exist, None if OK."""
    if not Path(DB_PATH).exists():
        return _NO_DB_MSG
    return None


# Tables and their FK relationships (entity_id → entities.id)
_FK_TABLES = {
    "entity_notes": "entity_id",
    "entity_urls": "entity_id",
    "entity_measures": "entity_id",
    "entity_source_data": "entity_id",
    "url_provenance": "entity_id",
}

_ALL_TABLES = {"entities", "entity_notes", "entity_urls", "entity_measures",
               "entity_source_data", "url_provenance"}

# --- Conditions parsing (Django __operator convention) ---

_OPERATOR_RE = re.compile(r"^(.+)__(gte|gt|lte|lt|ne|like|null)$")
_OP_MAP = {
    "gte": ">=",
    "gt": ">",
    "lte": "<=",
    "lt": "<",
    "ne": "!=",
    "like": "LIKE",
}


def _parse_conditions(table: str, conditions: dict, default_table: str | None = None) -> tuple[list[str], list]:
    """Parse Django-style conditions into SQL WHERE clauses and params."""
    clauses = []
    params = []

    for key, value in conditions.items():
        # Check for table-scoped condition (e.g., entity_notes.note__like)
        if "." in key and not key.startswith("__"):
            scoped_table, field_expr = key.split(".", 1)
            if scoped_table not in _ALL_TABLES:
                raise ValueError(f"Unknown table in condition: {scoped_table}")
            prefix = f"{scoped_table}."
        else:
            field_expr = key
            prefix = f"{default_table}." if default_table else ""

        # Check for operator suffix
        op_match = _OPERATOR_RE.match(field_expr)
        if op_match:
            field, op_name = op_match.group(1), op_match.group(2)
            if op_name == "null":
                if value:
                    clauses.append(f"{prefix}{field} IS NULL")
                else:
                    clauses.append(f"{prefix}{field} IS NOT NULL")
                continue
            sql_op = _OP_MAP[op_name]
        else:
            field = field_expr
            sql_op = "="

        clauses.append(f"{prefix}{field} {sql_op} ?")
        params.append(value)

    return clauses, params


def _build_select(table: str, conditions: dict | None, include: list[str] | None, limit: int | None) -> tuple[str, list]:
    """Build SELECT query with optional conditions, joins, and limit."""
    if table not in _ALL_TABLES:
        raise ValueError(f"Unknown table: {table}. Valid tables: {', '.join(sorted(_ALL_TABLES))}")

    conditions = conditions or {}
    include = include or []
    params: list = []

    # Validate include tables
    for inc_table in include:
        if inc_table not in _FK_TABLES:
            raise ValueError(f"Cannot include '{inc_table}': no FK relationship to join on. Valid: {', '.join(sorted(_FK_TABLES))}")

    # Build column list — qualify all columns with table name to avoid ambiguity
    conn = core.get_connection(DB_PATH)
    try:
        cols = []
        parent_cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        for c in parent_cols:
            cols.append(f"{table}.{c['name']} AS {c['name']}")

        for inc_table in include:
            inc_cols = conn.execute(f"PRAGMA table_info({inc_table})").fetchall()
            for c in inc_cols:
                cols.append(f"{inc_table}.{c['name']} AS \"{inc_table}.{c['name']}\"")
    finally:
        conn.close()

    select_clause = ", ".join(cols) if include else "*"

    # Build FROM/JOIN
    from_clause = table
    for inc_table in include:
        fk_col = _FK_TABLES[inc_table]
        from_clause += f" LEFT JOIN {inc_table} ON {inc_table}.{fk_col} = {table}.id"

    # Build WHERE — qualify unscoped conditions with parent table name when joining
    where_clauses, where_params = _parse_conditions(table, conditions, default_table=table if include else None)
    params.extend(where_params)

    where = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Build query
    sql = f"SELECT {select_clause} FROM {from_clause}{where} ORDER BY {table}.rowid"
    if limit:
        sql += f" LIMIT {int(limit)}"

    return sql, params


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    """Convert sqlite3.Row objects to plain dicts."""
    return [dict(r) for r in rows]


def _nest_includes(rows: list[dict], table: str, include: list[str]) -> list[dict]:
    """Nest included table data under parent entities.

    Expects column names qualified as 'table.column' for included tables
    (produced by _build_select). Parent columns are unqualified.
    """
    if not include or not rows:
        return rows

    entities: dict[str, dict] = {}

    for row in rows:
        entity_id = row.get("id")
        if entity_id not in entities:
            # Parent columns are unqualified
            parent = {k: v for k, v in row.items() if "." not in k}
            for inc in include:
                parent[inc] = []
            entities[entity_id] = parent

        # Extract child rows from qualified columns
        for inc in include:
            prefix = f"{inc}."
            child_data = {}
            for k, v in row.items():
                if k.startswith(prefix):
                    col_name = k[len(prefix):]
                    if col_name != _FK_TABLES.get(inc):
                        child_data[col_name] = v
            if any(v is not None for v in child_data.values()):
                if child_data not in entities[entity_id][inc]:
                    entities[entity_id][inc].append(child_data)

    return list(entities.values())


# --- MCP Tools ---


@mcp.tool()
def create_records(table: str, data: dict | list[dict], source_url: str | None = None) -> str:
    """Insert one or many records. Accepts single object or array.

    For entities table: normalizes URL, checks dedup, creates provenance.
    For other tables: straight insert.

    Args:
        table: Table name (entities, entity_notes, entity_measures, entity_urls, entity_source_data, url_provenance)
        data: Single record object or array of record objects with field:value pairs
        source_url: (entities only) Source URL for provenance tracking
    """
    if err := _check_db(): return err
    records = data if isinstance(data, list) else [data]

    if table == "entities":
        results = []
        for record in records:
            result = register_entity(
                DB_PATH,
                name=record.get("name", ""),
                url=record.get("url"),
                source_url=record.get("source_url") or source_url,
                relevance=record.get("relevance"),
                description=record.get("description"),
                role=record.get("role"),
            )
            results.append(result)
        return json.dumps(results if len(results) > 1 else results[0])

    if table == "entity_notes":
        results = []
        for record in records:
            entity_id = record.get("entity_id")
            note = record.get("note")
            if not entity_id or not note:
                results.append({"error": "entity_id and note are required"})
                continue
            result = upsert_notes(DB_PATH, entity_id, [note])
            results.append(result)
        return json.dumps(results if len(results) > 1 else results[0])

    if table == "entity_measures":
        results = []
        for record in records:
            entity_id = record.get("entity_id")
            measure = record.get("measure")
            value = record.get("value")
            if not entity_id or not measure or not value:
                results.append({"error": "entity_id, measure, and value are required"})
                continue
            result = upsert_measures(DB_PATH, entity_id, [f"{measure}={value}"])
            results.append(result)
        return json.dumps(results if len(results) > 1 else results[0])

    # Generic insert for other tables
    conn = core.get_connection(DB_PATH)
    try:
        results = []
        with conn:
            for record in records:
                cols = list(record.keys())
                placeholders = ", ".join(["?"] * len(cols))
                col_names = ", ".join(cols)
                conn.execute(
                    f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                    [record[c] for c in cols],
                )
                results.append({"status": "created", "data": record})
        return json.dumps(results if len(results) > 1 else results[0])
    finally:
        conn.close()


@mcp.tool()
def read_records(table: str, conditions: dict | None = None, include: list[str] | None = None, limit: int | None = None) -> str:
    """Read records with optional filtering and star-schema joins.

    Conditions use Django __operator convention:
      field: value          → equality
      field__gte: N         → >=
      field__gt: N          → >
      field__lte: N         → <=
      field__lt: N          → <
      field__ne: value      → !=
      field__like: pattern  → LIKE
      field__null: true     → IS NULL
      field__null: false    → IS NOT NULL

    Include resolves FK joins from schema (e.g., include entity_notes to get notes with entities).

    Args:
        table: Table to read from
        conditions: Filter conditions as field:value pairs with optional __operator suffix
        include: Related tables to join via FK relationships
        limit: Maximum number of records to return
    """
    if err := _check_db(): return err
    try:
        sql, params = _build_select(table, conditions, include, limit)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    conn = core.get_connection(DB_PATH)
    try:
        rows = conn.execute(sql, params).fetchall()
        result = _rows_to_dicts(rows)

        if include:
            result = _nest_includes(result, table, include)

        return json.dumps(result, default=str)
    finally:
        conn.close()


@mcp.tool()
def update_records(table: str, id: str, data: dict) -> str:
    """Update record fields by ID.

    For entities table: validates stage transitions.
    For other tables: straight update.

    Args:
        table: Table name
        id: Record ID (e.g., e1, n14)
        data: Fields to update as key:value pairs
    """
    if err := _check_db(): return err
    if table == "entities":
        result = update_entity(
            DB_PATH,
            ids=[id],
            stage=data.get("stage"),
            relevance=data.get("relevance"),
            description=data.get("description"),
            name=data.get("name"),
            role=data.get("role"),
        )
        return json.dumps({"status": "updated", "result": result})

    # Generic update
    conn = core.get_connection(DB_PATH)
    try:
        with conn:
            set_clauses = ", ".join([f"{k} = ?" for k in data.keys()])
            params = list(data.values()) + [id]
            conn.execute(
                f"UPDATE {table} SET {set_clauses} WHERE id = ?",
                params,
            )
        return json.dumps({"status": "updated", "id": id, "fields": list(data.keys())})
    finally:
        conn.close()


@mcp.tool()
def delete_records(table: str, id: str | None = None, all: bool = False) -> str:
    """Delete record by ID, or delete all records from a table.

    Args:
        table: Table name
        id: Record ID to delete (required unless all=True)
        all: Delete all records from table (required for measures bulk delete)
    """
    if err := _check_db(): return err
    if table == "entity_measures" and all:
        result = clear_measures(DB_PATH)
        return json.dumps({"status": "cleared", "result": result})

    if not id and not all:
        return json.dumps({"error": "Either id or all=True is required"})

    conn = core.get_connection(DB_PATH)
    try:
        with conn:
            if all:
                conn.execute(f"DELETE FROM {table}")
                return json.dumps({"status": "cleared", "table": table})
            else:
                conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
                return json.dumps({"status": "deleted", "table": table, "id": id})
    finally:
        conn.close()


@mcp.tool()
def query(sql: str, params: dict | None = None) -> str:
    """Execute read-only SQL query. SELECT statements only.

    Use for complex reads that need joins, aggregations, or subqueries
    beyond what read_records supports.

    Args:
        sql: SQL query (must be SELECT)
        params: Named parameters for the query (e.g., {"stage": "researched"})
    """
    if err := _check_db(): return err
    stripped = sql.strip().upper()
    if not stripped.startswith("SELECT"):
        return json.dumps({"error": "Only SELECT queries are allowed. Use create_records/update_records/delete_records for writes."})

    conn = core.get_connection(DB_PATH)
    try:
        rows = conn.execute(sql, params or {}).fetchall()
        return json.dumps(_rows_to_dicts(rows), default=str)
    finally:
        conn.close()


@mcp.tool()
def describe_entities(table: str | None = None) -> str:
    """Discover database schema — tables, columns, types, and FK relationships.

    Args:
        table: Specific table to describe (optional; omit for all tables)
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
    try:
        if table:
            if table not in _ALL_TABLES:
                return json.dumps({"error": f"Unknown table: {table}. Valid: {', '.join(sorted(_ALL_TABLES))}"})
            columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
            fks = conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
            return json.dumps({
                "table": table,
                "columns": [{"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"]), "default": c["dflt_value"]} for c in columns],
                "foreign_keys": [{"column": fk["from"], "references": f"{fk['table']}.{fk['to']}"} for fk in fks],
                "relationships": [t for t, fk_col in _FK_TABLES.items() if t != table] if table == "entities" else ["entities"] if table in _FK_TABLES else [],
            })

        # All tables
        result = {}
        for t in sorted(_ALL_TABLES):
            columns = conn.execute(f"PRAGMA table_info({t})").fetchall()
            result[t] = {
                "columns": [{"name": c["name"], "type": c["type"]} for c in columns],
                "relationships": [rel for rel, _ in _FK_TABLES.items() if rel != t] if t == "entities" else ["entities"] if t in _FK_TABLES else [],
            }
        return json.dumps(result)
    finally:
        conn.close()


@mcp.tool()
def merge_entities(ids: list[str]) -> str:
    """Merge multiple entities into lowest-ID survivor.

    Combines descriptions, preserves all notes/URLs/provenance/measures.
    Sets merged entities to stage 'merged'. Hard to reverse.

    Args:
        ids: Entity IDs to merge (comma-separated or list, e.g., ["e1", "e2"])
    """
    if err := _check_db(): return err
    id_list = ids if isinstance(ids, list) else ids.split(",")
    result = _merge_entities(DB_PATH, id_list)
    return json.dumps({"status": "merged", "result": result})


@mcp.tool()
def init_database() -> str:
    """Initialize research database. Creates schema if database doesn't exist. Idempotent — safe to call on existing database."""
    result = core.init_db(DB_PATH)
    return json.dumps({"status": "initialized", "result": result})


# --- Entry point ---

if __name__ == "__main__":
    mcp.run()
