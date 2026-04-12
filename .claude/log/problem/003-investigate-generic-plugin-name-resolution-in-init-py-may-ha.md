---
created: 2026-04-11T23:49:02.529468+00:00
---

# Investigate generic plugin name resolution in _init.py — may have same marketplace path bug as convention_gate had

`skills/navigator/_init.py` uses `plugin.get_plugin_name(plugin_root)` to derive the plugin name from `plugin.json` and builds db paths as `.claude/{plugin_name}/navigator/navigator.db`. This works but is the same generic pattern that broke in `convention_gate.py` when `CLAUDE_PLUGIN_ROOT` pointed to a marketplace cache path (`...cache/a-horde-o-bees/ocd/0.0.166`).

The convention_gate fix was to hardcode "ocd" since the plugin knows its own name. The `_init.py` module uses `plugin.get_plugin_name()` which reads from `plugin.json` — this works correctly but is still unnecessary indirection for a plugin that knows its own identity.

Question: should `_init.py` (and any other code using this pattern) be simplified to hardcode "ocd", or does the `get_plugin_name` approach work reliably enough via plugin.json? The `_init.py` path is called during `/ocd-init` which runs with proper env vars, so it may not have the same failure mode — but worth verifying.
