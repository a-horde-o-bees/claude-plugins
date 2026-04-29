"""Persistent configuration storage.

Settings live in a single-row `settings` table with one typed column per
setting. Metadata (descriptions, defaults) lives in SETTINGS_SCHEMA — this
module is the source of truth for what settings exist, their types, and
their meaning.

To add a new setting: append an entry to SETTINGS_SCHEMA. `init_settings`
will ALTER TABLE on the next call to add the column with its default.
"""

import sqlite3


SETTINGS_SCHEMA: dict[str, dict] = {
    "threshold_min": {
        "sql_type": "INTEGER",
        "default": 15,
        "description": (
            "Idle-gap threshold in minutes. Gaps between events larger than "
            "this are classified as idle (walked-away) rather than engaged "
            "composition. Below threshold = engaged time. Determines where "
            "compose-pause attribution stops counting toward user_time and "
            "starts counting toward idle."
        ),
    },
}


def _format_default(value: object, sql_type: str) -> str:
    """Format a default value for inclusion in a CREATE/ALTER TABLE clause."""
    if sql_type == "INTEGER":
        return str(int(value))  # type: ignore[arg-type]
    if sql_type == "REAL":
        return str(float(value))  # type: ignore[arg-type]
    if sql_type == "TEXT":
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
    raise ValueError(f"unsupported sql_type: {sql_type}")


def init_settings(conn: sqlite3.Connection) -> None:
    """Create settings table if needed; ensure all schema columns exist; ensure single row."""
    cols = ", ".join(
        f"{key} {meta['sql_type']} NOT NULL DEFAULT {_format_default(meta['default'], meta['sql_type'])}"
        for key, meta in SETTINGS_SCHEMA.items()
    )
    conn.execute(f"CREATE TABLE IF NOT EXISTS settings ({cols})")

    existing = {row[1] for row in conn.execute("PRAGMA table_info(settings)").fetchall()}
    for key, meta in SETTINGS_SCHEMA.items():
        if key not in existing:
            default_clause = _format_default(meta["default"], meta["sql_type"])
            conn.execute(
                f"ALTER TABLE settings ADD COLUMN {key} {meta['sql_type']} "
                f"NOT NULL DEFAULT {default_clause}"
            )

    if not conn.execute("SELECT 1 FROM settings LIMIT 1").fetchone():
        conn.execute("INSERT INTO settings DEFAULT VALUES")

    conn.commit()


def get(conn: sqlite3.Connection, key: str) -> object:
    """Return the current value of a setting (typed per the schema)."""
    if key not in SETTINGS_SCHEMA:
        raise KeyError(f"unknown setting: {key}")
    row = conn.execute(f"SELECT {key} FROM settings").fetchone()
    if row is None:
        return SETTINGS_SCHEMA[key]["default"]
    return row[0]


def set_value(conn: sqlite3.Connection, key: str, value: object) -> object:
    """Update a setting; coerce value to the schema's type. Returns the stored value."""
    if key not in SETTINGS_SCHEMA:
        raise KeyError(f"unknown setting: {key}")
    sql_type = SETTINGS_SCHEMA[key]["sql_type"]
    coerced: object
    if sql_type == "INTEGER":
        coerced = int(value)  # type: ignore[arg-type]
    elif sql_type == "REAL":
        coerced = float(value)  # type: ignore[arg-type]
    elif sql_type == "TEXT":
        coerced = str(value)
    else:
        raise ValueError(f"unsupported sql_type: {sql_type}")
    conn.execute(f"UPDATE settings SET {key} = ?", (coerced,))
    conn.commit()
    return coerced


def list_all(conn: sqlite3.Connection) -> dict:
    """Return all settings as {key: {value, default, description}}."""
    out: dict = {}
    for key, meta in SETTINGS_SCHEMA.items():
        out[key] = {
            "value": get(conn, key),
            "default": meta["default"],
            "description": meta["description"],
        }
    return out
