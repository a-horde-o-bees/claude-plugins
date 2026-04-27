# Sample

## Identification

### url

https://github.com/misbahsy/video-audio-mcp

### stars

71

### last-commit (date or relative)

not captured; repo shows "6 Commits" on main — small, possibly early-stage

### license

MIT

### default branch

main

### one-line purpose

Video/audio processing MCP server — 30+ ffmpeg-backed tools for media conversion and manipulation.

## 1. Language and runtime

### language(s) + version constraints

Python 100%; `requires-python = ">=3.13"` (pyproject)

### framework/SDK in use

raw `mcp[cli]>=1.9.0` + `ffmpeg-python>=0.2.0`

### pitfalls observed

- **Python 3.13 floor** — aggressive, like hass-mcp

## 2. Transport

### supported transports

stdio

### how selected

default

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

clone + `uv sync` / `pip install -r requirements.txt`

### published package name(s)

project name in pyproject is `video-edit-mcp` — presumably not on PyPI (no install command from PyPI)

### install commands shown in README

`uv sync`; `pip install -r requirements.txt`

### pitfalls observed

- **pyproject project-name vs repo-name drift** — an axis for "what is the authoritative identifier?" — PyPI name, repo name, console-script name can all diverge

## 4. Entry point / launch

### command(s) users/hosts run

`uv run server.py`; `python server.py`

### wrapper scripts, launchers, stubs

bare script `server.py`

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

env-level ffmpeg binary availability; no documented runtime config

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

none — local media processing

### where credentials come from

N/A

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

not applicable — local file operations

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

**30+ tools** covering:

- Video: format conversion, trimming, resolution scaling, codec changes, overlays
- Audio: format conversion, bitrate/sample rate adjustment, channel configuration
- Creative: text overlays, watermarks, subtitles, transitions
- Advanced: concatenation, B-roll insertion, silence removal

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not captured

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

Not enumerated

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest test suite in `tests/` — 30+ functions tested; `pytest` declared as a runtime dep (unusual — it should be a dev dep)

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

README includes a GitHub Actions example with FFmpeg install step — pattern is documented; actual `.github/workflows/*.yml` presence not confirmed

### pitfalls observed

- **System-tool dependency (ffmpeg)** — requires out-of-band install; README's GitHub Actions example includes an explicit `apt-get install ffmpeg` step

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

none captured

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

GitHub Actions YAML example in README

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-file server (`server.py`)

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- **System-tool dependency (ffmpeg)** — requires out-of-band install; README's GitHub Actions example includes an explicit `apt-get install ffmpeg` step
- **`ffmpeg-python` library** — wraps ffmpeg CLI via Python; alternative approaches wrap ffmpeg directly via subprocess or call `pyav`
- **`pytest` in runtime deps** — probably an oversight; tests shouldn't require installing pytest for users running the server
- **Python 3.13 floor** — aggressive, like hass-mcp
- Project name in `pyproject.toml` (`video-edit-mcp`) differs from repo name (`video-audio-mcp`) — mild naming inconsistency

## 18. Unanticipated axes observed

- **System-binary dependency as a distribution concern** — ffmpeg must be on PATH; CI docs include install step; similar constraint exists for Tesseract in PDF OCR servers. Forms a server class "system-dep servers" where Docker distribution is the only self-contained option
- **Tool-count density** — 30+ tools for file processing from a 6-commit repo; shows how quickly a FFmpeg wrapper can scale via codegen-like uniformity
- **pyproject project-name vs repo-name drift** — an axis for "what is the authoritative identifier?" — PyPI name, repo name, console-script name can all diverge

## 19. Python-specific

### SDK / framework variant

- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: raw `mcp[cli]>=1.9.0` — `[cli]` extra installs FastMCP-style helpers; README says "Built with FastMCP framework" — likely FastMCP 1.x via the SDK, not the standalone 2.x
- version pin from pyproject.toml: `mcp[cli]>=1.9.0`, `ffmpeg-python>=0.2.0`, `pillow>=11.2.1`, `pytest>=8.3.5`
- import pattern observed: likely `from mcp.server.fastmcp import FastMCP` — the 1.x-in-SDK path

### Python version floor

`requires-python` value: `>=3.13`

### Packaging

- build backend: not extracted
- lock file present: `uv.lock` implied
- version manager convention: `uv`

### Entry point

- `[project.scripts]` console script / `__main__.py` module / bare script / other: **bare script** (`server.py`)
- actual console-script name(s): none
- host-config snippet shape: `uv run server.py` — direct script invocation from an absolute path

### Install workflow expected of end users

install form + one-liner from README: `uv sync` (or `pip install -r requirements.txt`)

### Async and tool signatures

sync `def` or `async def`: `ffmpeg-python` is sync — likely sync handlers

### Type / schema strategy

Pydantic / dataclasses / TypedDict / raw dict / Annotated: FastMCP-1.x-auto-derived from type hints via the SDK

### Testing

- pytest / pytest-asyncio / unittest / none: pytest
- fixture style: 30+ function-level tests

### Dev ergonomics

mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: documented GitHub Actions pattern

### Notable Python-specific choices

- `pytest` declared as a runtime dep — likely a mistake or a side-effect of listing all deps uniformly
- Uses `pillow` — suggests thumbnail/frame capture features in addition to pure ffmpeg ops
- Python 3.13 floor on a 6-commit repo — tracking bleeding-edge Python

## 20. Gaps

what couldn't be determined: exact stars date, console-script presence (pyproject omitted `[project.scripts]`), actual build backend, whether CI is real or only documented as a pattern, confirmation of FastMCP-in-SDK vs standalone
