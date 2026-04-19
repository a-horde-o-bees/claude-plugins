"""Tests for path resolution, directory containment, and settings merge."""

from pathlib import Path

from hooks import auto_approval


class TestIsWithinDirectory:
    def test_file_in_directory(self) -> None:
        assert auto_approval.is_within_directory(Path("/project/foo.py"), Path("/project")) is True

    def test_file_in_subdirectory(self) -> None:
        assert auto_approval.is_within_directory(Path("/project/a/b/c.py"), Path("/project")) is True

    def test_directory_equals_target(self) -> None:
        assert auto_approval.is_within_directory(Path("/project"), Path("/project")) is True

    def test_outside_directory(self) -> None:
        assert auto_approval.is_within_directory(Path("/other/foo.py"), Path("/project")) is False

    def test_prefix_attack(self) -> None:
        """'/project-evil/foo' must NOT match '/project'."""
        assert auto_approval.is_within_directory(Path("/project-evil/foo.py"), Path("/project")) is False

    def test_sibling_directory(self) -> None:
        assert auto_approval.is_within_directory(Path("/projects/other/f.py"), Path("/projects/myapp")) is False


class TestIsWithinAllowedDirs:
    def test_project_dir(self) -> None:
        settings = {"permissions": {"additionalDirectories": []}}
        assert auto_approval.is_within_allowed_dirs(Path("/project/foo.py"), Path("/project"), settings) is True

    def test_outside_project(self) -> None:
        settings = {"permissions": {"additionalDirectories": []}}
        assert auto_approval.is_within_allowed_dirs(Path("/other/foo.py"), Path("/project"), settings) is False

    def test_additional_directory(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["/extra"]}}
        assert auto_approval.is_within_allowed_dirs(Path("/extra/foo.py"), Path("/project"), settings) is True

    def test_tilde_expansion(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["~/projects"]}}
        dirs = auto_approval.get_allowed_directories(Path("/project"), settings)
        expected = Path.home() / "projects"
        assert expected in dirs


class TestResolvePath:
    def test_relative_path(self) -> None:
        result = auto_approval.resolve_path("foo/bar.py", Path("/project"))
        assert result == Path("/project/foo/bar.py")

    def test_absolute_path(self) -> None:
        result = auto_approval.resolve_path("/absolute/bar.py", Path("/project"))
        assert result == Path("/absolute/bar.py")

    def test_parent_traversal(self) -> None:
        result = auto_approval.resolve_path("foo/../bar.py", Path("/project"))
        assert result == Path("/project/bar.py")


class TestSettingsMerge:
    def test_unions_allow_lists(self) -> None:
        global_s = {"permissions": {"allow": ["Bash(ls:*)"], "deny": []}}
        project_s = {"permissions": {"allow": ["Bash(git:*)"], "deny": []}}
        merged = auto_approval.merge_settings(global_s, project_s)
        assert "Bash(ls:*)" in merged["permissions"]["allow"]
        assert "Bash(git:*)" in merged["permissions"]["allow"]

    def test_deduplicates(self) -> None:
        global_s = {"permissions": {"allow": ["Bash(ls:*)"], "deny": []}}
        project_s = {"permissions": {"allow": ["Bash(ls:*)"], "deny": []}}
        merged = auto_approval.merge_settings(global_s, project_s)
        assert merged["permissions"]["allow"].count("Bash(ls:*)") == 1
