# Sample

Mirrors of `https://github.com/misbahsy/video-audio-mcp`. Video/audio processing MCP server — 30+ ffmpeg-backed tools for media conversion and manipulation. 71 stars, MIT, default branch `main`, small repo (~6 commits).

## Server runtime

### Python with FastMCP

Python 100% server using `mcp[cli]>=1.9.0` — `[cli]` extra installs FastMCP-style helpers; README says "Built with FastMCP framework" — likely FastMCP 1.x via the SDK rather than the standalone 2.x. Import pattern likely `from mcp.server.fastmcp import FastMCP` (the 1.x-in-SDK path). Python 3.13+ floor (`requires-python = ">=3.13"`) is aggressive. `ffmpeg-python>=0.2.0` for ffmpeg wrapping; `pillow>=11.2.1` for image work. FastMCP 1.x-auto-derived schemas from type hints via the SDK; `ffmpeg-python` is sync so handlers likely sync.

## Transport

### stdio

Default and only transport.

### Selection mechanism

Implicit single mode — stdio only.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

30+ tools wrapping ffmpeg media operations exhaustively: Video — format conversion, trimming, resolution scaling, codec changes, overlays. Audio — format conversion, bitrate/sample rate adjustment, channel configuration. Creative — text overlays, watermarks, subtitles, transitions. Advanced — concatenation, B-roll insertion, silence removal.

## Configuration delivery

### Environment variables

Implicit env-level ffmpeg binary availability; no documented runtime configuration env vars.

## Authentication

### None / implicit (local-resource gating)

No auth — local media processing on user-supplied files.

## Multi-tenancy

### Single-user / single-tenant per process

N/A — local file operations on user filesystem.

## Distribution channel

### Source clone with editable install

`uv sync` or `pip install -r requirements.txt` after clone — no PyPI publication. The pyproject project name is `video-edit-mcp` (mismatched with repo name `video-audio-mcp`); not on PyPI.

## Entry point and launch

### Bare interpreter + script path

`uv run server.py` or `python server.py` — bare `server.py` script; no installable console script declared.

## Build and packaging

### Hatchling + uv (Python)

`uv sync`-managed install; `uv.lock` implied. Build backend not surfaced.

### Python version pinning

`requires-python = ">=3.13"` — aggressive modern-Python target.

### Pin discipline (Python)

Dependency pins: `mcp[cli]>=1.9.0`, `ffmpeg-python>=0.2.0`, `pillow>=11.2.1`, `pytest>=8.3.5`. `pytest` declared in `[project.dependencies]` rather than as a dev extra — almost certainly an oversight; ships test framework to all consumers.

### System-level dependencies

System binary required (CLI on PATH) — ffmpeg must be installed out-of-band; the package manager cannot install it. README's GitHub Actions example explicitly includes `apt-get install ffmpeg`.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP-1.x-auto-derived schemas from type hints via the SDK.

### Async model (cross-cutting)

Sync throughout — `ffmpeg-python` is sync; handlers likely sync.

## Test stack

### pytest with async + coverage

pytest test suite in `tests/` — 30+ functions tested.

### `pytest` declared as runtime dependency

Test deps NOT properly gated — `pytest` lands under `[project.dependencies]` rather than `[dependency-groups]`. Likely oversight rather than design choice.

## CI

### Documented but not necessarily wired

README includes a GitHub Actions YAML example with `apt-get install ffmpeg` step; whether `.github/workflows/*.yml` actually exists not confirmed. The pattern is documented as a copy-paste seed for downstream consumers.

## Container artifacts

### No container artifacts

No Dockerfile or docker-compose captured.

## Observability

### None / unspecified

No logging/observability documented at the project level.

## Host integration

### No host integration documentation

Host integrations not enumerated in the sample.

## Repository layout

### Single-file script / monolith

Single-file server (`server.py`) — minimum viable layout.

## Documentation surface

### README as the canonical surface

README is the canonical surface; includes a documented GitHub Actions YAML example for CI seed.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

Small repo, ~6 commits.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` directory or Claude Code wrapper.
