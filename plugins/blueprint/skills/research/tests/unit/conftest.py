"""Shared fixtures for research database unit tests."""

import importlib
import os
import sys
from pathlib import Path

import pytest

_plugin_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_plugin_root))

from skills.research._db import init_db


@pytest.fixture
def db(tmp_path):
    """Create fresh database and configure server to use it."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    os.environ["DB_PATH"] = db_path

    import servers.research_db as srv
    importlib.reload(srv)
    srv.DB_PATH = db_path

    yield {
        "path": db_path,
        "create": srv.create_records,
        "read": srv.read_records,
        "update": srv.update_records,
        "delete": srv.delete_records,
        "query": srv.query,
        "describe": srv.describe_entities,
        "merge": srv.merge_entities,
    }
