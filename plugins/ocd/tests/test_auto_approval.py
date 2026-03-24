"""Unit tests for auto_approval hook."""

from pathlib import Path

import auto_approval as hook


# =========================================================================
# Layer 1 — Hardcoded blocks
# =========================================================================


class TestCheckHardcodedBlocks:
    def test_cd_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("cd /tmp") is not None
        assert "cd" in hook.check_hardcoded_blocks("cd /tmp").lower()

    def test_cd_bare_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("cd") is not None

    def test_pushd_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("pushd /tmp") is not None

    def test_popd_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("popd") is not None

    def test_cd_substring_not_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("abcd foo") is None

    def test_compound_and(self) -> None:
        result = hook.check_hardcoded_blocks("ls && pwd")
        assert result is not None
        assert "&&" in result

    def test_compound_or(self) -> None:
        result = hook.check_hardcoded_blocks("ls || pwd")
        assert result is not None
        assert "||" in result

    def test_semicolon(self) -> None:
        result = hook.check_hardcoded_blocks("ls; pwd")
        assert result is not None
        assert ";" in result

    def test_pipe(self) -> None:
        result = hook.check_hardcoded_blocks("cat foo | grep bar")
        assert result is not None
        assert "|" in result

    def test_operators_inside_single_quotes_allowed(self) -> None:
        assert hook.check_hardcoded_blocks("echo '&& || ; |'") is None

    def test_operators_inside_double_quotes_allowed(self) -> None:
        assert hook.check_hardcoded_blocks('echo "&& || ; |"') is None

    def test_simple_command_allowed(self) -> None:
        assert hook.check_hardcoded_blocks("ls -la") is None

    def test_git_command_allowed(self) -> None:
        assert hook.check_hardcoded_blocks("git status") is None

    def test_empty_command(self) -> None:
        assert hook.check_hardcoded_blocks("") is None


# =========================================================================
# Bash pattern matching
# =========================================================================


class TestMatchBashPattern:
    def test_verb_colon_star(self) -> None:
        assert hook.match_bash_pattern("rm -rf /tmp/foo", "rm:*") is True

    def test_verb_colon_star_exact(self) -> None:
        assert hook.match_bash_pattern("rm", "rm:*") is True

    def test_verb_colon_star_no_match(self) -> None:
        assert hook.match_bash_pattern("mv foo bar", "rm:*") is False

    def test_path_star(self) -> None:
        assert hook.match_bash_pattern(".claude/foo.sh", ".claude/*") is True

    def test_path_star_no_match(self) -> None:
        assert hook.match_bash_pattern("ls .claude/", ".claude/*") is False

    def test_exact_match(self) -> None:
        assert hook.match_bash_pattern("pwd", "pwd") is True

    def test_exact_match_with_args(self) -> None:
        assert hook.match_bash_pattern("pwd -P", "pwd") is True

    def test_exact_no_match(self) -> None:
        assert hook.match_bash_pattern("ls -la", "pwd") is False

    def test_multi_word_verb(self) -> None:
        assert hook.match_bash_pattern("uv sync --frozen", "uv sync:*") is True

    def test_multi_word_verb_no_match(self) -> None:
        assert hook.match_bash_pattern("uv add foo", "uv sync:*") is False

    def test_venv_bin_star(self) -> None:
        assert hook.match_bash_pattern(".venv/bin/pytest foo", ".venv/bin/*") is True

    def test_cli_py(self) -> None:
        assert hook.match_bash_pattern("./cli.py blueprint list", "./cli.py:*") is True


# =========================================================================
# Dynamic settings enforcement — Bash
# =========================================================================


SAMPLE_SETTINGS = {
    "permissions": {
        "deny": [],
        "additionalDirectories": [".", "~/projects"],
        "allow": [
            "Edit",
            "Write",
            "Bash(ls:*)",
            "Bash(rm:*)",
            "Bash(git:*)",
            "Bash(.claude/*)",
            "Bash(pwd)",
        ],
    }
}


