"""MCP server presentation layer.

Each module in this package exposes a thin FastMCP server that wraps
business logic from a domain library under ``lib/``. Servers are
launched via ``run.py`` with module syntax (e.g.,
``python3 run.py servers.navigator``) so relative imports resolve.
"""
