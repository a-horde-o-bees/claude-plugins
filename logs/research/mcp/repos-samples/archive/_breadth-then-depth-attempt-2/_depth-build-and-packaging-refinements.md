# Depth Pass Refinements — Sample > Build and packaging

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### `Sample > Build and packaging > Hatchling + uv (Python)`

**Gap:** The path name pairs two orthogonal axes (build backend = hatchling, version manager = uv), but the supporting evidence shows the path is in practice "any uv-managed Python project," whether or not hatchling is actually the build backend. About 17 of 45 supporting samples explicitly confirm `hatchling.build`; another ~11 (AlwaysSany, baryhuang, ckreiling, isaaccorley, lanbaoshen, misbahsy, sajal2692, severity1, shibuiwilliam, shreyaskarnik, utensils, zongmin-yu) explicitly say "build backend not surfaced" while still placing the sample under this path because the project is uv-managed. The current description leads with "Hatchling + uv" as if both are confirmed, but the placement criterion the corpus actually uses is "uv as version manager; hatchling assumed unless overridden by Setuptools/Poetry/uv_build/Hatch-force-include."

**Sharpened text suggestion:**

```
The mainstream modern Python pattern: `uv` as the version manager (lockfile via `uv.lock`,
install via `uv sync` / `uvx` / editable `uv pip install -e`) with hatchling as the
dominant build backend (`build-backend = "hatchling.build"` in `pyproject.toml`).
The pairing is the corpus default — when a uv-managed project explicitly names a
backend, hatchling is the overwhelming choice; many samples don't surface the backend
field at all and are placed here as the "uv-managed, hatchling-assumed" baseline.
Pairs with `[project.scripts]` console-script declarations, `requires-python` floors,
src-layout (`src/<package>/`), and often `[dev]` extras for test-only deps. Per-sub-package
uv projects in monorepo layouts. Not all samples committing `uv.lock` appear here —
that orthogonal commit/no-commit choice is its own path.
```

### `Sample > Build and packaging > Optional-dependency fan-out`

**Gap:** The current description gestures at two patterns ("range from a single `[dev]` extra to a domain-driven fan-out") but the cross-corpus evidence shows two genuinely different intents: (a) **dev/test taxonomy** — `[dev]`, `[test]`, `[lint]`, `[typing]` — gating tooling for contributors and CI (datalayer/earthdata, datalayer/jupyter, shibuiwilliam, zongmin-yu); (b) **domain fan-out** — extras shaping the user-facing install footprint when the dependency surface is large or heterogeneous (ClickHouse `[chdb]`, awslabs/openapi `[yaml]/[prometheus]/[all]`, blazickjp `[pdf]`, jlowin per-LLM-vendor, mahdin75 8 geospatial extras + `all`, rohitg00 `[ui]`, openags `httpx[socks]`). Different audiences (contributor vs end-user), different decision criteria, often coexist in the same project — they should be named.

**Sharpened text suggestion:**

```
Python projects expose multiple optional-dependency groups via `[project.optional-dependencies]`.
Two distinct intents the corpus exhibits:

- **Dev/test taxonomy** — `[dev]`, `[test]`, `[lint]`, `[typing]` extras gate tooling
  for contributors and CI (`pip install -e .[dev]`, `uv sync --extra test`). Decouples
  the contributor toolchain from runtime install. Replaces a separate `requirements-dev.txt`.
- **Domain fan-out** — extras shape the end-user install footprint when the dependency
  surface is large or heterogeneous. Patterns include alternative-engine swaps (`[chdb]`
  for an embedded analytics engine, `[yaml]` / `[prometheus]` for capability slices),
  per-LLM-vendor extras (`anthropic`/`azure`/`gemini`/`openai` opt-ins), and per-upstream-library
  extras with an `all` composer (eight geospatial libraries each as their own extra).

Both intents often coexist in the same project. Domain fan-out is appropriate when the
dependency surface is large enough that a one-size install is wasteful; dev taxonomy is
appropriate whenever the project has any non-trivial test or lint setup.
```

### `Sample > Build and packaging > System-level dependencies`

