"""Unit tests for override_approvals hook."""

import pytest

import override_approvals as hook


# =========================================================================
# Layer 1 — Hardcoded blocks
# =========================================================================


class TestCheckHardcodedBlocks:
    def test_cd_blocked(self):
        assert hook.check_hardcoded_blocks("cd /tmp") is not None
        assert "cd" in hook.check_hardcoded_blocks("cd /tmp").lower()

    def test_cd_bare_blocked(self):
        assert hook.check_hardcoded_blocks("cd") is not None

    def test_pushd_blocked(self):
        assert hook.check_hardcoded_blocks("pushd /tmp") is not None

    def test_popd_blocked(self):
        assert hook.check_hardcoded_blocks("popd") is not None

    def test_cd_substring_not_blocked(self):
        assert hook.check_hardcoded_blocks("abcd foo") is None

    def test_compound_and(self):
        result = hook.check_hardcoded_blocks("ls && pwd")
        assert result is not None
        assert "&&" in result

    def test_compound_or(self):
        result = hook.check_hardcoded_blocks("ls || pwd")
        assert result is not None
        assert "||" in result

    def test_semicolon(self):
        result = hook.check_hardcoded_blocks("ls; pwd")
        assert result is not None
        assert ";" in result

    def test_pipe(self):
        result = hook.check_hardcoded_blocks("cat foo | grep bar")
        assert result is not None
        assert "|" in result

    def test_operators_inside_single_quotes_allowed(self):
        assert hook.check_hardcoded_blocks("echo '&& || ; |'") is None

    def test_operators_inside_double_quotes_allowed(self):
        assert hook.check_hardcoded_blocks('echo "&& || ; |"') is None

    def test_simple_command_allowed(self):
        assert hook.check_hardcoded_blocks("ls -la") is None

    def test_git_command_allowed(self):
        assert hook.check_hardcoded_blocks("git status") is None

    def test_empty_command(self):
        assert hook.check_hardcoded_blocks("") is None


# =========================================================================
# Bash pattern matching
# =========================================================================


class TestMatchBashPattern:
    def test_verb_colon_star(self):
        assert hook.match_bash_pattern("rm -rf /tmp/foo", "rm:*") is True

    def test_verb_colon_star_exact(self):
        assert hook.match_bash_pattern("rm", "rm:*") is True

    def test_verb_colon_star_no_match(self):
        assert hook.match_bash_pattern("mv foo bar", "rm:*") is False

    def test_path_star(self):
        assert hook.match_bash_pattern(".claude/foo.sh", ".claude/*") is True

    def test_path_star_no_match(self):
        assert hook.match_bash_pattern("ls .claude/", ".claude/*") is False

    def test_exact_match(self):
        assert hook.match_bash_pattern("pwd", "pwd") is True

    def test_exact_match_with_args(self):
        assert hook.match_bash_pattern("pwd -P", "pwd") is True

    def test_exact_no_match(self):
        assert hook.match_bash_pattern("ls -la", "pwd") is False

    def test_multi_word_verb(self):
        assert hook.match_bash_pattern("uv sync --frozen", "uv sync:*") is True

    def test_multi_word_verb_no_match(self):
        assert hook.match_bash_pattern("uv add foo", "uv sync:*") is False

    def test_venv_bin_star(self):
        assert hook.match_bash_pattern(".venv/bin/pytest foo", ".venv/bin/*") is True

    def test_cli_py(self):
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
    def test_allowed_command(self):
        assert hook.is_bash_allowed("ls -la", SAMPLE_SETTINGS) is True

    def test_allowed_rm(self):
        assert hook.is_bash_allowed("rm /tmp/foo", SAMPLE_SETTINGS) is True

    def test_allowed_git(self):
        assert hook.is_bash_allowed("git status", SAMPLE_SETTINGS) is True

    def test_allowed_pwd(self):
        assert hook.is_bash_allowed("pwd", SAMPLE_SETTINGS) is True

    def test_allowed_claude_script(self):
        assert hook.is_bash_allowed(".claude/hooks/foo.sh", SAMPLE_SETTINGS) is True

    def test_disallowed_command(self):
        assert hook.is_bash_allowed("curl http://example.com", SAMPLE_SETTINGS) is False

    def test_empty_settings(self):
        assert hook.is_bash_allowed("ls", {}) is False


class TestIsBashDenied:
    def test_not_denied_when_empty(self):
        assert hook.is_bash_denied("ls", SAMPLE_SETTINGS) is False

    def test_denied_when_matched(self):
        settings = {"permissions": {"deny": ["Bash(rm:*)"]}}
        assert hook.is_bash_denied("rm -rf /", settings) is True

    def test_not_denied_when_no_match(self):
        settings = {"permissions": {"deny": ["Bash(rm:*)"]}}
        assert hook.is_bash_denied("ls", settings) is False


# =========================================================================
# Dynamic settings enforcement — Edit/Write
# =========================================================================


class TestIsPathDenied:
    def test_not_denied_empty_list(self):
        assert hook.is_path_denied("/foo/bar", "Edit", SAMPLE_SETTINGS) is False

    def test_denied_by_tool_pattern(self):
        settings = {"permissions": {"deny": ["Edit(.env)"]}}
        assert hook.is_path_denied(".env", "Edit", settings) is True

    def test_denied_by_glob(self):
        settings = {"permissions": {"deny": ["Write(secrets/**)"]}}
        assert hook.is_path_denied("secrets/api/key.json", "Write", settings) is True

    def test_not_denied_wrong_tool(self):
        settings = {"permissions": {"deny": ["Edit(.env)"]}}
        assert hook.is_path_denied(".env", "Write", settings) is False

    def test_denied_by_blanket_tool(self):
        settings = {"permissions": {"deny": ["Edit"]}}
        assert hook.is_path_denied("anything.txt", "Edit", settings) is True


class TestGlobMatch:
    def test_double_star(self):
        assert hook._glob_match("a/b/c/d.txt", "a/**") is True

    def test_single_star(self):
        assert hook._glob_match("a/foo.txt", "a/*.txt") is True

    def test_single_star_no_slash(self):
        assert hook._glob_match("a/b/foo.txt", "a/*.txt") is False

    def test_exact(self):
        assert hook._glob_match(".env", ".env") is True

    def test_no_match(self):
        assert hook._glob_match("foo.txt", "bar.txt") is False


# =========================================================================
# Path resolution and directory checks
# =========================================================================


class TestIsWithinAllowedDirs:
    def test_project_dir(self):
        settings = {"permissions": {"additionalDirectories": []}}
        assert hook.is_within_allowed_dirs("/project/foo.py", "/project", settings) is True

    def test_outside_project(self):
        settings = {"permissions": {"additionalDirectories": []}}
        assert hook.is_within_allowed_dirs("/other/foo.py", "/project", settings) is False

    def test_additional_directory(self):
        settings = {"permissions": {"additionalDirectories": ["/extra"]}}
        assert hook.is_within_allowed_dirs("/extra/foo.py", "/project", settings) is True

    def test_relative_dot_directory(self):
        settings = {"permissions": {"additionalDirectories": ["."]}}
        project = "/home/dev/projects/myproject"
        path = project + "/sub/file.py"
        assert hook.is_within_allowed_dirs(path, project, settings) is True


class TestIsToolInList:
    def test_present(self):
        assert hook.is_tool_in_list("Edit", ["Edit", "Write"]) is True

    def test_absent(self):
        assert hook.is_tool_in_list("Bash", ["Edit", "Write"]) is False

    def test_bash_pattern_not_blanket(self):
        assert hook.is_tool_in_list("Bash", ["Bash(ls:*)"]) is False
