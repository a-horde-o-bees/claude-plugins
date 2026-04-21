"""Integration tests for scripts/auto_init.py.

Tests run the script as a subprocess against a synthetic throwaway git
repo. Full end-to-end coverage against the real project tree is not
practical (would mutate `.claude/` and run every plugin's init); tests
here exercise the consumer-facing exit-code surface — the
unresolved-backup gate, empty-project no-op, and orphan pruning in
`TEMPLATE_CATEGORIES`.
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


class TestUnresolvedBackupGate:
    def test_exits_2_when_pre_sync_has_db_files(self, empty_repo: Path):
        """Stale `.claude/pre-sync/**/*.db` must block the next run —
        the operator has to resolve or remove before re-syncing."""
        pre_sync = empty_repo / ".claude" / "pre-sync"
        pre_sync.mkdir(parents=True)
        (pre_sync / "leftover.db").write_bytes(b"SQLite format 3\x00")

        result = _run_auto_init(empty_repo)

        assert result.returncode == 2
        assert "unresolved" in result.stderr

    def test_exits_0_when_pre_sync_absent(self, empty_repo: Path):
        result = _run_auto_init(empty_repo)
        assert result.returncode == 0, result.stderr

    def test_exits_0_when_pre_sync_has_no_db_files(self, empty_repo: Path):
        """Pre-sync directory with non-DB contents is not an unresolved state."""
        pre_sync = empty_repo / ".claude" / "pre-sync"
        pre_sync.mkdir(parents=True)
        (pre_sync / "note.txt").write_text("stray file\n")

        result = _run_auto_init(empty_repo)

        assert result.returncode == 0, result.stderr


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
        """`.claude/logs/` is user content — never pruned by auto_init."""
        log_entry = empty_repo / ".claude" / "logs" / "idea" / "keep-me.md"
        log_entry.parent.mkdir(parents=True)
        log_entry.write_text("user content\n")

        result = _run_auto_init(empty_repo)

        assert result.returncode == 0, result.stderr
        assert log_entry.exists()