class TestIsBashAllowed:
    def test_allowed_command(self) -> None:
        assert hook.is_bash_allowed("ls -la", SAMPLE_SETTINGS) is True

    def test_allowed_rm(self) -> None:
        assert hook.is_bash_allowed("rm /tmp/foo", SAMPLE_SETTINGS) is True

    def test_allowed_git(self) -> None:
        assert hook.is_bash_allowed("git status", SAMPLE_SETTINGS) is True

    def test_allowed_pwd(self) -> None:
        assert hook.is_bash_allowed("pwd", SAMPLE_SETTINGS) is True

    def test_allowed_claude_script(self) -> None:
        assert hook.is_bash_allowed(".claude/hooks/foo.sh", SAMPLE_SETTINGS) is True

    def test_disallowed_command(self) -> None:
        assert hook.is_bash_allowed("curl http://example.com", SAMPLE_SETTINGS) is False

    def test_empty_settings(self) -> None:
        assert hook.is_bash_allowed("ls", {}) is False


class TestIsBashDenied:
    def test_not_denied_when_empty(self) -> None:
        assert hook.is_bash_denied("ls", SAMPLE_SETTINGS) is False

    def test_denied_when_matched(self) -> None:
        settings = {"permissions": {"deny": ["Bash(rm:*)"]}}
        assert hook.is_bash_denied("rm -rf /", settings) is True

    def test_not_denied_when_no_match(self) -> None:
        settings = {"permissions": {"deny": ["Bash(rm:*)"]}}
        assert hook.is_bash_denied("ls", settings) is False


# =========================================================================
# Dynamic settings enforcement — Edit/Write
# =========================================================================


class TestIsPathDenied:
    def test_not_denied_empty_list(self) -> None:
        assert hook.is_path_denied("/foo/bar", "Edit", SAMPLE_SETTINGS) is False

    def test_denied_by_tool_pattern(self) -> None:
        settings = {"permissions": {"deny": ["Edit(.env)"]}}
        assert hook.is_path_denied(".env", "Edit", settings) is True

    def test_denied_by_glob(self) -> None:
        settings = {"permissions": {"deny": ["Write(secrets/**)"]}}
        assert hook.is_path_denied("secrets/api/key.json", "Write", settings) is True

    def test_not_denied_wrong_tool(self) -> None:
        settings = {"permissions": {"deny": ["Edit(.env)"]}}
        assert hook.is_path_denied(".env", "Write", settings) is False

    def test_denied_by_blanket_tool(self) -> None:
        settings = {"permissions": {"deny": ["Edit"]}}
        assert hook.is_path_denied("anything.txt", "Edit", settings) is True


class TestGlobMatch:
    def test_double_star(self) -> None:
        assert hook._glob_match("a/b/c/d.txt", "a/**") is True

    def test_single_star(self) -> None:
        assert hook._glob_match("a/foo.txt", "a/*.txt") is True

    def test_single_star_no_slash(self) -> None:
        assert hook._glob_match("a/b/foo.txt", "a/*.txt") is False

    def test_exact(self) -> None:
        assert hook._glob_match(".env", ".env") is True

    def test_no_match(self) -> None:
        assert hook._glob_match("foo.txt", "bar.txt") is False


# =========================================================================
# Path resolution and directory checks
# =========================================================================


class TestIsWithinAllowedDirs:
    def test_project_dir(self) -> None:
        settings = {"permissions": {"additionalDirectories": []}}
        assert hook.is_within_allowed_dirs(Path("/project/foo.py"), Path("/project"), settings) is True

    def test_outside_project(self) -> None:
        settings = {"permissions": {"additionalDirectories": []}}
        assert hook.is_within_allowed_dirs(Path("/other/foo.py"), Path("/project"), settings) is False

    def test_additional_directory(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["/extra"]}}
        assert hook.is_within_allowed_dirs(Path("/extra/foo.py"), Path("/project"), settings) is True

    def test_relative_dot_directory(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["."]}}
        project = Path("/home/dev/projects/myproject")
        path = project / "sub" / "file.py"
        assert hook.is_within_allowed_dirs(path, project, settings) is True


