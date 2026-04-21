"""Integration tests for scripts/release.sh.

Tests run the script as a subprocess against synthetic throwaway git
repos with their own origin remotes — release.sh cannot be tested
against the real project repo because it mutates plugin.json and
fetches from origin. Each test gets a fresh repo with main aligned
to a bare origin and at least one plugin manifest.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


RELEASE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "release.sh"


def _run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=check,
    )


def _run_release(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(RELEASE_SCRIPT), *args],
        cwd=repo, capture_output=True, text=True,
    )


def _write_plugin_manifest(repo: Path, name: str, version: str) -> Path:
    manifest_dir = repo / "plugins" / name / ".claude-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_dir / "plugin.json"
    manifest.write_text(json.dumps({"name": name, "version": version}, indent=2) + "\n")
    return manifest


@pytest.fixture
def release_repo(tmp_path: Path) -> Path:
    """A throwaway repo on main, aligned with a bare origin, one plugin manifest."""
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--quiet", "--bare", "-b", "main", str(origin)],
        check=True,
    )

    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "--quiet", "-b", "main")
    _run_git(repo, "config", "user.email", "test@example.com")
    _run_git(repo, "config", "user.name", "Test")
    _run_git(repo, "remote", "add", "origin", str(origin))
    _write_plugin_manifest(repo, "ocd", "0.1.3")
    _run_git(repo, "add", "plugins/ocd/.claude-plugin/plugin.json")
    _run_git(repo, "commit", "-m", "init", "--quiet")
    _run_git(repo, "push", "-u", "origin", "main", "--quiet")
    return repo


def _plugin_version(repo: Path, name: str = "ocd") -> str:
    manifest = repo / "plugins" / name / ".claude-plugin" / "plugin.json"
    return json.loads(manifest.read_text())["version"]


class TestUsageAndFormat:
    def test_exits_64_with_no_args(self, release_repo: Path):
        result = _run_release(release_repo)
        assert result.returncode == 64
        assert "Usage:" in result.stderr

    @pytest.mark.parametrize("bad_version", ["1.2", "v1.2.3", "1.2.3.4", "abc"])
    def test_exits_64_on_non_semver(self, release_repo: Path, bad_version: str):
        result = _run_release(release_repo, bad_version)
        assert result.returncode == 64
        assert "x.y.z" in result.stderr


class TestBranchPrecondition:
    def test_exits_1_when_not_on_main(self, release_repo: Path):
        _run_git(release_repo, "checkout", "-b", "feature-x", "--quiet")

        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 1
        assert "main" in result.stderr


class TestWorkingTreePrecondition:
    def test_exits_1_with_unstaged_changes(self, release_repo: Path):
        (release_repo / "untracked.txt").write_text("dirty\n")
        _run_git(release_repo, "add", "untracked.txt")
        _run_git(release_repo, "commit", "-m", "dummy", "--quiet")
        (release_repo / "untracked.txt").write_text("modified\n")

        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 1
        assert "uncommitted" in result.stderr

    def test_exits_1_with_staged_changes(self, release_repo: Path):
        (release_repo / "new.txt").write_text("staged\n")
        _run_git(release_repo, "add", "new.txt")

        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 1
        assert "uncommitted" in result.stderr


class TestOriginAlignmentPrecondition:
    def test_exits_1_when_local_ahead_of_origin(self, release_repo: Path):
        (release_repo / "extra.txt").write_text("ahead\n")
        _run_git(release_repo, "add", "extra.txt")
        _run_git(release_repo, "commit", "-m", "ahead", "--quiet")

        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 1
        assert "origin/main" in result.stderr


class TestTagExistence:
    def test_exits_1_when_tag_already_exists(self, release_repo: Path):
        _run_git(release_repo, "tag", "v0.2.0")

        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 1
        assert "v0.2.0" in result.stderr


class TestVersionAscending:
    def test_exits_1_when_target_not_greater(self, release_repo: Path):
        """Manifest is 0.1.3; requesting 0.1.3 or lower must fail."""
        result = _run_release(release_repo, "0.1.3")

        assert result.returncode == 1
        assert "not less than" in result.stderr

    def test_exits_1_when_target_lower(self, release_repo: Path):
        result = _run_release(release_repo, "0.1.2")

        assert result.returncode == 1


class TestNoManifests:
    def test_exits_1_when_no_plugin_manifests(
        self, release_repo: Path,
    ):
        shutil.rmtree(release_repo / "plugins")
        _run_git(release_repo, "add", "-A")
        _run_git(release_repo, "commit", "-m", "remove plugins", "--quiet")
        _run_git(release_repo, "push", "origin", "main", "--quiet")

        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 1
        assert "No plugin manifests" in result.stderr


class TestHappyPath:
    def test_bumps_plugin_json_and_reports_next_steps(
        self, release_repo: Path,
    ):
        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 0, result.stderr
        assert _plugin_version(release_repo) == "0.2.0"
        assert "Next steps" in result.stdout
        assert "release v0.2.0" in result.stdout

    def test_bumps_every_manifest_under_plugins(
        self, release_repo: Path,
    ):
        """Multiple manifests all get bumped in one pass."""
        _write_plugin_manifest(release_repo, "other", "0.1.0")
        _run_git(release_repo, "add", "plugins/other/.claude-plugin/plugin.json")
        _run_git(release_repo, "commit", "-m", "add other plugin", "--quiet")
        _run_git(release_repo, "push", "origin", "main", "--quiet")

        result = _run_release(release_repo, "0.2.0")

        assert result.returncode == 0, result.stderr
        assert _plugin_version(release_repo, "ocd") == "0.2.0"
        assert _plugin_version(release_repo, "other") == "0.2.0"

    def test_leaves_git_state_unstaged(self, release_repo: Path):
        """Script only touches plugin.json; doesn't stage, commit, or tag."""
        _run_release(release_repo, "0.2.0")

        # plugin.json bumped but not staged
        status = _run_git(release_repo, "status", "--porcelain").stdout
        assert "plugin.json" in status
        assert not any(line.startswith(("M  ", "A  ")) for line in status.splitlines())

        # No tag created
        tags = _run_git(release_repo, "tag").stdout.strip()
        assert tags == ""
