"""Generic JSON file helpers — atomic write, missing-file handling."""

import json

from scripts._config import load, save


def test_load_missing_file_returns_empty_dict(tmp_path):
    assert load(tmp_path / "nonexistent.json") == {}


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "registry.json"
    data = {"a": {"x": 1}, "b": {"y": "two"}}
    save(path, data)
    assert load(path) == data


def test_save_writes_pretty_sorted_json(tmp_path):
    path = tmp_path / "registry.json"
    save(path, {"b": 2, "a": 1})
    text = path.read_text()
    assert text.endswith("\n")
    assert json.loads(text) == {"a": 1, "b": 2}
    assert text.index('"a"') < text.index('"b"')


def test_save_atomic_no_temp_left_behind(tmp_path):
    path = tmp_path / "registry.json"
    save(path, {"k": "v"})
    siblings = list(path.parent.iterdir())
    assert siblings == [path]