**Gap:** The current description's three-way sub-axis (Self-contained / System binary / Browser runtime) treats "Self-contained" as a sub-pattern of *this path*, but in the corpus, self-containment is the **default** for every Python/Node/Go project — the path name itself ("System-level dependencies") is what makes a sample notable. Calling out marlonluo2018 as "self-contained" is no more meaningful than tagging every npm-installable project. The path should name the *deviation*, not the default.

**Sharpened text suggestion:**

```
Cross-cutting sub-axis — external binaries the host must install before the server can run,
beyond what the language package manager (pip / npm / cargo / go) resolves:

- **System binary required (CLI on PATH)** — Server depends on a host-level binary
  (Tesseract OCR, GDAL, ffmpeg, kubectl/helm/istioctl/argocd, Nmap/Ghidra/Nuclei/SQLMap/Hashcat)
  the package manager cannot install. README surfaces the install responsibility on the user
  (`apt-get install ffmpeg`); Docker becomes the only self-contained distribution path.
  Whole-server categories cluster here (CLI wrappers, security-tool wrappers).
- **Browser runtime (Playwright / Puppeteer)** — Server depends on a browser binary the
  language toolchain fetches as a post-install step (`playwright install`). Multi-GB install
  footprint; container distribution becomes significantly more attractive than bare pip/npm.
  Auto-fetch on first use is sometimes the ergonomic alternative.

Self-contained (registry-only) installation is the corpus default and lives at the
absence of this path — projects that don't require any system binary have no reason to
appear under this section.
```

(Note: the marlonluo2018 placement is flagged separately under Mis-placed samples below.)

### `Sample > Build and packaging > Python version pinning`

**Gap:** The current description's four-mechanism sub-axis is correct and well-evidenced. The cross-corpus view also reveals one rare deviation worth a single-line addition: `samuelgursky--davinci-resolve-mcp` pins an **upper bound** (`Python 3.10–3.12`, 3.13+ explicitly excluded) because of an upstream binary-compat constraint on the DaVinci Resolve scripting module. Every other sample states a *floor* only. Worth naming so the floor-as-posture framing isn't overgeneralized.

**Sharpened text suggestion (one-line append to existing description):**

```
Upper-bounded ranges are rare and almost always driven by an external binary-compat
constraint (e.g., a vendor scripting module ABI), not by project preference — when an
upper bound appears, look for a host-side dependency that won't tolerate newer interpreters.
```

### `Sample > Build and packaging > npm/Node toolchain`

**Gap:** The current description treats npm/Node as a single path. The cross-corpus view reveals a structural sub-axis — pnpm-workspace + Turbo monorepos (cloudflare/mcp-server-cloudflare, getsentry/sentry-mcp, upstash/context7, neondatabase, possibly more) versus single-package Node projects (the majority of supporters). The monorepo cluster pairs with separate roles (Repository layout — monorepo), uses Changesets for coordinated releases, and shares lint/build/format tooling across packages. Worth a sub-axis line so the pattern is named in the description, not only inferable from cross-role inspection.

**Sharpened text suggestion (append to existing description):**

```
Two sub-patterns in the corpus:

- **Single-package npm project** — one `package.json`, build via `tsc`/`tsup`/`esbuild`
  to `build/` or `dist/`, npm publish target. The default and the most common.
- **pnpm workspace + Turbo monorepo** — `pnpm-workspace.yaml` declares packages, Turbo
  orchestrates cross-package builds, Changesets handle coordinated release versioning,
  shared `eslint.config.*` / `prettier.config.*` / `tsconfig.json` at root. Pairs with
  Repository layout's monorepo paths and Wrangler-bundle distribution when the targets
  are Cloudflare Workers.
```

### `Sample > Build and packaging > Go modules (`go.mod` / `go.sum`)`

**Verification of Pass-2 reconciliation addition:** The description explicitly names Go modules as the Go peer of `Cargo (Rust)` and contrasts the version-pinning surface (`go.mod`/`go.sum` vs `pyproject.toml`/`package.json`/`Cargo.toml`). Cross-corpus evidence (mark3labs, metoro-io, viant) all show standard `go.mod` + Go-toolchain resolution; viant adds a bridge-binary built from the same module for non-Go consumers. The path's description is well-positioned and evidence-aligned. **No sharpening needed**; flagged here per the caller's reminder to verify.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### `Sample > Build and packaging > Optional-dependency fan-out` — dev vs domain intent

