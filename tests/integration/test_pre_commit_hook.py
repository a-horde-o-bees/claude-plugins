"""Integration tests for the pre-commit hook.

Verifies that shared files propagate from ocd to other plugins
when canonical sources are staged.
"""

import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).parent.parent.parent


class TestPreCommitPropagation(unittest.TestCase):
    """Test .githooks/pre-commit propagates shared files to non-ocd plugins."""

    plugin_dir = ROOT / "plugins" / "test-hook-plugin"

    def setUp(self):
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        (self.plugin_dir / "rules").mkdir(exist_ok=True)
        (self.plugin_dir / "scripts").mkdir(exist_ok=True)
        # Stage the dummy plugin so git sees it
        subprocess.run(
            ["git", "add", str(self.plugin_dir)],
            cwd=ROOT, capture_output=True,
        )

    def tearDown(self):
        # Unstage and remove dummy plugin
        subprocess.run(
            ["git", "reset", "HEAD", "--", str(self.plugin_dir)],
            cwd=ROOT, capture_output=True,
        )
        if self.plugin_dir.exists():
            shutil.rmtree(self.plugin_dir)

    def _run_hook(self):
        """Execute the pre-commit hook directly."""
        hook = ROOT / ".githooks" / "pre-commit"
        result = subprocess.run(
            ["bash", str(hook)],
            cwd=ROOT, capture_output=True, text=True,
        )
        return result

    def _stage_file(self, path: Path):
        """Stage a file change via git add."""
        subprocess.run(["git", "add", str(path)], cwd=ROOT, capture_output=True)

    def _touch_and_stage(self, path: Path):
        """Append a newline to a file and stage it."""
        with open(path, "a") as f:
            f.write("\n")
        self._stage_file(path)

    def _unstage_file(self, path: Path):
        """Unstage a file and restore its contents."""
        # Reset index (works for both tracked and new files)
        subprocess.run(
            ["git", "reset", "HEAD", "--", str(path)],
            cwd=ROOT, capture_output=True,
        )
        # Restore working tree for tracked files
        subprocess.run(
            ["git", "checkout", "--", str(path)],
            cwd=ROOT, capture_output=True,
        )

    def test_propagates_agent_authoring_rule(self):
        canonical = ROOT / "plugins" / "ocd" / "rules" / "ocd-agent-authoring.md"
        target = self.plugin_dir / "rules" / "ocd-agent-authoring.md"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists(), "Rule was not propagated")
            self.assertEqual(
                canonical.read_bytes(), target.read_bytes(),
                "Propagated rule content does not match canonical",
            )
        finally:
            self._unstage_file(canonical)

    def test_propagates_plugin_py(self):
        canonical = ROOT / "plugins" / "ocd" / "scripts" / "plugin.py"
        target = self.plugin_dir / "scripts" / "plugin.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists(), "plugin.py was not propagated")
            self.assertEqual(
                canonical.read_bytes(), target.read_bytes(),
                "Propagated plugin.py content does not match canonical",
            )
        finally:
            self._unstage_file(canonical)

    def test_propagates_plugin_cli_py(self):
        canonical = ROOT / "plugins" / "ocd" / "scripts" / "plugin_cli.py"
        target = self.plugin_dir / "scripts" / "plugin_cli.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists(), "plugin_cli.py was not propagated")
            self.assertEqual(
                canonical.read_bytes(), target.read_bytes(),
                "Propagated plugin_cli.py content does not match canonical",
            )
        finally:
            self._unstage_file(canonical)

    def test_skips_ocd_plugin(self):
        """Ocd is the canonical source — hook should not copy to itself."""
        canonical = ROOT / "plugins" / "ocd" / "scripts" / "plugin.py"
        original = canonical.read_bytes()

        self._touch_and_stage(canonical)
        try:
            self._run_hook()
            # ocd's plugin.py should have the touch change, not be overwritten
            self.assertEqual(canonical.read_bytes(), original + b"\n")
        finally:
            self._unstage_file(canonical)

    def test_skips_plugin_without_target_dir(self):
        """If a plugin lacks the target subdirectory, skip it."""
        # Remove scripts/ so plugin.py has nowhere to go
        shutil.rmtree(self.plugin_dir / "scripts")
        canonical = ROOT / "plugins" / "ocd" / "scripts" / "plugin.py"

        self._touch_and_stage(canonical)
        try:
            result = self._run_hook()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(
                (self.plugin_dir / "scripts" / "plugin.py").exists(),
                "Should not create scripts/ directory",
            )
        finally:
            self._unstage_file(canonical)

    def test_no_action_when_canonical_not_staged(self):
        """Hook should exit early when no canonical files are staged."""
        target = self.plugin_dir / "scripts" / "plugin.py"
        result = self._run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertFalse(target.exists(), "Should not propagate when nothing staged")
