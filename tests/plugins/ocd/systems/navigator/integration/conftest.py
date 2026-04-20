"""Integration-test conftest for navigator.

Seeds a valid stub database and points DB_PATH at it before any test
module imports systems.navigator.server. The server's `_READY` gate
evaluates at import time; without a valid schema at that moment, tool
decorators are skipped and tests calling `nav_server.paths_*` see
AttributeError. This conftest is imported before sibling test modules,
so the env setup lands in time.

Per-test fixtures override DB_PATH to their own seeded tmp databases
for actual assertions; this module only ensures the import-time
tool registrations fire.
"""

import os
import sqlite3
import tempfile
from pathlib import Path

import systems.navigator._db as _db


def _seed_stub_db() -> Path:
    stub_dir = Path(tempfile.gettempdir()) / "ocd-navigator-test-stub"
    stub_dir.mkdir(parents=True, exist_ok=True)
    stub_db = stub_dir / "stub.db"
    conn = sqlite3.connect(str(stub_db))
    conn.executescript(_db.SCHEMA)
    conn.close()
    return stub_db


os.environ["DB_PATH"] = str(_seed_stub_db())
