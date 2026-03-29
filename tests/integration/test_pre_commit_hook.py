"""Integration tests for the pre-commit hook.

Verifies that shared files propagate from ocd to other plugins
when canonical sources are staged. Runs in a disposable git worktree
so tests cannot affect the main working tree.
"""

import shutil
import subprocess

import pytest


class TestPreCommitPropagation:
    """Test .githooks/pre-commit propagates shared files to non-ocd plugins."""

    @pytest.fixture(autouse=True)
    def setup_plugin(self, worktree):
        self.root = worktree
        self.plugin_dir = worktree / "plugins" / "test-hook-plugin"
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        (self.plugin_dir / "rules").mkdir(exist_ok=True)
        (self.plugin_dir / "plugin").mkdir(exist_ok=True)
        subprocess.run(
            ["git", "add", str(self.plugin_dir)],
            cwd=self.root, capture_output=True,
        )
        yield
        subprocess.run(
            ["git", "reset", "HEAD", "--", str(self.plugin_dir)],
            cwd=self.root, capture_output=True,
        )
        if self.plugin_dir.exists():
            shutil.rmtree(self.plugin_dir)

    def _run_hook(self):
        hook = self.root / ".githooks" / "pre-commit"
        return subprocess.run(
            ["bash", str(hook)],
            cwd=self.root, capture_output=True, text=True,
        )

    def _stage_file(self, path):
        subprocess.run(["git", "add", str(path)], cwd=self.root, capture_output=True)

    def _touch_and_stage(self, path):
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
        target = self.plugin_dir / "plugin" / "__init__.py"
        result = self._run_hook()
        assert result.returncode == 0
        assert not target.exists(), "Should not propagate when nothing staged"

    def test_propagates_agent_authoring_rule(self):
        canonical = self.root / "plugins" / "ocd" / "rules" / "ocd-agent-authoring.md"
        target = self.plugin_dir / "rules" / "ocd-agent-authoring.md"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert target.exists(), "Rule was not propagated"
            assert canonical.read_bytes() == target.read_bytes(), \
                "Propagated rule content does not match canonical"
        finally:
            self._unstage_file(canonical)

    def test_propagates_plugin_init(self):
        canonical = self.root / "plugins" / "ocd" / "plugin" / "__init__.py"
        target = self.plugin_dir / "plugin" / "__init__.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert target.exists(), "__init__.py was not propagated"
            assert canonical.read_bytes() == target.read_bytes(), \
                "Propagated __init__.py content does not match canonical"
        finally:
            self._unstage_file(canonical)

    def test_propagates_plugin_main(self):
        canonical = self.root / "plugins" / "ocd" / "plugin" / "__main__.py"
        target = self.plugin_dir / "plugin" / "__main__.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert target.exists(), "__main__.py was not propagated"
            assert canonical.read_bytes() == target.read_bytes(), \
                "Propagated __main__.py content does not match canonical"
        finally:
            self._unstage_file(canonical)

    def test_skips_ocd_plugin(self):
        """Ocd is the canonical source — hook should not copy to itself."""
        canonical = self.root / "plugins" / "ocd" / "plugin" / "__init__.py"
        original = canonical.read_bytes()

        self._touch_and_stage(canonical)
        try:
            self._run_hook()
            assert canonical.read_bytes() == original + b"\n"
        finally:
            self._unstage_file(canonical)

    def test_skips_plugin_without_target_dir(self):
        """If a plugin lacks the target subdirectory, skip it."""
        shutil.rmtree(self.plugin_dir / "plugin")
        canonical = self.root / "plugins" / "ocd" / "plugin" / "__init__.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            assert result.returncode == 0, result.stderr
            assert not (self.plugin_dir / "plugin" / "__init__.py").exists(), \
                "Should not create plugin/ directory"
        finally:
            self._unstage_file(canonical)