Sub-pattern: dev/test taxonomy (4 samples) vs domain fan-out (8+ samples). Recommendation: **fold into description** as a two-bullet split (see sharpening above). A bucket split would be premature — same mechanism (`[project.optional-dependencies]`), same file location, projects often combine both.

### `Sample > Build and packaging > npm/Node toolchain` — single vs monorepo

Sub-pattern: single-package npm vs pnpm-workspace + Turbo monorepo (5+ samples). Recommendation: **fold into description** (see sharpening above). Bucket split would duplicate Repository-layout role's monorepo distinction.

### `Sample > Build and packaging > Bare script (no build)` — uv-sync vs installer-script

Sub-pattern: single-file `.py` + `uv sync` against ad-hoc deps (labeveryday) vs no-pyproject + custom `install.py` orchestrator (samuelgursky). Two genuinely distinct mechanisms, but only 1 sample each — too thin to split. Recommendation: **fold one-line nuance** into description noting the two shapes.

### `Sample > Build and packaging > Hatchling + uv (Python)` — explicit-backend vs assumed-backend

Sub-pattern: ~17 samples explicitly confirm `hatchling.build` in pyproject.toml; ~11 only confirm uv as version manager and say "build backend not surfaced." Recommendation: **fold into description** (see sharpening above) so the path's placement criterion is explicit. No split — they're not different choices, just different evidence depth from sample authors.

### `Sample > Build and packaging > Pin discipline (Python)` — pin tightness as posture

Sub-pattern (already in description): exact pin / narrow range / loose `>=`. Confirmed across the corpus. The description already covers this well; cross-corpus view adds no new nuance. **No change.**

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. The path tree under this role separates genuinely distinct choices (build backend, version-manager workflow, lock-file commit, system-binary deviation, language ecosystem). Evidence comparison didn't surface any path-pair where the same choice is described twice under different names.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None proposed. Even the `Optional-dependency fan-out` two-intent pattern doesn't justify a split — the two intents share the same mechanism and often coexist in the same project. A description-level split (the suggested two-bullet sharpening) carries the nuance without introducing a second path that fragments the support count.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

### `marlonluo2018--pandas-mcp-server.md` currently under `System-level dependencies`

**Evidence:** The sample's content under this path reads: "Self-contained (registry-only) — pure Python ecosystem; pandas, fastmcp, chardet, psutil all install via pip." This is the *absence* of system-level dependencies — the corpus default — not an instance of the path. Under the sharpened description (which removes "Self-contained" as a sub-axis since it's the default), this sample no longer has a placement reason here. Recommendation: **remove from this path.** The sample's other build/packaging facts (loose `fastmcp >= 1.0.0` pin, pytest-as-runtime-dep oversight) are already captured under `Pin discipline (Python)` — no information loss from removing.

### `echelon-ai-labs--servicenow-mcp.md` currently under `Pin discipline (Python)`

**Evidence:** The sample's content under this path reads: "Specific build backend not captured. Version manager convention: pip (`pip install -e .`)." This is generic build/package-manager content — not pin discipline. The sample says nothing about pin tightness, exact pins, ranges, or floor strategy. Recommendation: **remove from this path.** If the sample exhibits no pin discipline observation, it shouldn't be placed here. The package-manager fact may belong under `Hatchling + uv (Python)` or a different path depending on the broader sample, but reconciler should verify rather than assume.

### `mukul975--cve-mcp-server.md` currently under `Pin discipline (Python)`

**Evidence:** The sample's content under this path reads: "`pyproject.toml` based packaging; pip/uv compatible." Same issue as echelon-ai-labs — generic packaging content with no pin-tightness or version-strategy observation. Recommendation: **remove from this path.** Reconciler should verify whether the sample belongs under a generic `Hatchling + uv (Python)` placement instead.

