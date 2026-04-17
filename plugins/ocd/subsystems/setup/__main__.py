"""Setup CLI — agent-facing entry for plugin infrastructure management.

Thin delegator: the `setup` skill name describes what the user is doing
(setting up the plugin's project-level infrastructure). The framework
that implements init/status/permissions lives at plugin/ (generic,
propagated to every plugin via pre-commit hook). This module routes
`ocd setup ...` through to that framework so the skill surface and the
implementation stay decoupled.
"""

from plugin.__main__ import main


if __name__ == "__main__":
    main()
