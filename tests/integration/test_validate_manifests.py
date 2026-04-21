"""Integration tests for scripts/validate-manifests.py.

Subprocess-invokes the validator against synthetic marketplace trees in
`tmp_path` to verify it catches specific failure modes (missing required
fields, reserved names, non-kebab-case, missing plugin source paths,
plugin.json name mismatch).
"""

import json
import subprocess
from pathlib import Path

import pytest


VALIDATOR = Path(__file__).resolve().parents[1].parent / "scripts" / "validate-manifests.py"


def _write_marketplace(repo: Path, data: dict) -> None:
    (repo / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (repo / ".claude-plugin" / "marketplace.json").write_text(json.dumps(data))


def _write_plugin(repo: Path, subdir: str, name: str) -> None:
    plugin_dir = repo / subdir
    (plugin_dir / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": name, "version": "0.0.0"}),
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Synthetic repo fixture with the validator script copied in-place.

    The validator hardcodes REPO_ROOT from its own filesystem location, so
    testing against synthetic trees requires running a copy of the script
    whose REPO_ROOT resolves to the synthetic repo.
    """
    synthetic = tmp_path / "repo"
    synthetic.mkdir()
    (synthetic / "scripts").mkdir()
    (synthetic / "scripts" / "validate-manifests.py").write_text(
        VALIDATOR.read_text(),
    )
    return synthetic


def _validate(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "scripts/validate-manifests.py"],
        cwd=repo,
        capture_output=True,
        text=True,
    )


class TestHappyPath:
    def test_minimal_valid_marketplace(self, repo: Path) -> None:
        _write_marketplace(repo, {
            "name": "my-plugins",
            "owner": {"name": "Alice"},
            "plugins": [{"name": "foo", "source": "./foo"}],
        })
        _write_plugin(repo, "foo", "foo")

        result = _validate(repo)
        assert result.returncode == 0, result.stderr
        assert "Validation passed" in result.stdout


class TestFailureModes:
    def test_missing_marketplace_fields(self, repo: Path) -> None:
        _write_marketplace(repo, {"name": "incomplete"})
        result = _validate(repo)
        assert result.returncode != 0
        assert "missing required field: owner" in result.stderr
        assert "missing required field: plugins" in result.stderr

    def test_reserved_marketplace_name(self, repo: Path) -> None:
        _write_marketplace(repo, {
            "name": "anthropic-plugins",
            "owner": {"name": "Alice"},
            "plugins": [],
        })
        result = _validate(repo)
        assert result.returncode != 0
        assert "reserved" in result.stderr

    def test_non_kebab_marketplace_name(self, repo: Path) -> None:
        _write_marketplace(repo, {
            "name": "My_Plugins",
            "owner": {"name": "Alice"},
            "plugins": [],
        })
        result = _validate(repo)
        assert result.returncode != 0
        assert "kebab-case" in result.stderr

    def test_plugin_missing_source_path(self, repo: Path) -> None:
        _write_marketplace(repo, {
            "name": "my-plugins",
            "owner": {"name": "Alice"},
            "plugins": [{"name": "missing", "source": "./no-such-dir"}],
        })
        result = _validate(repo)
        assert result.returncode != 0
        assert "source path not found" in result.stderr

    def test_plugin_json_name_mismatch(self, repo: Path) -> None:
        _write_marketplace(repo, {
            "name": "my-plugins",
            "owner": {"name": "Alice"},
            "plugins": [{"name": "entry-name", "source": "./foo"}],
        })
        _write_plugin(repo, "foo", "different-name")
        result = _validate(repo)
        assert result.returncode != 0
        assert "does not match marketplace entry" in result.stderr

    def test_invalid_json(self, repo: Path) -> None:
        (repo / ".claude-plugin").mkdir(parents=True)
        (repo / ".claude-plugin" / "marketplace.json").write_text("{not valid json")
        result = _validate(repo)
        assert result.returncode != 0
        assert "invalid JSON" in result.stderr
