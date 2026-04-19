"""Tests for bash and glob pattern matching in auto_approval hook."""

from hooks import auto_approval


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
# Glob matching
# =========================================================================


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
