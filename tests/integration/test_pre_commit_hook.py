"""Integration tests for the pre-commit hook.

Verifies two pre-commit behaviors: shared-file propagation from
canonical sources to other plugins when those sources are staged, and
plugin.json version auto-bumping — the Option E cache-invalidation
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


class TestPreCommitPropagation:
    """Test .githooks/pre-commit propagates shared files to non-ocd plugins."""

    @pytest.fixture(autouse=True)
    def setup_plugin(self, worktree):
        self.root = worktree
        self.plugin_dir = worktree / "plugins" / "test-hook-plugin"
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        (self.plugin_dir / "systems" / "setup").mkdir(parents=True, exist_ok=True)
        (self.plugin_dir / "tools").mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "add", str(self.plugin_dir)],
            cwd=self.root, capture_output=True,
        )
        yield
        # Reset index to HEAD and restore tracked files to clear any side
        # effects from the hook — bumps to plugins/ocd/.claude-plugin/plugin.json
        # and propagated copies under test-hook-plugin must not leak into the
        # next test class running in the same session-scoped worktree.
        subprocess.run(
            ["git", "reset", "HEAD"],
            cwd=self.root, capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "--", "."],
            cwd=self.root, capture_output=True,
        )
        if self.plugin_dir.exists():
            shutil.rmtree(self.plugin_dir)

    def _run_hook(self):
        return subprocess.run(
            ["bash", str(MAIN_TREE_HOOK)],
            cwd=self.root, capture_output=True, text=True,
        )

    def _stage_file(self, path):
        subprocess.run(["git", "add", str(path)], cwd=self.root, capture_output=True)

    def _touch_and_stage(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write("\n")
        self._stage_file(path)

    def _unstage_file(self, path):
        subprocess.run(
            ["git", "reset", "HEAD", "--", str(path)],
            cwd=self.root, capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "--", str(path)],
            cwd=self.root, capture_output=True,
        )

    def test_no_action_when_canonical_not_staged(self):
        target = self.plugin_dir / "systems" / "setup" / "__init__.py"
        result = self._run_hook()
        assert result.returncode == 0
        assert not target.exists(), "Should not propagate when nothing staged"

    def test_propagates_setup_init(self):
        canonical = self.root / "plugins" / "ocd" / "systems" / "setup" / "__init__.py"
        target = self.plugin_dir / "systems" / "setup" / "__init__.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert target.exists(), "__init__.py was not propagated"
            assert canonical.read_bytes() == target.read_bytes(), \
                "Propagated __init__.py content does not match canonical"
        finally:
            self._unstage_file(canonical)

    def test_propagates_setup_main(self):
        canonical = self.root / "plugins" / "ocd" / "systems" / "setup" / "__main__.py"
        target = self.plugin_dir / "systems" / "setup" / "__main__.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert target.exists(), "__main__.py was not propagated"
            assert canonical.read_bytes() == target.read_bytes(), \
                "Propagated __main__.py content does not match canonical"
        finally:
            self._unstage_file(canonical)

    def test_propagates_tools_environment(self):
        """Canonical source at project-root tools/ propagates into every
        plugin's tools/ subdir — the always-on primitives vendored per plugin.
        """
        canonical = self.root / "tools" / "environment.py"
        target = self.plugin_dir / "tools" / "environment.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert target.exists(), "environment.py was not propagated"
            assert canonical.read_bytes() == target.read_bytes(), \
                "Propagated environment.py content does not match canonical"
        finally:
            self._unstage_file(canonical)

    def test_skips_ocd_plugin(self):
        """Ocd is the source of setup/; project-root tools/ is canonical for
        env/errors. Hook must not copy to either source location."""
        canonical = self.root / "plugins" / "ocd" / "systems" / "setup" / "__init__.py"
        original = canonical.read_bytes()

        self._touch_and_stage(canonical)
        try:
            self._run_hook()
            assert canonical.read_bytes() == original + b"\n"
        finally:
            self._unstage_file(canonical)

    def test_skips_plugin_without_target_dir(self):
        """If a plugin lacks the target subdirectory, skip it."""
        shutil.rmtree(self.plugin_dir / "systems" / "setup")
        canonical = self.root / "plugins" / "ocd" / "systems" / "setup" / "__init__.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert not (self.plugin_dir / "systems" / "setup" / "__init__.py").exists(), \
                "Should not create systems/setup/ directory"
        finally:
            self._unstage_file(canonical)


class TestPreCommitVersionBump:
    """Test .githooks/pre-commit auto-bumps plugin.json version on commits
    that touch the plugin tree, and correctly skips the bump when only
    plugin.json itself is staged (the release-commit escape hatch).
    """

    PLUGIN_JSON_REL = "plugins/ocd/.claude-plugin/plugin.json"

    @pytest.fixture(autouse=True)
    def setup(self, worktree):
        self.root = worktree
        self.plugin_json = worktree / self.PLUGIN_JSON_REL
        # Snapshot baseline so every test starts from the same working-tree
        # state regardless of prior-test leakage.
        self._baseline = self.plugin_json.read_bytes()
        yield
        # Restore working tree and index to baseline
        self.plugin_json.write_bytes(self._baseline)
        subprocess.run(
            ["git", "reset", "HEAD", "--", self.PLUGIN_JSON_REL],
            cwd=self.root, capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "--", self.PLUGIN_JSON_REL],
            cwd=self.root, capture_output=True,
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
        scratch = self.root / "plugins" / "ocd" / ".pre_commit_test_scratch.md"
        scratch.write_text("test content\n")
        try:
            subprocess.run(
                ["git", "add", str(scratch)],
                cwd=self.root, capture_output=True, check=True,
            )
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert self._version() == self._bump_z(starting), \
                f"Expected version {self._bump_z(starting)}, got {self._version()}"
        finally:
            subprocess.run(
                ["git", "reset", "HEAD", "--", str(scratch)],
                cwd=self.root, capture_output=True,
            )
            if scratch.exists():
                scratch.unlink()

    def test_skips_bump_when_only_plugin_json_staged(self):
        """Release-commit escape hatch: if plugin.json is the only plugin-tree
        file staged, hook does NOT re-bump z. The operator's manual edit
        (bump y, reset z=0 at release cut) survives unchanged."""
        manual_version = "9.9.9"
        data = json.loads(self._baseline)
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

    def test_bump_under_partial_commit_leaves_clean_status(self, project_root):
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
        # The session-scoped `worktree` fixture creates the worktree at
        # HEAD --detach, so the worktree's .githooks/* reflects the
        # committed hooks, not whatever is currently in the project's
        # working tree. Sync the working-tree hooks into the worktree
        # before exercising — otherwise this test validates HEAD's
        # hooks (potentially missing the fix-under-test) rather than
        # the current project hooks. Sync both pre-commit and
        # post-commit; the partial-commit MM fix lives in post-commit.
        for hook_name in ("pre-commit", "post-commit"):
            src = project_root / ".githooks" / hook_name
            if not src.is_file():
                continue
            dst = self.root / ".githooks" / hook_name
            shutil.copy2(src, dst)

        scratch = self.root / "plugins" / "ocd" / ".pre_commit_test_scratch.md"
        scratch.write_text("test content\n")
        scratch_rel = str(scratch.relative_to(self.root))
        try:
            # Stage the scratch first so the partial-commit form below has
            # something to commit. Partial-commit (`git commit -m msg
            # <path>`) requires the path to be tracked or already staged
            # — otherwise git rejects it as "did not match any file(s)
            # known to git." Staging via `git add` puts the file in the
            # main index, where partial-commit then snapshots into a temp
            # index for the hook's duration.
            subprocess.run(
                ["git", "add", scratch_rel],
                cwd=self.root, capture_output=True, check=True,
            )
            # Inline identity — CI runners have no git user.email/name
            # configured, and the existing tests bypass this by running
            # the hook directly rather than via `git commit`. This test
            # must drive a real commit, so configure identity per-call.
            result = subprocess.run(
                [
                    "git",
                    "-c", "user.email=test@example.com",
                    "-c", "user.name=Partial Commit Test",
                    "commit", "-m", "partial-commit test", scratch_rel,
                ],
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
        finally:
            subprocess.run(
                ["git", "reset", "--soft", "HEAD~1"],
                cwd=self.root, capture_output=True,
            )
            subprocess.run(
                ["git", "reset", "HEAD", "--", scratch_rel],
                cwd=self.root, capture_output=True,
            )
            if scratch.exists():
                scratch.unlink()