### `JackKuo666--PubMed-MCP-Server.md` currently in both `No lock file` and `Requirements-driven (legacy Python)`

**Evidence:** The "No lock file" content says "Lock file absent — `requirements.txt` plays the pin role." The "Requirements-driven" content says "`requirements.txt` is the install contract; `pyproject.toml` also present." The two facts are the same observation phrased two ways. The "No lock file" path with only this one sample is functionally redundant with `Requirements-driven (legacy Python)` for this sample's case (and the only other case in the corpus that would qualify, `hannesrudolph`, is also already in `Requirements-driven`). Recommendation for the reconciler: **either remove JackKuo666 from `No lock file`** (keeping the path alive for some hypothetical future case where a project has `pyproject.toml` with no lock and no requirements.txt — currently zero such samples), **or remove the `No lock file` path entirely** and fold its description into `Requirements-driven (legacy Python)`. Borderline judgment call — the path may stay alive as a documented possibility even with thin support, but the double-placement should be resolved.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Three orthogonal axes are bundled under "Build and packaging" but vary independently

The role's intro names "build backend, lockfile, dependency-pinning approach, and version-manager conventions" — and indeed the supporting paths span four orthogonal dimensions:

1. **Build backend** — hatchling / setuptools / poetry / uv_build / Cargo / Go-toolchain / Maven-Gradle / Wrangler / CMake / no-backend
2. **Version manager / install workflow** — uv / pip / poetry / pnpm / npm / cargo / go-toolchain / maven-gradle / wrangler
3. **Lock-file commit choice** — `uv.lock` committed / `requirements.lock` committed / no lock
4. **Dependency-pinning tightness** — exact / narrow range / loose `>=`

The current path tree mixes axes (e.g., "Hatchling + uv" pairs axes 1+2; `uv.lock` committed is axis 3 alone; `Pin discipline` is axis 4 alone; `No lock file` is axis 3 alone). This is fine for a per-path qualitative tree but means a single sample can legitimately appear under 3-4 paths. The reconciler should not interpret this as redundancy — it's the role's natural multi-axis nature, not a sign of bucket overlap. Worth noting in the role-level intro so a future reader doesn't try to "clean up" by collapsing axis-distinct paths.

### Python is over-represented in path count vs. sample distribution

11 of 20 paths are Python-specific (Hatchling+uv, Python version pinning, Pin discipline, uv.lock, Optional-dep fan-out, Requirements-driven, Setuptools, uv_build, Hatch force-include, No lock file, Poetry, requirements.lock = 12 actually). Only 4 are non-Python ecosystem-specific (npm/Node, Cargo, Go modules, Maven/Gradle, Wrangler = 5). System-level dependencies and Bare script are cross-language. The Python path count reflects depth of Python evidence — not necessarily that Python's build space is more complex than Node's, just that the corpus has 60+ Python servers and ~20 Node servers. The path tree is honest about evidence; quantification surfaces the asymmetry.

### Build-system substrate ↔ Repository layout is the strongest cross-role coupling under this role

The description for `Hatch force-include for monorepo wheel` already explicitly links to `Repository layout — Monorepo with per-server subdirectories and one PyPI package`. The pnpm-workspace+Turbo cluster under `npm/Node toolchain` similarly links to Repository-layout monorepo paths. `awslabs--mcp` (per-server pyproject.toml) shows the Python equivalent — many small uv projects under one repo. These coupling threads are best surfaced by Repository-layout-side cross-references rather than re-listed here, but the depth pass confirms the coupling is real and structural, not incidental.

### "Build backend not surfaced" is itself an observation

A nontrivial fraction (~25%) of Python samples under `Hatchling + uv (Python)` say "build backend not surfaced" or equivalent. This is partly an artifact of the original sample-collection methodology (some agents extracted backend, some didn't), and partly a corpus reality (some projects lack `[build-system]` declaration at all and rely on default behavior). The cross-corpus view shows this consistently enough that the consolidated description should acknowledge the assumed-backend placement criterion (see sharpening above) rather than implying every supporting sample has a confirmed `hatchling.build` declaration.
