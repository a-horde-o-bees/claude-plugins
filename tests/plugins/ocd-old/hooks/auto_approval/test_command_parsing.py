"""Tests for command parsing: splitting, env stripping, and loop expansion."""

from hooks import auto_approval


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
