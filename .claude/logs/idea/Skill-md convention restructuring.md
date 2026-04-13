# Skill-md Convention Restructuring

Three areas of skill-md.md that need revisiting as file compartmentalization matures.

## --auto and --delegate

The --auto convergence loop and --delegate backgrounding sections are older design. They prescribe agent spawning patterns, iteration limits, and composition rules inline in skill-md.md. With the compartmentalization model (each execution context gets exactly its own instructions), these dispatch patterns may be better expressed as reusable component files or extracted into their own convention rather than embedded in the base skill convention. The current inline guidance also conflicts with newer patterns — evaluate-skill's concurrent dispatch structure doesn't fit the --auto sequential iteration model.

Sections to extract: Standard Arguments (--auto, --delegate, Agent Spawn Requirement), including the convergence loop PFN block and requirements lists.

## Multi-Path Workflows

Multi-path workflows prescribe separate `## Workflow: Name` sections with routing logic in Route. File compartmentalization achieves the same goal more cleanly — each workflow path lives in its own component file, the Route dispatches to the right file, and the executor reads only its path. The multi-path section may be replaceable with guidance on extracting workflow variants into component files.

## Error Handling defaults

Error Handling is listed as Prescribed in the Body Structure table but has no dedicated section describing the default pattern. The table says "minimum: report failure with available details" but doesn't show what that looks like in practice or provide a template. Other Prescribed sections (Route, Workflow) have detailed guidance. Error Handling should too.
