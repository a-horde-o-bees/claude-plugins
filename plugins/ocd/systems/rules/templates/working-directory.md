---
tagline: Stay in project root; use absolute paths instead of cd/pushd/popd
---

# Working Directory

Working directory must remain project root for the entire session. Use absolute paths or tool flags instead of changing directories.

- No `cd`, `pushd`, `popd` — use `git -C <path>` for submodule operations
