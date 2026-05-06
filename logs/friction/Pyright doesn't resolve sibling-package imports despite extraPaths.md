# Pyright doesn't resolve sibling-package imports despite extraPaths

Pyright reports `Import "<sibling_package>" could not be resolved` (and similarly for relative imports inside the sibling) despite `pyrightconfig.json` having `extraPaths: ["."]`. Runtime imports work fine when the project is invoked with `python -m <one_of_the_packages>` from project root, with both packages on `sys.path`.

## Reproduction

Project layout where two packages live as siblings under project root:

```
project-root/
├── pyrightconfig.json   # {"extraPaths": ["."], ...}
├── package_a/
│   ├── __init__.py
│   └── main.py          # `from package_b import x`
└── package_b/
    ├── __init__.py
    └── _internal.py     # `from ._internal import y` triggers same warning
```

Pyright shows `reportMissingImports` warnings on both the absolute (`from package_b ...`) and relative (`from ._internal ...`) imports.

## Suspected cause

Pyright's path resolution from `extraPaths` may not pick up sibling `__init__.py`-rooted packages when they're at the same level as the parser's invocation point. The Python runtime resolves them via cwd/sys.path; Pyright's static analysis doesn't replicate this.

## Worth investigating

- Explicit `include` directives in `pyrightconfig.json` enumerating the package directories
- Restructuring under a `src/` layout (`src/package_a/`, `src/package_b/`) with `extraPaths: ["src"]`
- A `setup.py` / `pyproject.toml` package declaration that registers both packages

## Impact

Cosmetic — does not block runtime, tests, or behavior. But persistent: every edit re-triggers the warnings, and a new contributor seeing them may assume the imports are broken.

Encountered in: monaco-lock-company--erp-migration project (sibling `data/` and `project/` packages at root).
