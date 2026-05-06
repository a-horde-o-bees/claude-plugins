"""Unit tests for the rules system's setup facade.

Covers the per-system setup shape (purpose, list_items, status, install,
uninstall) exposed at `systems.rules.__init__` per the plugin-system
convention. Validates per-scope deploy paths, target handling, and
unsupported-scope error reporting.
"""

import systems.rules as rules_setup


class TestPurpose:
    def test_returns_one_line_string(self):
        result = rules_setup.purpose()
        assert isinstance(result, str)
        assert "\n" not in result
        assert result.strip() == result


class TestListItems:
    def test_returns_items_with_name_and_purpose(self, scopes):
        result = rules_setup.list_items()
        assert "items" in result
        assert len(result["items"]) >= 24
        for item in result["items"]:
            assert "name" in item
            assert "purpose" in item
            assert item["purpose"]
            assert not item["purpose"].startswith("includes:")
            assert not item["purpose"].startswith("---")

    def test_items_sorted_by_name(self, scopes):
        result = rules_setup.list_items()
        names = [item["name"] for item in result["items"]]
        assert names == sorted(names)

    def test_purpose_skips_yaml_frontmatter(self, scopes):
        result = rules_setup.list_items()
        honesty = next(item for item in result["items"] if item["name"] == "honesty")
        assert "Action and output" in honesty["purpose"] or "verify" in honesty["purpose"].lower()


class TestStatus:
    def test_default_reports_both_scopes(self, scopes):
        result = rules_setup.status()
        paths = [f["path"] for f in result["files"]]
        assert any(p.startswith("~/.claude/rules/ocd/") for p in paths)
        assert any(p.startswith(".claude/rules/ocd/") and not p.startswith("~/") for p in paths)

    def test_scope_filter_user(self, scopes):
        result = rules_setup.status(scope="user")
        paths = [f["path"] for f in result["files"]]
        assert all(p.startswith("~/.claude/rules/ocd/") for p in paths)

    def test_scope_filter_project(self, scopes):
        result = rules_setup.status(scope="project")
        paths = [f["path"] for f in result["files"]]
        assert all(p.startswith(".claude/rules/ocd/") for p in paths)

    def test_unsupported_scope_returns_error(self, scopes):
        result = rules_setup.status(scope="planet")
        assert any("unsupported scope" in e["value"] for e in result["extra"])

    def test_reports_absent_before_install(self, scopes):
        result = rules_setup.status(scope="project")
        assert all(f["before"] == "absent" for f in result["files"])


class TestInstall:
    def test_install_single_target_at_project_scope(self, scopes):
        result = rules_setup.install(scope="project", targets=["honesty"])
        assert (scopes.project / ".claude/rules/ocd/honesty.md").is_file()
        assert not (scopes.user / "rules/ocd/honesty.md").exists()
        paths = [f["path"] for f in result["files"]]
        assert paths == [".claude/rules/ocd/honesty.md"]

    def test_install_single_target_at_user_scope(self, scopes):
        result = rules_setup.install(scope="user", targets=["honesty"])
        assert (scopes.user / "rules/ocd/honesty.md").is_file()
        assert not (scopes.project / ".claude/rules/ocd/honesty.md").exists()
        paths = [f["path"] for f in result["files"]]
        assert paths == ["~/.claude/rules/ocd/honesty.md"]

    def test_install_multiple_targets(self, scopes):
        result = rules_setup.install(
            scope="project",
            targets=["honesty", "borrow-before-build", "clean-break"],
        )
        assert (scopes.project / ".claude/rules/ocd/honesty.md").is_file()
        assert (scopes.project / ".claude/rules/ocd/borrow-before-build.md").is_file()
        assert (scopes.project / ".claude/rules/ocd/clean-break.md").is_file()
        paths = [f["path"] for f in result["files"]]
        assert len(paths) == 3

    def test_install_all_at_scope(self, scopes):
        rules_setup.install(scope="project", targets=None)
        deployed = list((scopes.project / ".claude/rules/ocd").glob("*.md"))
        assert len(deployed) >= 24

    def test_install_target_with_md_extension_accepted(self, scopes):
        rules_setup.install(scope="project", targets=["honesty.md"])
        assert (scopes.project / ".claude/rules/ocd/honesty.md").is_file()

    def test_install_unknown_target_returns_error(self, scopes):
        result = rules_setup.install(scope="project", targets=["not-a-rule"])
        assert any("unknown rule" in e["value"] for e in result["extra"])
        assert result["files"] == []

    def test_install_partial_unknown_targets_blocks_all(self, scopes):
        result = rules_setup.install(
            scope="project",
            targets=["honesty", "not-a-rule"],
        )
        assert any("unknown rule" in e["value"] for e in result["extra"])
        assert result["files"] == []
        assert not (scopes.project / ".claude/rules/ocd/honesty.md").exists()

    def test_install_unsupported_scope_returns_error(self, scopes):
        result = rules_setup.install(scope="planet", targets=["honesty"])
        assert any("unsupported scope" in e["value"] for e in result["extra"])
        assert result["files"] == []

    def test_install_idempotent(self, scopes):
        rules_setup.install(scope="project", targets=["honesty"])
        result = rules_setup.install(scope="project", targets=["honesty"])
        assert result["files"][0]["before"] == "current"
        assert result["files"][0]["after"] == "current"


