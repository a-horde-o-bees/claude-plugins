"""Integration tests for the pre-commit hook.

Verifies plugin.json version auto-bumping — the Option E cache-invalidation
mechanism that must fire on every plugin-tree change except release
commits (where only plugin.json is staged so the hook's escape hatch
triggers).

Runs in a disposable git worktree so tests cannot affect the main
working tree. The hook invoked is the main project's current
working-tree copy, not the disposable worktree's HEAD snapshot — tests
must validate the hook under edit rather than the last committed
version.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


MAIN_TREE_HOOK = Path(__file__).resolve().parents[2] / ".githooks" / "pre-commit"


class TestPreCommitVersionBump:
    """Test .githooks/pre-commit auto-bumps plugin.json version on commits
    to main that touch the plugin tree, and correctly skips the bump when
    only plugin.json itself is staged (the release-commit escape hatch).

    Runs in a `pristine_repo` (fresh `git init -b main`) rather than the
    parent-project `worktree` fixture — the bump path is gated on
    `branch == main`, and only a standalone repo can satisfy that gate
    (the parent's main worktree owns the only `main` ref).
    """

    PLUGIN_JSON_REL = "plugins/test-plugin/.claude-plugin/plugin.json"
    STARTING_VERSION = "0.0.1"

    @pytest.fixture(autouse=True)
    def setup(self, pristine_repo: Path):
        self.root = pristine_repo
        self.plugin_json = pristine_repo / self.PLUGIN_JSON_REL
        self.plugin_json.parent.mkdir(parents=True)
        self.plugin_json.write_text(
            json.dumps(
                {"name": "test-plugin", "version": self.STARTING_VERSION},
                indent=2,
            ) + "\n"
        )
        # Initial commit so HEAD exists — the partial-commit test drives
        # `git commit -m msg <path>` which requires HEAD to compare
        # against. --no-verify because the project hook isn't installed
        # in this fresh repo (and we don't want it firing on the seed).
        subprocess.run(
            ["git", "add", "."],
            cwd=self.root, capture_output=True, check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial", "--no-verify"],
            cwd=self.root, capture_output=True, check=True,
        )

    def _run_hook(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(MAIN_TREE_HOOK)],
            cwd=self.root, capture_output=True, text=True,
        )

    def _version(self) -> str:
        return json.loads(self.plugin_json.read_text())["version"]

    def _bump_z(self, version: str) -> str:
        parts = version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)

    def test_bumps_z_when_plugin_tree_changes(self):
        """Staging any plugin-tree change other than plugin.json itself
        triggers the auto-bump. Hook reads plugin.json, increments z,
        writes back, stages plugin.json."""
        starting = self._version()
        scratch = self.root / "plugins" / "test-plugin" / ".pre_commit_test_scratch.md"
        scratch.write_text("test content\n")
        subprocess.run(
            ["git", "add", str(scratch)],
            cwd=self.root, capture_output=True, check=True,
        )
        result = self._run_hook()
        assert result.returncode == 0, result.stderr
        assert self._version() == self._bump_z(starting), \
            f"Expected version {self._bump_z(starting)}, got {self._version()}"

    def test_skips_bump_when_only_plugin_json_staged(self):
        """Release-commit escape hatch: if plugin.json is the only plugin-tree
        file staged, hook does NOT re-bump z. The operator's manual edit
        (bump y, reset z=0 at release cut) survives unchanged."""
        manual_version = "9.9.9"
        data = json.loads(self.plugin_json.read_text())
        data["version"] = manual_version
        self.plugin_json.write_text(json.dumps(data, indent=2) + "\n")
        subprocess.run(
            ["git", "add", self.PLUGIN_JSON_REL],
            cwd=self.root, capture_output=True, check=True,
        )

        result = self._run_hook()
        assert result.returncode == 0, result.stderr
        assert self._version() == manual_version, \
            "Hook must not bump z when only plugin.json is staged"

    def test_bump_under_partial_commit_leaves_clean_status(self, project_root: Path):
        """Partial-commit form (`git commit -m msg <file>`) must leave the
        main index in sync with HEAD after the auto-bump.

        When git commit is invoked with explicit paths, GIT_INDEX_FILE is
        set to a temp index for the pre-commit hook's duration. The
        hook's `git add plugin.json` updates the temp index, the commit
        captures it, and HEAD ends up bumped. But the main index was
        never updated — it still holds the pre-bump plugin.json. Result
        post-commit: working tree has the bumped value (hook wrote it),
        main index has the pre-bump value, HEAD has the bumped value —
        an MM state on plugin.json that requires manual `git reset HEAD`
        + `git checkout --` to clear before the next commit.

        The hook must explicitly sync the bump into the main index too,
        regardless of whether GIT_INDEX_FILE points at a temp.
        """
        # Install project hooks via core.hooksPath so `git commit` fires
        # the working-tree pre-commit + post-commit (the MM-state fix
        # lives in post-commit). pristine_repo is a fresh `git init`, so
        # nothing fires by default.
        subprocess.run(
            ["git", "-C", str(self.root), "config", "core.hooksPath",
             str(project_root / ".githooks")],
            capture_output=True, check=True,
        )

        scratch = self.root / "plugins" / "test-plugin" / ".pre_commit_test_scratch.md"
        scratch.write_text("test content\n")
        scratch_rel = str(scratch.relative_to(self.root))
        # Partial-commit (`git commit -m msg <path>`) requires the path
        # to be tracked or already staged — otherwise git rejects it as
        # "did not match any file(s) known to git." Staging via `git add`
        # puts the file in the main index, where partial-commit then
        # snapshots into a temp index for the hook's duration.
        subprocess.run(
            ["git", "add", scratch_rel],
            cwd=self.root, capture_output=True, check=True,
        )
        result = subprocess.run(
            ["git", "commit", "-m", "partial-commit test", scratch_rel],
            cwd=self.root, capture_output=True, text=True,
        )
        assert result.returncode == 0, (
            f"partial commit failed: stdout={result.stdout!r} "
            f"stderr={result.stderr!r}"
        )
        status = subprocess.run(
            ["git", "status", "--short", "--", self.PLUGIN_JSON_REL],
            cwd=self.root, capture_output=True, text=True, check=True,
        )
        assert status.stdout.strip() == "", (
            "plugin.json should be clean after partial-commit auto-bump, "
            f"got status: {status.stdout!r}"
        )
