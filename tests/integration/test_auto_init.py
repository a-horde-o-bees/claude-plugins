"""Integration tests for scripts/auto_init.py.

Tests run the script as a subprocess against a synthetic throwaway git
repo. Full end-to-end coverage against the real project tree is not
practical (would mutate `.claude/` and run every plugin's init); tests
here exercise the consumer-facing exit-code surface — empty-project
no-op, orphan pruning in `TEMPLATE_CATEGORIES`, and the end-of-run
backup report.

Schema-comparison helpers used by DB-backed systems live in
`tools/db.py` with their own coverage in `test_db.py`.
"""

import subprocess
import sys
from pathlib import Path

import pytest


AUTO_INIT = Path(__file__).resolve().parents[2] / "scripts" / "auto_init.py"


def _run_auto_init(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUTO_INIT)],
        cwd=repo, capture_output=True, text=True,
    )


@pytest.fixture
def empty_repo(tmp_path: Path) -> Path:
    """Fresh git repo with no plugins/ and no .claude/ tree."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "-C", str(repo), "init", "--quiet", "-b", "main"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test"],
        check=True,
    )
    (repo / "README.md").write_text("initial\n")
    subprocess.run(
        ["git", "-C", str(repo), "add", "README.md"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "init", "--quiet"],
        check=True,
    )
    return repo


class TestBackupReporting:
    def test_reports_backups_left_under_claude_dir(self, empty_repo: Path):
        """A timestamped `.db.backup-*` left by a prior init() should be
        flagged in the end-of-run summary so the operator can review it."""
        backup = (
            empty_repo / ".claude" / "ocd" / "needs-map"
            / "needs-map.db.backup-2026-01-01T00-00-00Z"
        )
        backup.parent.mkdir(parents=True)
        backup.write_bytes(b"SQLite format 3\x00")

        result = _run_auto_init(empty_repo)

        assert result.returncode == 0
        assert "backup" in result.stderr.lower()
        assert "needs-map.db.backup-" in result.stderr

    def test_silent_when_no_backups_exist(self, empty_repo: Path):
        """End-of-run summary fires only when at least one backup is found."""
        result = _run_auto_init(empty_repo)

        assert result.returncode == 0
        assert "backup" not in result.stderr.lower()


class TestEmptyProject:
    def test_succeeds_with_no_plugins_dir(self, empty_repo: Path):
        """Empty repo — no plugins, no .claude — main() returns 0 silently."""
        result = _run_auto_init(empty_repo)
        assert result.returncode == 0, result.stderr

    def test_succeeds_with_empty_plugins_dir(self, empty_repo: Path):
        (empty_repo / "plugins").mkdir()

        result = _run_auto_init(empty_repo)

        assert result.returncode == 0, result.stderr


class TestOrphanPruning:
    def test_removes_orphans_in_rules_directory(self, empty_repo: Path):
        """Files under `.claude/{rules,conventions,patterns}/` that no
        system claimed must be deleted — that's the whole point of
        running auto-init after a template removal."""
        orphan = empty_repo / ".claude" / "rules" / "ocd" / "stale.md"
        orphan.parent.mkdir(parents=True)
        orphan.write_text("# stale content\n")

        result = _run_auto_init(empty_repo)

        assert result.returncode == 0, result.stderr
        assert not orphan.exists()
        assert "orphan removed" in result.stdout

    def test_removes_orphans_across_all_template_categories(self, empty_repo: Path):
        """rules, conventions, and patterns are all template-managed."""
        orphans = [
            empty_repo / ".claude" / "rules" / "x.md",
            empty_repo / ".claude" / "conventions" / "y.md",
            empty_repo / ".claude" / "patterns" / "z.md",
        ]
        for orphan in orphans:
            orphan.parent.mkdir(parents=True, exist_ok=True)
            orphan.write_text("stale\n")

        result = _run_auto_init(empty_repo)

        assert result.returncode == 0, result.stderr
        for orphan in orphans:
            assert not orphan.exists()

    def test_leaves_non_template_categories_alone(self, empty_repo: Path):
        """`logs/` is user content at project root — never pruned by auto_init."""
        log_entry = empty_repo / "logs" / "idea" / "keep-me.md"
        log_entry.parent.mkdir(parents=True)
        log_entry.write_text("user content\n")

        result = _run_auto_init(empty_repo)

        assert result.returncode == 0, result.stderr
        assert log_entry.exists()
