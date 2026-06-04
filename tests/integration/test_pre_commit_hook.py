"""Integration tests for the pre-commit hook + scripts/bump-apply.py.

The hook auto-applies the in-PR plugin version bump: for each plugin with
staged code changes (any plugins/<name>/ file other than its own plugin.json),
set the version to z+1 of origin/main unless it is already ahead (idempotent;
a manual minor/major bump is respected). It runs on every branch — the
advanced-main race that made the prior hook skip feature branches is closed by
the /checkpoint merge-time recompute, and bump-check.yml is the CI belt.

Runs in a disposable `pristine_repo` with the real working-tree hook and a copy
of the real scripts/bump-apply.py, plus an origin/main ref to compare against —
so the hook is validated under edit, not the last committed version.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MAIN_TREE_HOOK = ROOT / ".githooks" / "pre-commit"


class TestPreCommitVersionBump:
    PLUGIN_JSON_REL = "plugins/test-plugin/.claude-plugin/plugin.json"
    STARTING_VERSION = "0.0.1"

    @pytest.fixture(autouse=True)
    def setup(self, pristine_repo: Path, project_root: Path):
        self.root = pristine_repo
        self.plugin_json = pristine_repo / self.PLUGIN_JSON_REL
        self.plugin_json.parent.mkdir(parents=True)
        self.plugin_json.write_text(
            json.dumps({"name": "test-plugin", "version": self.STARTING_VERSION}, indent=2) + "\n"
        )
        # The hook shells out to scripts/bump-apply.py relative to the repo root.
        scripts = pristine_repo / "scripts"
        scripts.mkdir()
        shutil.copy(project_root / "scripts" / "bump-apply.py", scripts / "bump-apply.py")
        subprocess.run(["git", "add", "."], cwd=self.root, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "initial", "--no-verify"],
            cwd=self.root, capture_output=True, check=True,
        )
        # The base the bump compares against (z+1 of origin/main).
        subprocess.run(
            ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
            cwd=self.root, capture_output=True, check=True,
        )

    def _run_hook(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(MAIN_TREE_HOOK)], cwd=self.root, capture_output=True, text=True
        )

    def _version(self) -> str:
        return json.loads(self.plugin_json.read_text())["version"]

    def _stage_code_change(self) -> None:
        scratch = self.root / "plugins" / "test-plugin" / "SKILL.md"
        scratch.write_text("skill body\n")
        subprocess.run(
            ["git", "add", str(scratch)], cwd=self.root, capture_output=True, check=True
        )

    def _stage_manifest(self) -> None:
        subprocess.run(
            ["git", "add", self.PLUGIN_JSON_REL], cwd=self.root, capture_output=True, check=True
        )

    def test_bumps_to_zplus1_of_base_on_plugin_change(self):
        """A staged plugin-tree change bumps the version to z+1 of origin/main."""
        self._stage_code_change()
        result = self._run_hook()
        assert result.returncode == 0, result.stderr
        assert self._version() == "0.0.2"  # z+1 of origin/main (0.0.1)

    def test_no_bump_when_only_manifest_staged(self):
        """A release-style commit (manual version, only the manifest staged) is
        left untouched — no plugin code changed, so nothing to bump."""
        data = json.loads(self.plugin_json.read_text())
        data["version"] = "9.9.9"
        self.plugin_json.write_text(json.dumps(data, indent=2) + "\n")
        self._stage_manifest()
        result = self._run_hook()
        assert result.returncode == 0, result.stderr
        assert self._version() == "9.9.9"

    def test_respects_manual_higher_bump(self):
        """An author who bumped a minor/major manually keeps it — a code change
        does not override a version already ahead of base."""
        data = json.loads(self.plugin_json.read_text())
        data["version"] = "0.1.0"
        self.plugin_json.write_text(json.dumps(data, indent=2) + "\n")
        self._stage_code_change()
        self._stage_manifest()
        result = self._run_hook()
        assert result.returncode == 0, result.stderr
        assert self._version() == "0.1.0"  # already > base 0.0.1 → untouched

    def test_idempotent_second_run(self):
        """Running the hook twice bumps once — the second run sees the version
        already ahead of base and leaves it."""
        self._stage_code_change()
        assert self._run_hook().returncode == 0
        assert self._version() == "0.0.2"
        assert self._run_hook().returncode == 0
        assert self._version() == "0.0.2"

    def test_bumps_on_feature_branch(self):
        """The bump now fires on any branch (the prior hook skipped non-main)."""
        subprocess.run(
            ["git", "checkout", "-q", "-b", "feature"],
            cwd=self.root, capture_output=True, check=True,
        )
        self._stage_code_change()
        result = self._run_hook()
        assert result.returncode == 0, result.stderr
        assert self._version() == "0.0.2"

    def test_bump_under_partial_commit_leaves_clean_status(self, project_root: Path):
        """Partial-commit form (`git commit -m msg <file>`) must leave the main
        index in sync with HEAD after the auto-bump — the post-commit hook syncs
        the main index that the temp-index `git add` under partial commit misses.
        """
        subprocess.run(
            ["git", "-C", str(self.root), "config", "core.hooksPath",
             str(project_root / ".githooks")],
            capture_output=True, check=True,
        )
        scratch = self.root / "plugins" / "test-plugin" / "SKILL.md"
        scratch.write_text("skill body\n")
        scratch_rel = str(scratch.relative_to(self.root))
        subprocess.run(
            ["git", "add", scratch_rel], cwd=self.root, capture_output=True, check=True
        )
        result = subprocess.run(
            ["git", "commit", "-m", "partial-commit test", scratch_rel],
            cwd=self.root, capture_output=True, text=True,
        )
        assert result.returncode == 0, (
            f"partial commit failed: stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        status = subprocess.run(
            ["git", "status", "--short", "--", self.PLUGIN_JSON_REL],
            cwd=self.root, capture_output=True, text=True, check=True,
        )
        assert status.stdout.strip() == "", (
            f"plugin.json should be clean after partial-commit auto-bump, got: {status.stdout!r}"
        )
