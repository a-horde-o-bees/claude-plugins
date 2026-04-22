# Per-plugin permission contribution

## Purpose

Each plugin that ships a CLI runner (e.g. `ocd-run`, a hypothetical `blueprint-run`) should own a permissions template that its own init deploys. Today only ocd has a runner, and ocd's permissions system is coupled to ocd's template at `plugins/ocd/systems/permissions/settings.json`. Blueprint and future plugins have no mechanism to contribute their own patterns.

## Alignment with System Dormancy

The per-plugin model matches the dormancy discipline documented in project `ARCHITECTURE.md`: a plugin's influence on the agent (rules, tools, permission contributions) reaches the user only when that plugin has been deployed. A cross-plugin permission contribution would be absent until the plugin's init runs.

## Design shapes to consider

- **Per-plugin template, per-plugin deploy.** Each plugin has its own `systems/permissions/settings.json` and its own init flow writes to the chosen scope. OCD's permissions machinery stays plugin-local; blueprint clones the pattern when it needs to.
- **Aggregation in ocd's permissions system.** OCD discovers templates across enabled plugins and merges categories when deploying. One deploy flow but couples ocd's infrastructure to foreign plugin layout.

First shape fits dormancy better. Defers a decision until blueprint (or another plugin) actually introduces a runner.

## Prompt

Triggered from the dormancy-validation sandbox run: `Bash(ocd-run:*)` was missing from user settings.json and the ocd permissions template, causing subprocess skill invocations to hit permission prompts.
