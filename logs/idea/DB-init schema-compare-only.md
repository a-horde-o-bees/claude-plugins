# DB-init schema-compare-only

## Driver

Today every system's `init(force=True)` unconditionally wipes its DB and rebuilds the schema from scratch — even when the schema is already current. Navigator runs this on every `/checkpoint` via `auto_init`. The wipe-and-rebuild produces a different binary file each time (SQLite page metadata diverges per write) and triggers a fresh scan on the next agent MCP call. Most of the time the schema hasn't changed; the rebuild is wasted.

## Proposed shape

A framework helper that wraps DB init with a schema-comparison gate:

```python
def db_init_if_schema_diverges(
    db_path: Path,
    expected_tables: set[str],
    rebuild_fn: Callable[[Path], None],
    force: bool = False,
) -> str:
    """Init the DB only when its schema diverges from expected.

    - DB absent → call rebuild_fn, return "absent → current"
    - DB present, schema matches expected_tables (subset check) → return "current → current" (no-op)
    - DB present, schema diverges → call rebuild_fn (preserved data lost), return "divergent → current"
    - DB present, force=True override → call rebuild_fn anyway, return "current → reinstalled"

    Schema match uses subset semantics — extra tables ok, missing expected tables = divergent.
    """
```

Each system's init calls `db_init_if_schema_diverges` instead of unconditional wipe-and-rebuild. Navigator (and any future DB system) only rebuilds when the schema actually drifted, leaving populated data intact between checkpoints.

## Benefits

- Eliminates the "every checkpoint reinstalls navigator.db" derivative commit when nothing meaningful changed
- Preserves scan state across checkpoints — re-scan only fires on agent demand, not because init wiped the DB
- Forces a deliberate force=True for a real wipe (e.g. `ocd-run navigator init --force`), reflecting actual intent

## Constraints

- `force=True` semantics shift — currently force always rebuilds, proposed version only rebuilds on schema divergence. Need to decide whether `auto_init` calls force=True (always rebuild) or schema-only (rebuild on drift).
- The check needs to be cheap (PRAGMA table_list query), not a full data validation pass.
- Doesn't help when the schema DID drift — those checkpoints still produce a derivative commit, but they should.

## Why deprioritized

After timing `auto_init.py` at 0.26s, the actual rebuild cost is negligible. The real friction is the derivative commit + the navigator.db diff that lands every checkpoint, both of which this idea would eliminate. But it's not blocking work.

## Adjacent

- The "Standard system init + propagate internal resolution" idea (priority:high) likely subsumes the schema-compare logic into `framework.standard_init` — a system's DB init becomes a single declarative call. Land that refactor first; bake schema-compare-only into the new helper rather than retrofitting.
