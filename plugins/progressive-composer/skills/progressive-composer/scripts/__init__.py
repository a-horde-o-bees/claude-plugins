"""progressive-composer Python implementation.

Each verb lives in its own module (`track.py`, `install.py`, ...). Shared
helpers carry an underscore prefix (`_paths.py`, `_config.py`,
`_clone.py`) signalling internal-only consumption. All verbs invoke
uniformly via `uv run -m scripts.<verb> <args>` from the skill folder.

Current scripts are stdlib-only — `uv run` invokes the resolved Python
without dependency installation. Future scripts that add third-party
deps declare them via PEP 723 inline directives at the top of the
module; `uv run` resolves and caches them transparently per invocation.
The invocation form does not change as deps come and go.
"""
