"""Contract test for the SANDBOX-TASKS.md template.

The template at `plugins/ocd/systems/sandbox/templates/SANDBOX-TASKS.md`
is the seed `_new.md` and `_pack.md` substitute into every new sandbox.
This test pins its structural contract — heading with `{feature-id}`
placeholder and the four canonical sections (Pointers, Tasks, Open
Questions are required headings; the goal paragraph sits between
heading and Pointers). Any drift fails here so a downstream sandbox
seeded from a regressed template doesn't mis-shape the file.
"""

from __future__ import annotations

from pathlib import Path

import pytest


REQUIRED_SECTION_HEADINGS = ("## Pointers", "## Tasks", "## Open Questions")


@pytest.fixture(scope="module")
def template_path(project_root: Path) -> Path:
    return project_root / "plugins" / "ocd" / "systems" / "sandbox" / "templates" / "SANDBOX-TASKS.md"


class TestTemplateContract:
    def test_template_file_exists(self, template_path: Path) -> None:
        assert template_path.is_file(), (
            f"SANDBOX-TASKS.md template missing at {template_path} — "
            "_new.md and _pack.md depend on it"
        )

    def test_heading_carries_feature_id_placeholder(self, template_path: Path) -> None:
        first_line = template_path.read_text().splitlines()[0]
        assert first_line == "# Sandbox: {feature-id}", (
            f"first line is {first_line!r}; expected exact placeholder form "
            "`# Sandbox: {feature-id}` so workflow substitution finds it"
        )

    def test_required_sections_present(self, template_path: Path) -> None:
        body = template_path.read_text()
        missing = [h for h in REQUIRED_SECTION_HEADINGS if h not in body]
        assert not missing, (
            f"required section headings missing from template: {missing} — "
            "agents reading SANDBOX-TASKS.md expect these"
        )

    def test_tasks_section_seeds_a_checkbox(self, template_path: Path) -> None:
        body = template_path.read_text()
        tasks_idx = body.index("## Tasks")
        next_section_idx = body.index("## Open Questions", tasks_idx)
        tasks_block = body[tasks_idx:next_section_idx]
        assert "- [ ]" in tasks_block, (
            "Tasks section missing GFM checkbox seed; readers won't know the "
            "expected format from the template alone"
        )
