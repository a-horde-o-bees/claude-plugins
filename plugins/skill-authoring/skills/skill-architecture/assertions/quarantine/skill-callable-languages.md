# Cost/benefit: languages for skill callables

> Quarantined draft — captured while building `git-roots.sh`. Elevate to a real
> architecture recommendation (probe-backed) when we get to it. Two candidates for now.

A "skill callable" is a mechanical script a skill ships and invokes directly (not a
skill-to-skill call) to do work that would otherwise burn agent context — enumerate
roots, parse a stream, count things. The canonical example is `runner.py`; the newest
is `git-roots.sh`. The language choice trades portability, startup cost, dependency
surface, and how cleanly it returns structured data.

## POSIX `sh`

**Benefits**
- **Zero dependencies** — runs wherever a POSIX shell + the wrapped tool exist.
- **No interpreter startup** — cheapest possible per-call cost; matters when a gate
  fires on every commit.
- **System-agnostic if disciplined** — `#!/usr/bin/env sh`, no bashisms (no `mapfile`,
  `declare -A`, `[[`, `${v,,}`). Then it runs on stock **macOS bash 3.2**, Linux, WSL,
  and **git-bash** on Windows. Plain `bash` is *not* agnostic — macOS ships the 2007
  3.2; bash-4+ features break there.
- Best fit for thin wrappers over a CLI (git, grep) where the logic *is* shell.

**Costs**
- **No structured output** — emitting/parsing JSON is painful; you fall back to
  line-oriented text and `awk`/`cut`. Fine for "one path per line," bad for nested data.
- **Quoting/word-splitting hazards** — spaces in paths, `set -eu` discipline, portable
  `wc | tr -d` idioms. Easy to write subtly non-portable or unsafe.
- **No real data structures / tests** — logic past ~50 lines gets unmaintainable.

## Python (via `uv run --script`, PEP 723)

**Benefits**
- **Structured data for free** — JSON in/out, dicts, real parsing; the natural choice
  when the callable returns a record, not a list of strings (e.g. `runner.py`'s probe
  signals).
- **Maintainable at size** — functions, types, unit tests, stdlib (`pathlib`, `json`,
  `subprocess`); scales past where shell collapses.
- **Portable interpreter via uv** — `uv` resolves/pins Python, so "works on my machine"
  risk drops *if uv is installed*.

**Costs**
- **Dependency on uv/Python** — the consumer's environment must have it; not guaranteed
  the way a POSIX shell is.
- **Startup cost** — `uv run` resolves and launches an interpreter every call; non-trivial
  if invoked in a tight loop or as a per-action gate.
- **Overkill for CLI wrangling** — wrapping `git` in Python is more ceremony than a
  three-line shell pipe.

## Provisional rule of thumb

- **Thin wrapper over a CLI, line-oriented output, called often** → POSIX `sh`
  (`git-roots.sh`).
- **Parses/produces structured data, non-trivial logic, wants tests** → Python+uv
  (`runner.py`).

The deciding axis is usually **output shape** (lines vs. records) and **call frequency**
(gate-on-every-action favors zero startup). To verify before elevating: measure `uv run`
startup cost and confirm the macOS-bash-3.2 portability claim on a real 3.2.
