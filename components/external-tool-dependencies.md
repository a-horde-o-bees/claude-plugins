# External tool dependencies

Tools installed globally on the user's system (npm globals, system packages, standalone binaries) cannot be auto-installed by plugins — they require user action. Skills that depend on these tools check availability at runtime in their Route and provide corrective install guidance:

```
1. Verify tool available — bash: `command -v <tool>`
    1. If not found: Exit to user — `<tool>` is required; install with `<install command>`
```

Use `SessionStart` hooks for Python packages (isolated in plugin venv). Use runtime checks in skills for everything else.
