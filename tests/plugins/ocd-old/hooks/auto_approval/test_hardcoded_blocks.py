"""Tests for hardcoded command blocks in auto_approval hook."""

from hooks import auto_approval


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
