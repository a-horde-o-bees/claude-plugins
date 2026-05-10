"""composition.md schema tests — parse, serialize, scaffold, mutate."""

import pytest

from scripts._spec import (
    BUILD_STATUS_DRAFT,
    Source,
    add_source_to_spec,
    make_composed_scaffold,
    parse,
    remove_source_from_spec,
    serialize,
)


def _example_source(commit="a" * 40):
    return Source(
        url="https://github.com/anthropics/skills.git",
        skill="slack-formatting",
        ref="main",
        commit=commit,
    )


def test_make_composed_scaffold_defaults():
    spec = make_composed_scaffold("my-skill", "user", description="my desc")
    assert spec.scope == "user"
    assert spec.description == "my desc"
    assert spec.sources == []
    assert spec.build_status == BUILD_STATUS_DRAFT
    assert "# Goal" in spec.body


def test_make_composed_scaffold_rejects_unknown_scope():
    with pytest.raises(ValueError, match="unknown scope"):
        make_composed_scaffold("my-skill", "global")


def test_serialize_then_parse_roundtrips():
    spec = make_composed_scaffold("rt-skill", "user", description="round trip")
    add_source_to_spec(spec, _example_source(commit="b" * 40))
    text = serialize(spec)
    parsed = parse(text)
    assert parsed.name == "rt-skill"
    assert parsed.scope == "user"
    assert parsed.description == "round trip"
    assert len(parsed.sources) == 1
    assert parsed.sources[0].commit == "b" * 40
    assert parsed.build_status == BUILD_STATUS_DRAFT


def test_add_source_appends_new():
    spec = make_composed_scaffold("my-skill", "user")
    add_source_to_spec(spec, _example_source())
    assert len(spec.sources) == 1


def test_add_source_replaces_existing_url_skill_pair():
    spec = make_composed_scaffold("my-skill", "user")
    add_source_to_spec(spec, _example_source(commit="old"))
    add_source_to_spec(spec, _example_source(commit="new"))
    assert len(spec.sources) == 1
    assert spec.sources[0].commit == "new"


def test_remove_source_removes_match():
    spec = make_composed_scaffold("my-skill", "user")
    add_source_to_spec(spec, _example_source())
    remove_source_from_spec(
        spec,
        "https://github.com/anthropics/skills.git",
        "slack-formatting",
    )
    assert spec.sources == []


def test_remove_source_silent_on_missing():
    spec = make_composed_scaffold("my-skill", "user")
    remove_source_from_spec(spec, "https://example.com", "no-such-skill")
    assert spec.sources == []


def test_parse_rejects_missing_frontmatter_delimiter():
    with pytest.raises(ValueError, match="frontmatter"):
        parse("no frontmatter here\n")


def test_parse_rejects_missing_required_fields():
    with pytest.raises(ValueError, match="must include"):
        parse("---\nspec_version: 1\n---\n\nbody\n")


def test_serialize_emits_empty_sources_inline():
    spec = make_composed_scaffold("my-skill", "user")
    text = serialize(spec)
    assert "sources: []" in text


def test_serialize_emits_block_list_for_populated_sources():
    spec = make_composed_scaffold("my-skill", "user")
    add_source_to_spec(spec, _example_source())
    text = serialize(spec)
    assert "sources:" in text
    assert "- url:" in text
    assert "  skill:" in text
    assert "  ref:" in text
    assert "  commit:" in text
