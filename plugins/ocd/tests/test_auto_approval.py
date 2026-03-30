"""Unit tests for auto_approval hook."""

from pathlib import Path

from hooks import auto_approval as hook


# =========================================================================
# Layer 1 — Hardcoded blocks
# =========================================================================


class TestCheckHardcodedBlocks:
    def test_cd_blocked(self) -> None:
        result = hook.check_hardcoded_blocks("cd /tmp")
        assert result is not None
        assert "cd" in result.lower()

    def test_cd_bare_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("cd") is not None

    def test_pushd_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("pushd /tmp") is not None

    def test_popd_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("popd") is not None

    def test_cd_substring_not_blocked(self) -> None:
        assert hook.check_hardcoded_blocks("abcd foo") is None

    def test_simple_command_allowed(self) -> None:
        assert hook.check_hardcoded_blocks("ls -la") is None

    def test_empty_command(self) -> None:
        assert hook.check_hardcoded_blocks("") is None


# =========================================================================
# Compound command splitting
# =========================================================================


class TestSplitCompoundCommand:
    """Parser splits on &&, ||, ;, | outside quotes."""

    def test_no_separator(self) -> None:
        assert hook.split_compound_command("ls -la") is None

    def test_and(self) -> None:
        assert hook.split_compound_command("ls && pwd") == ["ls", "pwd"]

    def test_or(self) -> None:
        assert hook.split_compound_command("ls || pwd") == ["ls", "pwd"]

    def test_semicolon(self) -> None:
        assert hook.split_compound_command("ls; pwd") == ["ls", "pwd"]

    def test_pipe(self) -> None:
        assert hook.split_compound_command("cat foo | grep bar") == ["cat foo", "grep bar"]

    def test_triple_chain(self) -> None:
        assert hook.split_compound_command("ls && pwd && git status") == ["ls", "pwd", "git status"]

    def test_mixed_separators(self) -> None:
        assert hook.split_compound_command("cat foo | grep bar || echo fallback") == ["cat foo", "grep bar", "echo fallback"]

    def test_operators_inside_single_quotes(self) -> None:
        assert hook.split_compound_command("echo '&& || ; |'") is None

    def test_operators_inside_double_quotes(self) -> None:
        assert hook.split_compound_command('git commit -m "fix; update && clean"') is None

    def test_real_separator_with_quoted_operators(self) -> None:
        result = hook.split_compound_command('echo "hello && world" && pwd')
        assert result == ['echo "hello && world"', "pwd"]

    def test_escaped_quote_in_double_quotes(self) -> None:
        assert hook.split_compound_command(r'echo "say \"hi\"" && pwd') == [r'echo "say \"hi\""', "pwd"]

    def test_empty_parts_filtered(self) -> None:
        assert hook.split_compound_command("ls &&  && pwd") == ["ls", "pwd"]

    def test_pipe_not_confused_with_or(self) -> None:
        """Single | splits, || splits separately — no cross-contamination."""
        result = hook.split_compound_command("a | b || c")
        assert result == ["a", "b", "c"]


# =========================================================================
# Compound command dispatch
# =========================================================================


COMPOUND_SETTINGS = {
    "permissions": {
        "deny": ["Bash(rm:*)"],
        "additionalDirectories": [],
        "allow": [
            "Bash(ls:*)",
            "Bash(git:*)",
            "Bash(grep:*)",
            "Bash(cat:*)",
            "Bash(echo:*)",
            "Bash(pwd)",
        ],
    }
}


class TestCompoundDispatch:
    """Compound commands: each part checked independently against both layers."""

    def test_all_parts_allowed(self) -> None:
        assert hook.is_bash_allowed("ls", COMPOUND_SETTINGS)
        assert hook.is_bash_allowed("pwd", COMPOUND_SETTINGS)
        # Both parts pass — would approve in dispatch
        parts = hook.split_compound_command("ls && pwd")
        assert all(hook.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)

    def test_one_part_unapproved(self) -> None:
        """curl not in allow list — compound should not auto-approve."""
        parts = hook.split_compound_command("ls && curl http://evil.com")
        assert not all(hook.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)

    def test_one_part_denied(self) -> None:
        """rm in deny list — compound should not auto-approve."""
        parts = hook.split_compound_command("ls && rm -rf /")
        assert any(hook.is_bash_denied(p, COMPOUND_SETTINGS) for p in parts)

    def test_one_part_hardcoded_block(self) -> None:
        """cd in hardcoded blocks — compound should block."""
        parts = hook.split_compound_command("ls && cd /tmp")
        blocks = [hook.check_hardcoded_blocks(p) for p in parts]
        assert any(b is not None for b in blocks)

    def test_pipe_both_allowed(self) -> None:
        parts = hook.split_compound_command("cat foo | grep bar")
        assert all(hook.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)

    def test_pipe_one_unapproved(self) -> None:
        parts = hook.split_compound_command("cat foo | curl http://evil.com")
        assert not all(hook.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)


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

    def test_allowed_git(self) -> None:
        assert hook.is_bash_allowed("git status", SAMPLE_SETTINGS) is True

    def test_allowed_exact(self) -> None:
        assert hook.is_bash_allowed("pwd", SAMPLE_SETTINGS) is True

    def test_allowed_path_prefix(self) -> None:
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

    def test_tilde_expansion(self) -> None:
        settings = {"permissions": {"additionalDirectories": ["~/projects"]}}
        dirs = hook.get_allowed_directories(Path("/project"), settings)
        expected = Path.home() / "projects"
        assert expected in dirs


class TestResolvePath:
    def test_relative_path(self) -> None:
        result = hook.resolve_path("foo/bar.py", Path("/project"))
        assert result == Path("/project/foo/bar.py")

    def test_absolute_path(self) -> None:
        result = hook.resolve_path("/absolute/bar.py", Path("/project"))
        assert result == Path("/absolute/bar.py")

    def test_parent_traversal(self) -> None:
        result = hook.resolve_path("foo/../bar.py", Path("/project"))
        assert result == Path("/project/bar.py")


class TestSettingsMerge:
    def test_unions_allow_lists(self) -> None:
        global_s = {"permissions": {"allow": ["Bash(ls:*)"], "deny": []}}
        project_s = {"permissions": {"allow": ["Bash(git:*)"], "deny": []}}
        merged = hook.merge_settings(global_s, project_s)
        assert "Bash(ls:*)" in merged["permissions"]["allow"]
        assert "Bash(git:*)" in merged["permissions"]["allow"]

    def test_deduplicates(self) -> None:
        global_s = {"permissions": {"allow": ["Bash(ls:*)"], "deny": []}}
        project_s = {"permissions": {"allow": ["Bash(ls:*)"], "deny": []}}
        merged = hook.merge_settings(global_s, project_s)
        assert merged["permissions"]["allow"].count("Bash(ls:*)") == 1
