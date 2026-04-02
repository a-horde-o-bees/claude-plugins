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
    """Create fresh database and expose domain tools by their actual names."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    os.environ["DB_PATH"] = db_path

    import servers.research_db as srv
    importlib.reload(srv)
    srv.DB_PATH = db_path

    tools = {"path": db_path}
    for name in [
        "register_entity", "register_entities",
        "set_name", "clear_name", "set_description", "clear_description",
        "set_purpose", "clear_purpose", "set_relevance", "clear_relevance",
        "set_stage",
        "set_modes", "add_modes", "remove_modes", "clear_modes",
        "add_notes", "set_note", "remove_notes", "clear_notes",
        "set_measures", "clear_measures", "clear_all_measures",
        "add_url", "add_provenance",
        "reject_entity", "merge_entities",
        "get_entity", "list_entities", "get_research_queue",
        "get_unclassified", "find_duplicates", "get_dashboard",
        "get_measure_summary",
        "set_criteria", "add_criterion", "remove_criterion", "get_criteria",
        "link_criterion_note", "unlink_criterion_note", "clear_criterion_links",
        "get_assessment", "compute_relevance",
        "init_database", "describe_schema",
    ]:
        tools[name] = getattr(srv, name)

    yield tools
