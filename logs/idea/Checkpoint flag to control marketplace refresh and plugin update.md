---
log-role: queue
---

# Checkpoint flag to control marketplace refresh and plugin update

The `/checkpoint` skill (when on main) runs marketplace refresh + plugin update + recommends a session restart as its trailing steps. These are useful when the commit's purpose is to ship plugin changes downstream — they propagate the new code into the user's next session's cache.

For commits that don't touch plugin code (docs, project-root edits, plan updates), the marketplace refresh + plugin update steps cost time and produce a stale "Restart to apply changes" message even when nothing actually needs reloading.

Idea: surface a flag (or auto-detect) to control whether the checkpoint includes these steps. Candidates:

- `--no-update` to skip refresh + plugin update + restart recommendation.
- Auto-detect based on the diff: if the commit touched anything under `plugins/<name>/`, run the update flow; otherwise skip.
- Always-skip by default; require `--update` for the propagation steps. Inverts the current default (consumers explicitly opt in to the propagation overhead).

Auto-detect is the most ergonomic but requires inspecting the just-pushed diff. Flag-based is simpler.

User surfaced this when noting that the unexpected `/ocd:git release` invocation (mid-session) was a separate concern from `/checkpoint`'s natural propagation steps — but the broader question of whether `/checkpoint` should always trigger marketplace + plugin update remains open.