class TestUninstall:
    def test_uninstall_single_target(self, scopes):
        rules_setup.install(scope="project", targets=["honesty"])
        rules_setup.install(scope="project", targets=["markdown"])
        result = rules_setup.uninstall(scope="project", targets=["honesty"])

        assert not (scopes.project / ".claude/rules/ocd/honesty.md").exists()
        assert (scopes.project / ".claude/rules/ocd/markdown.md").is_file()
        paths = [f["path"] for f in result["files"]]
        assert paths == [".claude/rules/ocd/honesty.md"]

    def test_uninstall_multiple_targets(self, scopes):
        rules_setup.install(
            scope="project",
            targets=["honesty", "borrow-before-build", "clean-break"],
        )
        result = rules_setup.uninstall(
            scope="project",
            targets=["honesty", "clean-break"],
        )
        assert not (scopes.project / ".claude/rules/ocd/honesty.md").exists()
        assert not (scopes.project / ".claude/rules/ocd/clean-break.md").exists()
        assert (scopes.project / ".claude/rules/ocd/borrow-before-build.md").is_file()
        paths = [f["path"] for f in result["files"]]
        assert len(paths) == 2

    def test_uninstall_all(self, scopes):
        rules_setup.install(scope="project", targets=None)
        rules_setup.uninstall(scope="project", targets=None)
        assert not (scopes.project / ".claude/rules/ocd").exists()

    def test_uninstall_when_nothing_deployed(self, scopes):
        result = rules_setup.uninstall(scope="project", targets=["honesty"])
        assert result["files"] == []

    def test_uninstall_unsupported_scope(self, scopes):
        result = rules_setup.uninstall(scope="planet")
        assert any("unsupported scope" in e["value"] for e in result["extra"])

    def test_uninstall_user_scope_does_not_touch_project(self, scopes):
        rules_setup.install(scope="project", targets=["honesty"])
        rules_setup.install(scope="user", targets=["honesty"])
        rules_setup.uninstall(scope="user", targets=["honesty"])
        assert (scopes.project / ".claude/rules/ocd/honesty.md").is_file()
        assert not (scopes.user / "rules/ocd/honesty.md").exists()


class TestScopeIsolation:
    def test_install_at_one_scope_does_not_affect_other(self, scopes):
        rules_setup.install(scope="user", targets=["honesty"])
        project_status = rules_setup.status(scope="project")
        honesty_at_project = next(
            f for f in project_status["files"]
            if f["path"].endswith("honesty.md")
        )
        assert honesty_at_project["before"] == "absent"
