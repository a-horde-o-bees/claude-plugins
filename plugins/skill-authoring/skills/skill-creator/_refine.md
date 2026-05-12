# Refine

> Workflow component for the `refine` verb of skill-creator. Owns iteration on an in-progress skill toward finalization.

### Variables

- {name} — skill name to refine
- {destination} — where the skill lives (defaults to `plugins/skill-authoring/skills/` if {name} resolves there; otherwise probe user/project)

### Rules

- Live-edit model — composition.md (if present) tracks intent; SKILL.md + components are the live implementation, edited in place
- Terminal phases (description optimization + packaging) fire only on explicit user signal — not eager
- Test runs are agent-spawning where possible (with-skill vs baseline) to surface trigger and output gaps the agent's own eyes miss

### Process

1. Resolve `{skill-folder}` = `{destination}/{name}/`. If not present: Exit to user: skill `{name}` not found at `{destination}` — run `new {name}` first or correct the destination.

2. Read the skill's SKILL.md + each `_<verb>.md` component to load current state.

3. Read evals/evals.json if present. If not present: prompt user whether to add test cases now; if yes, scaffold 2–3 prompts.

4. Run test cases — for each eval prompt:
    1. Spawn an agent with the skill loaded; record outputs to `evals-workspace/iteration-<N>/eval-<id>/with_skill/outputs/`.
    2. Spawn a baseline agent without the skill; record outputs to `evals-workspace/iteration-<N>/eval-<id>/without_skill/outputs/`.
    3. Capture timing (total_tokens, duration_ms) to `timing.json` per run.

5. While runs are in progress, draft quantitative assertions if not already present in evals.json. Reference the embedded schema: `sources/anthropics-skills--skill-creator/references/schemas.md`.

6. As runs complete, grade assertions per the embedded grader prompt: `sources/anthropics-skills--skill-creator/agents/grader.md`. Save results to `grading.json` per run directory.

7. Aggregate benchmark — bash: `uv run --directory sources/anthropics-skills--skill-creator -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name {name}`. Produces `benchmark.json` and `benchmark.md`.

8. Launch the eval viewer:
    - bash: `nohup python sources/anthropics-skills--skill-creator/eval-viewer/generate_review.py <workspace>/iteration-N --skill-name {name} --benchmark <workspace>/iteration-N/benchmark.json > /dev/null 2>&1 &`
    - Tell the user: "Outputs are open in your browser — Outputs tab for per-eval feedback, Benchmark tab for quantitative comparison. Come back here when you're done."

9. Wait for user feedback. When they say done: read `feedback.json` from the workspace.

10. Apply revisions to the live skill — for each feedback item:
    1. Identify which file(s) to revise (SKILL.md frontmatter / body, a `_<verb>.md` component, an embedded script).
    2. Edit live via Edit/Write tools.

11. Ask the user if they want another iteration loop (back to step 4) or to declare the skill done.

12. If user signals done:
    1. Run description optimization — generate 20 trigger-eval queries (8–10 should-trigger, 8–10 should-not-trigger, focus on near-misses), review with user via the embedded HTML template, then bash: `uv run --directory sources/anthropics-skills--skill-creator -m scripts.run_loop --eval-set <trigger-evals.json> --skill-path {skill-folder} --model <current-model-id> --max-iterations 5 --verbose`. Apply the `best_description` from the JSON output.
    2. Package — bash: `uv run --directory sources/anthropics-skills--skill-creator -m scripts.package_skill {skill-folder}`. Hand over the resulting `.skill` file path.

13. Return to caller:
    - Skill refined: {skill-folder}
    - Iterations run: count
    - Final description (post-optimization, if run)
    - Packaged at: path to `.skill` file (if packaged)
