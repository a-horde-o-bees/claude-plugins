"""Permissions deploy handles additionalDirectories alongside allow patterns."""

import json
from pathlib import Path

import pytest

from systems.permissions._operations import (
    _get_recommended_additional_directories,
    run_permissions_deploy,
)


@pytest.fixture
def project_dir(tmp_path, monkeypatch) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    monkeypatch.setenv("HOME", str(home))
    return project


class TestRecommendedSchema:
    def test_additional_directories_section_present(self):
        block = _get_recommended_additional_directories()
        assert block["paths"], "expected at least one recommended path"
        assert block["description"], "expected description text"

    def test_parent_relative_entry_recommended(self):
        block = _get_recommended_additional_directories()
        assert ".." in block["paths"]


class TestDeployWritesAdditionalDirectories:
    def test_project_scope_writes_additional_directories(self, project_dir, capsys):
        run_permissions_deploy(scope="project")
        capsys.readouterr()
        settings_path = project_dir / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text())
        dirs = settings.get("permissions", {}).get("additionalDirectories", [])
        assert ".." in dirs

    def test_deploy_is_idempotent_on_additional_directories(self, project_dir, capsys):
        run_permissions_deploy(scope="project")
        run_permissions_deploy(scope="project")
        capsys.readouterr()
        settings_path = project_dir / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text())
        dirs = settings.get("permissions", {}).get("additionalDirectories", [])
        assert dirs.count("..") == 1

    def test_deploy_preserves_existing_additional_directories(
        self, project_dir, capsys,
    ):
        settings_path = project_dir / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps({
                "permissions": {"additionalDirectories": ["/pre/existing"]},
            }),
        )
        run_permissions_deploy(scope="project")
        capsys.readouterr()
        settings = json.loads(settings_path.read_text())
        dirs = settings.get("permissions", {}).get("additionalDirectories", [])
        assert "/pre/existing" in dirs
        assert ".." in dirs
