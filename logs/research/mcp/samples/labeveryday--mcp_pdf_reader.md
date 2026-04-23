# labeveryday/mcp_pdf_reader

## Identification
- url: https://github.com/labeveryday/mcp_pdf_reader
- stars: 12
- last-commit (date or relative): not captured
- license: MIT
- default branch: main
- one-line purpose: PDF reader MCP server — PDF extraction + OCR; bare-script server.

## 1. Language and runtime
- language(s) + version constraints: Python 100%; version from `.python-version` file (specific version not captured)
- framework/SDK in use: FastMCP (marketed as "Modern MCP server framework")
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio
- how selected: default
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: source-only (clone + install); no PyPI publication documented
- published package name(s): none documented
- install commands shown in README:
  - `uv sync`
  - `pip install fastmcp PyMuPDF pytesseract Pillow`
- pitfalls observed:
  - No PyPI publication — consumption is clone-and-run
  - **No formal packaging** — the "script as a server" pattern competes with the console-script-PyPI pattern and represents a simpler distribution tier
  - what couldn't be determined: exact stars/commit date, tool count, whether there's a MANIFEST.in or setup.py, PyPI status, test presence, license file presence

## 4. Entry point / launch
- command(s) users/hosts run: `uv run python pdf_reader_server.py`; `python pdf_reader_server.py`
- wrapper scripts, launchers, stubs: bare script `pdf_reader_server.py` — no console script
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment / system-level Tesseract install; no runtime config surface documented
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: none — local file processing
- where credentials come from: N/A
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: not applicable — purely local file operations
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: tools for PDF text extraction, PDF image extraction, OCR text recognition within images
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not documented
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
Not captured explicitly per host
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: no CI/CD or test files mentioned in README
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: none documented
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: none mentioned
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: none captured
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single-file server (`pdf_reader_server.py`)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- **Bare-script entry point** — no `pyproject.toml` `[project.scripts]` entry; server is literally `python pdf_reader_server.py`
- **System dependency (Tesseract OCR)** — requires out-of-band install on the host; the README surfaces this
- PyMuPDF + pytesseract + Pillow stack — the default Python PDF+OCR toolkit
- No PyPI publication — consumption is clone-and-run

## 18. Unanticipated axes observed
- **System-tool dependency (Tesseract) surfaces on the user** — a design category where the MCP server cannot self-install its dependencies; similar to ffmpeg servers
- **No formal packaging** — the "script as a server" pattern competes with the console-script-PyPI pattern and represents a simpler distribution tier
- **Zero-auth, file-processing servers** form a distinct family — like AWS documentation server, but for local file inputs rather than remote public docs

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: FastMCP (variant not specified — README says "FastMCP framework"); installed via `pip install fastmcp` → implies standalone FastMCP 2.x package
- version pin from pyproject.toml: not captured precisely
- import pattern observed: likely `from fastmcp import FastMCP` given `pip install fastmcp`

### Python version floor
- `requires-python` value: not captured directly; `.python-version` present

### Packaging
- build backend: not applicable — single script, likely no build
- lock file present: `uv.lock` implied by `uv sync` invocation
- version manager convention: `uv`

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: **bare script** (`python pdf_reader_server.py`)
- actual console-script name(s): none
- host-config snippet shape: absolute path to `pdf_reader_server.py` via `uv run` or `python`

### Install workflow expected of end users
- install form + one-liner from README: `uv sync` then `uv run python pdf_reader_server.py`; plus system-level Tesseract install

### Async and tool signatures
- sync `def` or `async def`: PyMuPDF and pytesseract are sync — likely sync handlers

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: FastMCP 2.x auto-derives from type hints

### Testing
- pytest / pytest-asyncio / unittest / none: none documented

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: none documented

### Notable Python-specific choices
- File-processing stack is purely CPU-bound — async offers little value; sync handlers appropriate
- Bare-script server pattern demonstrates FastMCP 2.x's low-ceremony surface

## 20. Gaps
- what couldn't be determined: exact stars/commit date, tool count, whether there's a MANIFEST.in or setup.py, PyPI status, test presence, license file presence
