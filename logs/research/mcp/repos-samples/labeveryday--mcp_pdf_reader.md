# Sample

## Identification

### url

https://github.com/labeveryday/mcp_pdf_reader

### stars

12

### last-commit

not captured

### license

MIT

### default branch

main

### one-line purpose

PDF reader MCP server — PDF extraction + OCR; bare-script server.

## Language and runtime

### language(s) + version constraints

Python 100%; version from `.python-version` file (specific version not captured)

### framework/SDK in use

FastMCP (marketed as "Modern MCP server framework")

## Transport

### supported transports

stdio

### how selected

default

## Distribution

### every mechanism observed

source-only (clone + install); no PyPI publication documented

### published package name(s)

none documented

### install commands shown in README

`uv sync`; `pip install fastmcp PyMuPDF pytesseract Pillow`

### pitfalls observed

No PyPI publication — consumption is clone-and-run.

## Entry point / launch

### command(s) users/hosts run

`uv run python pdf_reader_server.py`; `python pdf_reader_server.py`

### wrapper scripts, launchers, stubs

bare script `pdf_reader_server.py` — no console script

## Configuration surface

### how config reaches the server

environment / system-level Tesseract install; no runtime config surface documented

## Authentication

### flow

none — local file processing

### where credentials come from

N/A

## Multi-tenancy

### tenancy model

not applicable — purely local file operations

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools for PDF text extraction, PDF image extraction, OCR text recognition within images

## Observability

### logging destination + format, metrics, tracing, debug flags

not documented

## Host integrations shown in README or repo

Not captured explicitly per host.

## Claude Code plugin wrapper

### presence and shape

none

## Tests

### presence, framework, location, notable patterns

no CI/CD or test files mentioned in README

## CI

### presence, system, triggers, what it runs

none documented

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

none mentioned

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

none captured

## Repo layout

### single-package / monorepo / vendored / other

single-file server (`pdf_reader_server.py`)

## Notable structural choices

Bare-script entry point — no `pyproject.toml` `[project.scripts]` entry; server is literally `python pdf_reader_server.py`. System dependency (Tesseract OCR) requires out-of-band install on the host; the README surfaces this. PyMuPDF + pytesseract + Pillow stack — the default Python PDF+OCR toolkit. No PyPI publication — consumption is clone-and-run.

## Unanticipated axes observed

System-tool dependency (Tesseract) surfaces on the user — a design category where the MCP server cannot self-install its dependencies; similar to ffmpeg servers. No formal packaging — the "script as a server" pattern competes with the console-script-PyPI pattern and represents a simpler distribution tier. Zero-auth, file-processing servers form a distinct family — like AWS documentation server, but for local file inputs rather than remote public docs.

## Python-specific

### SDK / framework variant

FastMCP (variant not specified — README says "FastMCP framework"); installed via `pip install fastmcp` → implies standalone FastMCP 2.x package. Version pin not captured precisely. Import pattern observed likely `from fastmcp import FastMCP` given `pip install fastmcp`.

### Python version floor

`requires-python` value not captured directly; `.python-version` present.

### Packaging

Build backend not applicable — single script, likely no build. Lock file: `uv.lock` implied by `uv sync` invocation. Version manager convention: `uv`.

### Entry point

Bare script (`python pdf_reader_server.py`). No console-script names. Host-config snippet shape: absolute path to `pdf_reader_server.py` via `uv run` or `python`.

### Install workflow expected of end users

`uv sync` then `uv run python pdf_reader_server.py`; plus system-level Tesseract install.

### Async and tool signatures

PyMuPDF and pytesseract are sync — likely sync handlers.

### Type / schema strategy

FastMCP 2.x auto-derives from type hints.

### Testing

none documented

### Dev ergonomics

none documented

### Notable Python-specific choices

File-processing stack is purely CPU-bound — async offers little value; sync handlers appropriate. Bare-script server pattern demonstrates FastMCP 2.x's low-ceremony surface.

## Gaps

Exact stars/commit date, tool count, whether there's a MANIFEST.in or setup.py, PyPI status, test presence, license file presence.
