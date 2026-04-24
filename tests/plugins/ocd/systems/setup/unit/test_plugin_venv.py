"""Smoke check: every plugin-venv-only package from ocd's pyproject.toml must be importable during testing.

The intent is to fail loudly if the test runner gave us the wrong venv — e.g.,
the project `.venv` instead of the ocd plugin venv. If any of these imports
fail, the test runner is not providing a venv that matches the plugin's
declared dependencies, and any subsequent plugin-venv-dependent test would
fail with a misleading ImportError at an arbitrary point during collection.
"""

import importlib


class TestPluginVenv:
    def test_mcp_importable(self) -> None:
        importlib.import_module("mcp")

    def test_weasyprint_importable(self) -> None:
        importlib.import_module("weasyprint")

    def test_markdown_importable(self) -> None:
        importlib.import_module("markdown")
