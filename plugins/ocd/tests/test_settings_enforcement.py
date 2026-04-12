"""Tests for dynamic settings enforcement (allow/deny rules) in auto_approval hook."""

from hooks import auto_approval


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


# =========================================================================
# Compound command dispatch
# =========================================================================


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
# Bash allow/deny
# =========================================================================


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
# Path deny (Edit/Write)
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