class TestResolvePath:
    def test_relative_path(self) -> None:
        result = hook.resolve_path("foo/bar.py", Path("/project"))
        assert result == Path("/project/foo/bar.py")

    def test_absolute_path(self) -> None:
        result = hook.resolve_path("/absolute/bar.py", Path("/project"))
        assert result == Path("/absolute/bar.py")

    def test_dot_relative(self) -> None:
        result = hook.resolve_path("./foo/bar.py", Path("/project"))
        assert result == Path("/project/foo/bar.py")

    def test_parent_traversal(self) -> None:
        result = hook.resolve_path("foo/../bar.py", Path("/project"))
        assert result == Path("/project/bar.py")

    def test_double_parent_traversal(self) -> None:
        result = hook.resolve_path("a/b/../../c.py", Path("/project"))
        assert result == Path("/project/c.py")


class TestIsWithinDirectory:
    def test_file_in_directory(self) -> None:
        assert hook.is_within_directory(Path("/project/foo.py"), Path("/project")) is True

    def test_file_in_subdirectory(self) -> None:
        assert hook.is_within_directory(Path("/project/a/b/c.py"), Path("/project")) is True

    def test_directory_equals_target(self) -> None:
        assert hook.is_within_directory(Path("/project"), Path("/project")) is True

    def test_outside_directory(self) -> None:
        assert hook.is_within_directory(Path("/other/foo.py"), Path("/project")) is False

    def test_prefix_attack(self) -> None:
        """'/project-evil/foo' must NOT match '/project'."""
        assert hook.is_within_directory(Path("/project-evil/foo.py"), Path("/project")) is False

    def test_sibling_directory(self) -> None:
        assert hook.is_within_directory(Path("/projects/other/f.py"), Path("/projects/myapp")) is False

    def test_root_directory(self) -> None:
        assert hook.is_within_directory(Path("/anything/at/all"), Path("/")) is True

    def test_trailing_slash(self) -> None:
        assert hook.is_within_directory(Path("/project/foo.py"), Path("/project/")) is True


class TestGetAllowedDirectories:
    def test_project_dir_always_included(self) -> None:
        settings = {"permissions": {"additionalDirectories": []}}
        dirs = hook.get_allowed_directories(Path("/project"), settings)
        assert Path("/project") in dirs

    def test_absolute_additional(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["/extra"]}}
        dirs = hook.get_allowed_directories(Path("/project"), settings)
        assert Path("/extra") in dirs

    def test_tilde_expansion(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["~/projects"]}}
        dirs = hook.get_allowed_directories(Path("/project"), settings)
        expected = Path.home() / "projects"
        assert expected in dirs

    def test_relative_resolved_against_project(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["../sibling"]}}
        dirs = hook.get_allowed_directories(Path("/home/dev/project"), settings)
        assert Path("/home/dev/sibling") in dirs

    def test_dot_resolves_to_project(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["."]}}
        project = Path("/home/dev/projects/myproject")
        dirs = hook.get_allowed_directories(project, settings)
        assert project in dirs

    def test_empty_settings(self) -> None:
        dirs = hook.get_allowed_directories(Path("/project"), {})
        assert dirs == {Path("/project")}


class TestIsToolInList:
    def test_present(self) -> None:
        assert hook.is_tool_in_list("Edit", ["Edit", "Write"]) is True

    def test_absent(self) -> None:
        assert hook.is_tool_in_list("Bash", ["Edit", "Write"]) is False

    def test_bash_pattern_not_blanket(self) -> None:
        assert hook.is_tool_in_list("Bash", ["Bash(ls:*)"]) is False
