"""Unit tests for governance operations."""

from pathlib import Path

import pytest

from servers.governance import (
    governance_list,
    governance_load,
    governance_match,
    governance_order,
)
from servers.governance._db import get_connection, init_db, SCHEMA
from servers.governance._frontmatter import (
    normalize_patterns,
    parse_governance,
    read_frontmatter,
)


def _write_governance_file(path: Path, includes, governed_by: list = None, excludes=None) -> None:
    """Create a markdown file with governance frontmatter at path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(includes, list):
        quoted = ", ".join(f'"{p}"' for p in includes)
        lines = ["---", f"includes: [{quoted}]"]
    else:
        lines = ["---", f'includes: "{includes}"']
    if excludes:
        if isinstance(excludes, list):
            lines.append("excludes:")
            for exc in excludes:
                lines.append(f'  - "{exc}"')
        else:
            lines.append(f'excludes: "{excludes}"')
    if governed_by:
        lines.append("governed_by:")
        for dep in governed_by:
            lines.append(f"  - {dep}")
    lines += ["---", ""]
    path.write_text("\n".join(lines))




@pytest.fixture
def db_path(tmp_path):
    """Create a temporary governance database with schema."""
    path = str(tmp_path / "test.db")
    conn = get_connection(path)
    conn.executescript(SCHEMA)
    conn.close()
    return path


class TestGovernanceLoad:
    @pytest.fixture
    def gov_env(self, project_dir, tmp_path):
        """Create governance files and database for governance testing."""
        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        _write_governance_file(project_dir / ".claude/rules/design-principles.md", "*")
        _write_governance_file(
            project_dir / ".claude/rules/workflow.md", "*",
            governed_by=[".claude/rules/design-principles.md"],
        )
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/python.md", "*.py",
            governed_by=[".claude/rules/design-principles.md"],
        )
        return {"db": db}

    def test_loads_governance_entries(self, gov_env):
        governance_load(gov_env["db"])
        conn = get_connection(gov_env["db"])
        rule_count = conn.execute("SELECT COUNT(*) as c FROM rules").fetchone()["c"]
        conv_count = conn.execute("SELECT COUNT(*) as c FROM conventions").fetchone()["c"]
        assert rule_count == 2
        assert conv_count == 1
        conn.close()

    def test_rules_in_rules_table(self, gov_env):
        governance_load(gov_env["db"])
        conn = get_connection(gov_env["db"])
        row = conn.execute(
            "SELECT entry_path FROM rules WHERE entry_path = '.claude/rules/design-principles.md'"
        ).fetchone()
        assert row is not None
        conn.close()

    def test_conventions_in_conventions_table(self, gov_env):
        governance_load(gov_env["db"])
        conn = get_connection(gov_env["db"])
        row = conn.execute(
            "SELECT entry_path FROM conventions WHERE entry_path = '.claude/conventions/ocd/python.md'"
        ).fetchone()
        assert row is not None
        conn.close()

    def test_idempotent_reload(self, gov_env):
        governance_load(gov_env["db"])
        governance_load(gov_env["db"])
        conn = get_connection(gov_env["db"])
        rule_count = conn.execute("SELECT COUNT(*) as c FROM rules").fetchone()["c"]
        conv_count = conn.execute("SELECT COUNT(*) as c FROM conventions").fetchone()["c"]
        assert rule_count == 2
        assert conv_count == 1
        conn.close()

    def test_returns_summary(self, gov_env):
        result = governance_load(gov_env["db"])
        assert result["governance_entries"] == 3

    def test_populates_depends_on(self, gov_env):
        governance_load(gov_env["db"])
        conn = get_connection(gov_env["db"])
        rows = conn.execute(
            "SELECT entry_path, depends_on_path FROM governance_depends_on "
            "ORDER BY entry_path, depends_on_path"
        ).fetchall()
        edges = {(r["entry_path"], r["depends_on_path"]) for r in rows}
        assert (".claude/rules/workflow.md", ".claude/rules/design-principles.md") in edges
        assert (".claude/conventions/ocd/python.md", ".claude/rules/design-principles.md") in edges
        assert len(edges) == 2
        conn.close()

    def test_depends_on_cleared_on_file_delete(self, gov_env, project_dir):
        governance_load(gov_env["db"])
        (project_dir / ".claude/rules/workflow.md").unlink()
        governance_load(gov_env["db"])
        conn = get_connection(gov_env["db"])
        rows = conn.execute(
            "SELECT COUNT(*) as c FROM governance_depends_on "
            "WHERE entry_path = '.claude/rules/workflow.md'"
        ).fetchone()
        assert rows["c"] == 0
        conn.close()

    def test_depends_on_replaced_on_file_change(self, gov_env, project_dir):
        governance_load(gov_env["db"])
        _write_governance_file(
            project_dir / ".claude/rules/workflow.md", "*",
            governed_by=[],
        )
        governance_load(gov_env["db"])
        conn = get_connection(gov_env["db"])
        rows = conn.execute(
            "SELECT COUNT(*) as c FROM governance_depends_on "
            "WHERE entry_path = '.claude/rules/workflow.md'"
        ).fetchone()
        assert rows["c"] == 0
        conn.close()


class TestGovernanceOrder:
    @pytest.fixture
    def order_db(self, tmp_path):
        db = str(tmp_path / "order.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()
        return db

    def _write_chain(self, project_dir, files: dict[str, list[str]]) -> None:
        """Write governance files under project_dir.

        files maps relative path → list of governed_by paths.
        """
        for rel, governed_by in files.items():
            _write_governance_file(
                project_dir / rel,
                includes="*",
                governed_by=governed_by if governed_by else None,
            )

    def test_empty_db(self, order_db):
        result = governance_order(order_db)
        assert result == {"levels": [], "dangling": []}

    def test_single_root(self, order_db, project_dir):
        self._write_chain(project_dir, {".claude/rules/a.md": []})
        result = governance_order(order_db)
        assert result["dangling"] == []
        assert result["levels"] == [[{"path": ".claude/rules/a.md", "governors": []}]]

    def test_simple_chain(self, order_db, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [],
                ".claude/rules/b.md": [".claude/rules/a.md"],
                ".claude/rules/c.md": [".claude/rules/b.md"],
            },
        )
        result = governance_order(order_db)
        assert result["dangling"] == []
        paths_per_level = [[e["path"] for e in level] for level in result["levels"]]
        assert paths_per_level == [
            [".claude/rules/a.md"],
            [".claude/rules/b.md"],
            [".claude/rules/c.md"],
        ]

    def test_independent_siblings_in_one_level(self, order_db, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [],
                ".claude/rules/b.md": [],
                ".claude/rules/c.md": [
                    ".claude/rules/a.md",
                    ".claude/rules/b.md",
                ],
            },
        )
        result = governance_order(order_db)
        assert result["dangling"] == []
        levels = result["levels"]
        assert len(levels) == 2
        level0_paths = {e["path"] for e in levels[0]}
        assert level0_paths == {".claude/rules/a.md", ".claude/rules/b.md"}
        assert levels[1] == [
            {
                "path": ".claude/rules/c.md",
                "governors": [".claude/rules/a.md", ".claude/rules/b.md"],
            }
        ]

    def test_bidirectional_pair_collapses_to_level(self, order_db, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [".claude/rules/b.md"],
                ".claude/rules/b.md": [".claude/rules/a.md"],
            },
        )
        result = governance_order(order_db)
        assert result["dangling"] == []
        assert len(result["levels"]) == 1
        level_paths = {e["path"] for e in result["levels"][0]}
        assert level_paths == {".claude/rules/a.md", ".claude/rules/b.md"}

    def test_three_cycle_collapses_to_level(self, order_db, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [".claude/rules/b.md"],
                ".claude/rules/b.md": [".claude/rules/c.md"],
                ".claude/rules/c.md": [".claude/rules/a.md"],
            },
        )
        result = governance_order(order_db)
        assert result["dangling"] == []
        assert len(result["levels"]) == 1
        level_paths = {e["path"] for e in result["levels"][0]}
        assert level_paths == {
            ".claude/rules/a.md",
            ".claude/rules/b.md",
            ".claude/rules/c.md",
        }

    def test_dangling_reference_returns_dangling(self, order_db, project_dir):
        self._write_chain(
            project_dir,
            {".claude/rules/a.md": [".claude/rules/missing.md"]},
        )
        result = governance_order(order_db)
        assert result["levels"] == []
        assert result["dangling"] == [
            {
                "entry_path": ".claude/rules/a.md",
                "missing": ".claude/rules/missing.md",
            }
        ]

    def test_foundations_before_dependents(self, order_db, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [],
                ".claude/rules/b.md": [".claude/rules/a.md"],
            },
        )
        result = governance_order(order_db)
        paths = [e["path"] for level in result["levels"] for e in level]
        assert paths.index(".claude/rules/a.md") < paths.index(".claude/rules/b.md")


class TestGovernanceList:
    def test_lists_entries(self, project_dir, tmp_path):
        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        _write_governance_file(project_dir / ".claude/rules/design-principles.md", "*")
        _write_governance_file(project_dir / ".claude/conventions/py.md", "*.py")

        result = governance_list(db)
        assert len(result) == 2
        rule = next(r for r in result if r["mode"] == "rule")
        conv = next(r for r in result if r["mode"] == "convention")
        assert rule["path"] == ".claude/rules/design-principles.md"
        assert rule["includes"] == "*"
        assert conv["path"] == ".claude/conventions/py.md"

    def test_empty(self, db_path):
        result = governance_list(db_path)
        assert result == []


class TestGovernanceMatch:
    @pytest.fixture
    def gov_db(self, project_dir, tmp_path):
        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        _write_governance_file(project_dir / ".claude/rules/principles.md", "*")
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/python.md", "*.py",
            governed_by=[".claude/rules/principles.md"],
        )
        governance_load(db)
        return db

    def test_matches_conventions_only(self, gov_db):
        result = governance_match(gov_db, ["src/app.py"])
        assert ".claude/conventions/ocd/python.md" in result["matches"]["src/app.py"]
        # Rules are excluded — already loaded into agent context
        assert ".claude/rules/principles.md" not in result["matches"]["src/app.py"]

    def test_wildcard_rule_excluded(self, gov_db):
        result = governance_match(gov_db, ["README.md"])
        # README.md matches principles.md (pattern: *) but it's a rule — excluded
        assert result["matches"] == {}

    def test_no_match(self, db_path):
        result = governance_match(db_path, ["test.py"])
        assert result["matches"] == {}

    def test_multiple_files(self, gov_db):
        result = governance_match(gov_db, ["src/app.py", "README.md"])
        # src/app.py matches python convention; README.md only matches rule (excluded)
        assert "src/app.py" in result["matches"]
        assert "README.md" not in result["matches"]

    def test_conventions_aggregated(self, gov_db):
        result = governance_match(gov_db, ["src/app.py"])
        assert ".claude/conventions/ocd/python.md" in result["conventions"]
        # Rules not in conventions list
        assert ".claude/rules/principles.md" not in result["conventions"]


class TestGovernanceMatchExcludes:
    @pytest.fixture
    def excludes_db(self, project_dir, tmp_path):
        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        _write_governance_file(project_dir / ".claude/rules/principles.md", "*")
        _write_governance_file(
            project_dir / ".claude/conventions/server.md", "servers/*.py",
            excludes=["__init__.py", "_helpers.py"],
        )
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/python.md", "*.py",
        )
        governance_load(db)
        return db

    def test_excludes_filters_basename(self, excludes_db):
        result = governance_match(excludes_db, ["servers/__init__.py"])
        # Python convention matches, but server convention excludes __init__.py
        matched = result["matches"].get("servers/__init__.py", [])
        assert ".claude/conventions/ocd/python.md" in matched
        assert ".claude/conventions/server.md" not in matched

    def test_excludes_allows_normal_files(self, excludes_db):
        result = governance_match(excludes_db, ["servers/navigator.py"])
        matched = result["matches"]["servers/navigator.py"]
        assert ".claude/conventions/server.md" in matched
        assert ".claude/conventions/ocd/python.md" in matched

    def test_excludes_filters_helpers(self, excludes_db):
        result = governance_match(excludes_db, ["servers/_helpers.py"])
        matched = result["matches"].get("servers/_helpers.py", [])
        assert ".claude/conventions/server.md" not in matched
        assert ".claude/conventions/ocd/python.md" in matched

    def test_excludes_in_conventions_list(self, excludes_db):
        result = governance_match(excludes_db, ["servers/__init__.py", "servers/navigator.py"])
        # server.md appears in conventions because it matched navigator.py
        assert ".claude/conventions/server.md" in result["conventions"]


class TestScanGovernance:
    @pytest.fixture
    def gov_scan_tree(self, project_dir):
        """Project tree with governance loaded, ready for scan."""
        project = project_dir
        (project / "app.py").write_text("x = 1\n")
        (project / "README.md").write_text("# Readme\n")
        sub = project / "sub"
        sub.mkdir()
        (sub / "helper.py").write_text("y = 2\n")

        db_file = project.parent / "scan_gov.db"
        db = str(db_file)
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        # Write governance files inside the project directory and load
        _write_governance_file(project / ".claude/rules/all.md", "*")
        _write_governance_file(
            project / ".claude/conventions/ocd/python.md", "*.py",
            governed_by=[".claude/rules/all.md"],
        )
        governance_load(db)
        return {"project": project, "db": db}

    def test_governance_match_uses_glob_patterns(self, gov_scan_tree):
        """governance_match uses patterns from convention_includes table."""
        db = gov_scan_tree["db"]
        result = governance_match(db, ["app.py", "README.md", "sub/helper.py"])
        # Python convention matches .py files
        assert ".claude/conventions/ocd/python.md" in result["matches"].get("app.py", [])
        assert ".claude/conventions/ocd/python.md" in result["matches"].get("sub/helper.py", [])
        # Python convention does not match README.md
        assert ".claude/conventions/ocd/python.md" not in result["matches"].get("README.md", [])

    def test_governance_load_discovers_new_files(self, gov_scan_tree):
        """New convention files added after init are registered by governance_load."""
        project = gov_scan_tree["project"]
        db = gov_scan_tree["db"]

        _write_governance_file(
            project / ".claude/conventions/readme.md", "README.md",
        )

        governance_load(db)

        conn = get_connection(db)
        rows = conn.execute(
            "SELECT entry_path FROM conventions "
            "WHERE entry_path = '.claude/conventions/readme.md'"
        ).fetchall()
        assert len(rows) == 1

        # governance_match finds the new convention
        result = governance_match(db, ["README.md"])
        assert ".claude/conventions/readme.md" in result["matches"].get("README.md", [])
        conn.close()

    def test_governance_load_removes_deleted_files(self, gov_scan_tree):
        """governance_load removes rows for files deleted from disk."""
        project = gov_scan_tree["project"]
        db = gov_scan_tree["db"]

        # Delete the convention file from disk
        (project / ".claude/conventions/ocd/python.md").unlink()
        governance_load(db)

        conn = get_connection(db)
        rows = conn.execute(
            "SELECT entry_path FROM conventions "
            "WHERE entry_path = '.claude/conventions/ocd/python.md'"
        ).fetchall()
        assert len(rows) == 0
        # CASCADE cleared pattern tables too
        include_rows = conn.execute(
            "SELECT entry_path FROM convention_includes "
            "WHERE entry_path = '.claude/conventions/ocd/python.md'"
        ).fetchall()
        assert len(include_rows) == 0
        conn.close()

    def test_governance_load_updates_changed_files(self, gov_scan_tree):
        """governance_load picks up content changes to existing files."""
        project = gov_scan_tree["project"]
        db = gov_scan_tree["db"]

        # Overwrite python.md with a different pattern
        _write_governance_file(
            project / ".claude/conventions/ocd/python.md", "*.pyi",
        )
        governance_load(db)

        result = governance_match(db, ["app.pyi"])
        assert ".claude/conventions/ocd/python.md" in result["matches"].get("app.pyi", [])
        # Old pattern no longer matches
        result = governance_match(db, ["app.py"])
        assert "app.py" not in result["matches"]

    def test_governance_load_ignores_rule_dir_files_without_frontmatter(self, gov_scan_tree):
        """Subsystem docs under .claude/rules/ without frontmatter are not rules."""
        project = gov_scan_tree["project"]
        db = gov_scan_tree["db"]

        # Drop a README with no governance frontmatter into the rules dir
        (project / ".claude/rules/README.md").write_text("# Rules\n\nSubsystem docs.\n")
        governance_load(db)

        conn = get_connection(db)
        row = conn.execute(
            "SELECT entry_path FROM rules WHERE entry_path = '.claude/rules/README.md'"
        ).fetchone()
        assert row is None
        conn.close()

    def test_governance_load_preserves_unchanged_hash(self, gov_scan_tree):
        """Unchanged files keep their stored git_hash across reloads."""
        project = gov_scan_tree["project"]
        db = gov_scan_tree["db"]

        conn = get_connection(db)
        before = conn.execute(
            "SELECT git_hash FROM conventions WHERE entry_path = '.claude/conventions/ocd/python.md'"
        ).fetchone()["git_hash"]
        conn.close()

        governance_load(db)

        conn = get_connection(db)
        after = conn.execute(
            "SELECT git_hash FROM conventions WHERE entry_path = '.claude/conventions/ocd/python.md'"
        ).fetchone()["git_hash"]
        conn.close()

        assert before == after


class TestNormalizePatterns:
    def test_single_string(self):
        assert normalize_patterns("*.py") == ["*.py"]

    def test_json_list(self):
        result = normalize_patterns('["test_*.*", "*_test.*", "conftest.*"]')
        assert result == ["test_*.*", "*_test.*", "conftest.*"]

    def test_single_element_list(self):
        assert normalize_patterns('["*.py"]') == ["*.py"]

    def test_empty_list(self):
        assert normalize_patterns("[]") == []


class TestReadFrontmatter:
    def test_reads_frontmatter_between_delimiters(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("---\nkey: value\nother: thing\n---\n\n# Body\n")
        assert read_frontmatter(f) == ["key: value", "other: thing"]

    def test_returns_none_when_no_opening_delimiter(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# Just a heading\n\nNo frontmatter here.\n")
        assert read_frontmatter(f) is None

    def test_returns_none_when_missing_closing_delimiter(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("---\nkey: value\nstill going\n")
        assert read_frontmatter(f) is None

    def test_returns_none_for_empty_file(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("")
        assert read_frontmatter(f) is None

    def test_returns_none_for_missing_file(self, tmp_path):
        assert read_frontmatter(tmp_path / "nope.md") is None

    def test_stops_at_closing_without_reading_body(self, tmp_path):
        f = tmp_path / "doc.md"
        body_marker = "SENTINEL_SHOULD_NOT_BE_PARSED"
        f.write_text(f"---\nkey: value\n---\n\n{body_marker}\n")
        lines = read_frontmatter(f)
        assert lines == ["key: value"]
        assert body_marker not in (lines or [])

    def test_empty_frontmatter_block(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("---\n---\n\n# Body\n")
        assert read_frontmatter(f) == []


class TestBlockStylePattern:
    def test_block_style_includes_parsed(self, tmp_path):
        """Block-style YAML list for includes is parsed correctly."""
        gov_file = tmp_path / "testing.md"
        gov_file.write_text(
            "---\n"
            "includes:\n"
            '  - "test_*.*"\n'
            '  - "*_test.*"\n'
            '  - "conftest.*"\n'
            "governed_by:\n"
            "  - .claude/rules/design.md\n"
            "---\n\n"
            "# Testing\n"
        )
        result = parse_governance(gov_file)
        assert result is not None
        patterns = normalize_patterns(result["includes"])
        assert patterns == ["test_*.*", "*_test.*", "conftest.*"]
        assert result["governed_by"] == [".claude/rules/design.md"]

    def test_flow_style_includes(self, tmp_path):
        """Flow-style YAML list for includes works."""
        gov_file = tmp_path / "testing.md"
        gov_file.write_text(
            '---\n'
            'includes: ["test_*.*", "*_test.*"]\n'
            '---\n\n'
            '# Testing\n'
        )
        result = parse_governance(gov_file)
        assert result is not None
        patterns = normalize_patterns(result["includes"])
        assert patterns == ["test_*.*", "*_test.*"]

    def test_single_includes(self, tmp_path):
        """Single string includes works."""
        gov_file = tmp_path / "python.md"
        gov_file.write_text(
            '---\n'
            'includes: "*.py"\n'
            '---\n\n'
            '# Python\n'
        )
        result = parse_governance(gov_file)
        assert result is not None
        assert result["includes"] == "*.py"

    def test_excludes_parsed(self, tmp_path):
        """Excludes field is parsed from frontmatter."""
        gov_file = tmp_path / "server.md"
        gov_file.write_text(
            '---\n'
            'includes: "servers/*.py"\n'
            'excludes:\n'
            '  - "__init__.py"\n'
            '  - "_helpers.py"\n'
            '---\n\n'
            '# Server\n'
        )
        result = parse_governance(gov_file)
        assert result is not None
        assert result["includes"] == "servers/*.py"
        excludes = normalize_patterns(result["excludes"])
        assert excludes == ["__init__.py", "_helpers.py"]


class TestListPatternGovernanceFor:
    @pytest.fixture
    def list_gov_db(self, project_dir, tmp_path):
        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        _write_governance_file(project_dir / ".claude/rules/all.md", "*")
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/testing.md",
            ["test_*.*", "*_test.*", "conftest.*"],
        )
        governance_load(db)
        return db

    def test_matches_test_prefix(self, list_gov_db):
        result = governance_match(list_gov_db, ["test_utils.py"])
        assert ".claude/conventions/ocd/testing.md" in result["matches"]["test_utils.py"]

    def test_matches_test_suffix(self, list_gov_db):
        result = governance_match(list_gov_db, ["app_test.py"])
        assert ".claude/conventions/ocd/testing.md" in result["matches"]["app_test.py"]

    def test_matches_conftest(self, list_gov_db):
        result = governance_match(list_gov_db, ["conftest.py"])
        assert ".claude/conventions/ocd/testing.md" in result["matches"]["conftest.py"]

    def test_no_match_regular_file(self, list_gov_db):
        result = governance_match(list_gov_db, ["app.py"])
        # app.py matches only the wildcard rule (excluded) — no conventions
        assert "app.py" not in result["matches"]

    def test_multiple_files_mixed(self, list_gov_db):
        result = governance_match(list_gov_db, ["test_foo.py", "app.py", "bar_test.py"])
        assert "test_foo.py" in result["matches"]
        # app.py matches only rule (excluded)
        assert "app.py" not in result["matches"]
        assert "bar_test.py" in result["matches"]


class TestListPatternGovernanceMatch:
    @pytest.fixture
    def list_gov_tree(self, project_dir, tmp_path):
        project = project_dir
        (project / "test_app.py").write_text("x = 1\n")
        (project / "utils_test.py").write_text("y = 2\n")
        (project / "conftest.py").write_text("z = 3\n")
        (project / "app.py").write_text("w = 4\n")

        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        _write_governance_file(
            project / ".claude/conventions/ocd/testing.md",
            ["test_*.*", "*_test.*", "conftest.*"],
        )
        governance_load(db)
        return {"project": project, "db": db}

    def test_governance_match_all_list_patterns(self, list_gov_tree):
        db = list_gov_tree["db"]
        result = governance_match(db, [
            "test_app.py", "utils_test.py", "conftest.py", "app.py",
        ])
        assert ".claude/conventions/ocd/testing.md" in result["matches"].get("test_app.py", [])
        assert ".claude/conventions/ocd/testing.md" in result["matches"].get("utils_test.py", [])
        assert ".claude/conventions/ocd/testing.md" in result["matches"].get("conftest.py", [])
        assert "app.py" not in result["matches"]
