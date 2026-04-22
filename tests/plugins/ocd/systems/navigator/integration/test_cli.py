"""Integration tests for the navigator CLI verb dispatch.

Exercises every `ocd-run navigator <verb>` through the real bin wrapper.
The underlying facade (paths_get, paths_list, scan_path, etc.) is
covered by per-function unit tests; this suite locks the CLI dispatch
surface — argparse wiring, exit codes, output format — for all 10
verbs so any regression surfaces immediately.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

from systems.navigator._db import SCHEMA, get_connection


def _run(
    ocd_run: Path, *args: str, env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ocd_run), "navigator", *args],
        capture_output=True, text=True,
        env=env, cwd=cwd,
    )


@pytest.fixture
def scratch_project(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    """Throwaway project with a minimal filesystem tree and isolated DB.

    Returns (project_dir, db_path, env) — env sets CLAUDE_PROJECT_DIR and
    is safe to pass to subprocess.run for navigator write verbs.

    The DB is created but tables are not materialized here — callers that
    need a pre-seeded schema use `seeded_project` instead. `ready` and
    subprocess tests that explicitly test fresh-DB behavior rely on the
    empty state.
    """
    project = tmp_path / "proj"
    (project / "src").mkdir(parents=True)
    (project / "src" / "app.py").write_text("print('hi')\n")
    (project / "src" / "util.py").write_text("def util(): pass\n")
    (project / "README.md").write_text("# proj\n")

    db = project / ".claude" / "ocd" / "navigator" / "navigator.db"
    db.parent.mkdir(parents=True)

    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project)
    return project, db, env


@pytest.fixture
def seeded_project(scratch_project) -> tuple[Path, Path, dict[str, str]]:
    """scratch_project + navigator schema applied to the DB.

    Navigator's CLI verbs (scan, describe, list, ...) expect the schema
    to already exist — normal usage relies on `/ocd:setup init` to
    create it. CLI tests stub in the schema directly via `_db.SCHEMA`.
    """
    project, db, env = scratch_project
    conn = get_connection(str(db))
    conn.executescript(SCHEMA)
    conn.close()
    return project, db, env


class TestScanVerb:
    def test_scan_populates_db(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project

        result = _run(
            ocd_run, "scan", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        assert db.is_file()
        assert "Scan:" in result.stdout or "Added" in result.stdout


class TestDescribeVerb:
    def test_describes_directory(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project

        result = _run(
            ocd_run, "describe", ".", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        assert "src" in result.stdout

    def test_requires_path_argument(self, ocd_run: Path, seeded_project):
        _, db, env = seeded_project
        result = _run(
            ocd_run, "describe", "--db", str(db),
            env=env,
        )
        assert result.returncode != 0


class TestListVerb:
    def test_lists_files(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project

        result = _run(
            ocd_run, "list", ".", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        paths = result.stdout.splitlines()
        assert any("src/app.py" in p for p in paths)
        assert any("README.md" in p for p in paths)

    def test_pattern_filter(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project

        result = _run(
            ocd_run, "list", ".", "--pattern", "*.py", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        paths = result.stdout.splitlines()
        assert all(p.endswith(".py") for p in paths if p.strip())

    def test_sizes_flag_adds_columns(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project

        result = _run(
            ocd_run, "list", ".", "--sizes", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        # tab-separated: path<tab>lines<tab>chars
        for line in result.stdout.splitlines():
            if line.strip():
                assert "\t" in line


class TestGetUndescribedVerb:
    def test_emits_undescribed_on_fresh_db(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project

        result = _run(
            ocd_run, "get-undescribed", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        # Either [?] markers or "No work remaining."
        assert "[?]" in result.stdout or "No work remaining" in result.stdout


class TestSetVerb:
    def test_writes_purpose(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project
        _run(ocd_run, "scan", "--db", str(db), env=env, cwd=project)

        result = _run(
            ocd_run, "set", "src/app.py",
            "--purpose", "Entry point",
            "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        assert "src/app.py" in result.stdout

    def test_requires_path(self, ocd_run: Path, seeded_project):
        _, db, env = seeded_project
        result = _run(
            ocd_run, "set", "--purpose", "x", "--db", str(db),
            env=env,
        )
        assert result.returncode != 0


class TestRemoveVerb:
    def test_removes_existing_path(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project
        _run(ocd_run, "scan", "--db", str(db), env=env, cwd=project)

        result = _run(
            ocd_run, "remove", "src/app.py", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        assert "src/app.py" in result.stdout

    def test_remove_nonexistent_reports_not_found(
        self, ocd_run: Path, seeded_project,
    ):
        project, db, env = seeded_project
        _run(ocd_run, "scan", "--db", str(db), env=env, cwd=project)

        result = _run(
            ocd_run, "remove", "nothing/here.py", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        assert "Not found" in result.stdout


class TestSearchVerb:
    def test_search_requires_pattern(self, ocd_run: Path, seeded_project):
        _, db, env = seeded_project
        result = _run(
            ocd_run, "search", "--db", str(db),
            env=env,
        )
        assert result.returncode != 0

    def test_search_with_pattern_runs(self, ocd_run: Path, seeded_project):
        project, db, env = seeded_project
        _run(ocd_run, "scan", "--db", str(db), env=env, cwd=project)

        result = _run(
            ocd_run, "search", "--pattern", "entry", "--db", str(db),
            env=env, cwd=project,
        )

        assert result.returncode == 0, result.stderr
        # Either finds results or reports no matches — either is valid output
        assert "Search:" in result.stdout or "No paths matching" in result.stdout


class TestResolveSkillVerb:
    def test_resolves_known_skill(self, ocd_run: Path):
        """`checkpoint` is a project-level skill at .claude/skills/checkpoint."""
        result = _run(ocd_run, "resolve-skill", "checkpoint")
        assert result.returncode == 0, result.stderr
        assert "SKILL.md" in result.stdout

    def test_unknown_skill_exits_1(self, ocd_run: Path):
        result = _run(ocd_run, "resolve-skill", "no-such-skill-anywhere")
        assert result.returncode == 1
        assert "not found" in result.stderr.lower()

    def test_requires_name(self, ocd_run: Path):
        result = _run(ocd_run, "resolve-skill")
        assert result.returncode != 0


class TestReadyVerb:
    def test_ready_returns_1_on_missing_db(
        self, ocd_run: Path, scratch_project,
    ):
        """Fresh scratch project (no schema applied) — ready must report
        not-ready so dormancy-gated callers know init is required."""
        _, db, env = scratch_project
        assert not db.is_file()

        result = _run(
            ocd_run, "ready", "--db", str(db),
            env=env,
        )

        assert result.returncode == 1

    def test_ready_returns_0_after_scan(
        self, ocd_run: Path, seeded_project,
    ):
        project, db, env = seeded_project
        _run(ocd_run, "scan", "--db", str(db), env=env, cwd=project)

        result = _run(
            ocd_run, "ready", "--db", str(db),
            env=env,
        )

        assert result.returncode == 0


class TestListSkillsVerb:
    def test_lists_discoverable_skills(self, ocd_run: Path):
        result = _run(ocd_run, "list-skills")
        assert result.returncode == 0, result.stderr
        # At minimum the checkpoint skill should surface
        assert "checkpoint" in result.stdout or "No skills found" in result.stdout


class TestDispatchBoundary:
    def test_missing_command_exits_nonzero(self, ocd_run: Path):
        result = subprocess.run(
            [str(ocd_run), "navigator"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
