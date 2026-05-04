# Sample

Mirrors of `https://github.com/labeveryday/mcp_pdf_reader`. PDF reader MCP server — bare-script Python server providing PDF text extraction, image extraction, and OCR via PyMuPDF + pytesseract + Pillow. 12 stars, MIT, default branch `main`.

## Server runtime

### Python with FastMCP

Python 100% server built on FastMCP (marketed as "Modern MCP server framework"). FastMCP variant not specified; installed via `pip install fastmcp` → standalone FastMCP 2.x package implied. Import pattern likely `from fastmcp import FastMCP` given the install command. Version pin not captured. `.python-version` present; `requires-python` value not captured directly. Sync handlers likely (PyMuPDF and pytesseract are sync).

## Transport

### stdio

Default transport.

## Capability surface

### Tools-only, hand-curated narrow surface

Hand-curated tools for PDF text extraction, PDF image extraction, and OCR text recognition within images.

## Configuration delivery

### Environment variables

System-level Tesseract install required out-of-band; no runtime config surface documented beyond environment.

## Authentication

### None / implicit (local-resource gating)

No authentication; local file processing only.

## Multi-tenancy

### Single-user / single-tenant per process

Local file operations; no tenancy concerns.

## Distribution channel

### Source clone with editable install

Source-only — `git clone` followed by `uv sync` or `pip install fastmcp PyMuPDF pytesseract Pillow`. No PyPI publication; consumption is clone-and-run.

## Entry point and launch

### Bare interpreter + script path

`uv run python pdf_reader_server.py` or `python pdf_reader_server.py` — bare script, no console script registered. Host-config snippet shape: absolute path to `pdf_reader_server.py` via `uv run` or `python`.

## Build and packaging

### Bare script (no build)

Single-file `.py` server with no `pyproject.toml` build backend; `uv sync` against ad-hoc dependency declarations. `uv.lock` implied by `uv sync` invocation.

### System-level dependencies

Tesseract OCR system binary required on the host — `apt-get install tesseract-ocr` (or platform equivalent). Package manager cannot install it; README surfaces the install responsibility on the user. Docker would become the only self-contained distribution path if added.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP 2.x auto-derives schema from Python signatures.

### Async model (cross-cutting)

Sync throughout — PyMuPDF and pytesseract are sync libraries; CPU-bound file processing means async offers little value.

## Repository layout

### Single-file script / monolith

The entire server is `pdf_reader_server.py` — a single file at repo root. The minimum viable layout for a "hackable" community server.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
