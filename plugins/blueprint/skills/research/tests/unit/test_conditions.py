"""Filter and query tests — list_entities filtering by stage, mode, and min_relevance."""

import json


def parse(result: str):
    return json.loads(result)


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestListFiltering:
    """Test list_entities filtering parameters."""

    def _seed_entities(self, db):
        for i, (name, rel) in enumerate([
            ("Rel 9", 9), ("Rel 7", 7), ("Rel 5", 5), ("Rel 3", 3), ("Rel 0", 0),
        ], 1):
            db["register_entity"]({"name": name, "url": f"https://e{i}.com", "relevance": rel})

    def test_list_all(self, db):
        self._seed_entities(db)
        text = result_text(db["list_entities"]())
        assert "Rel 9" in text
        assert "Rel 7" in text
        assert "Rel 5" in text
        assert "Rel 3" in text
        assert "Rel 0" in text

    def test_filter_by_stage(self, db):
        self._seed_entities(db)
        db["set_stage"]("e1", "researched")
        db["set_stage"]("e2", "researched")

        text = result_text(db["list_entities"](stage="researched"))
        assert "Rel 9" in text
        assert "Rel 7" in text
        assert "Rel 5" not in text

        text = result_text(db["list_entities"](stage="new"))
        assert "Rel 5" in text
        assert "Rel 3" in text
        assert "Rel 0" in text
        assert "Rel 9" not in text

    def test_filter_by_min_relevance(self, db):
        self._seed_entities(db)
        text = result_text(db["list_entities"](min_relevance=7))
        assert "Rel 9" in text
        assert "Rel 7" in text
        assert "Rel 5" not in text
        assert "Rel 3" not in text

    def test_filter_by_min_relevance_zero(self, db):
        self._seed_entities(db)
        text = result_text(db["list_entities"](min_relevance=0))
        # All entities have relevance >= 0
        assert "Rel 9" in text
        assert "Rel 0" in text

    def test_filter_by_mode(self, db):
        db["register_entity"]({"name": "Example", "url": "https://ex.com", "relevance": 8, "modes": ["example"]})
        db["register_entity"]({"name": "Context", "url": "https://ctx.com", "relevance": 7, "modes": ["context"]})
        db["register_entity"]({"name": "Directory", "url": "https://dir.com", "relevance": 6, "modes": ["directory"]})

        text = result_text(db["list_entities"](mode="example"))
        assert "Example" in text
        assert "Context" not in text

        text = result_text(db["list_entities"](mode="context"))
        assert "Context" in text
        assert "Example" not in text

    def test_combined_stage_and_min_relevance(self, db):
        self._seed_entities(db)
        db["set_stage"]("e1", "researched")  # rel 9
        db["set_stage"]("e2", "researched")  # rel 7
        db["set_stage"]("e3", "researched")  # rel 5

        text = result_text(db["list_entities"](stage="researched", min_relevance=7))
        assert "Rel 9" in text
        assert "Rel 7" in text
        assert "Rel 5" not in text

    def test_combined_mode_and_stage(self, db):
        db["register_entity"]({"name": "Ex New", "url": "https://en.com", "relevance": 8, "modes": ["example"]})
        db["register_entity"]({"name": "Ex Done", "url": "https://ed.com", "relevance": 7, "modes": ["example"]})
        db["register_entity"]({"name": "Ctx New", "url": "https://cn.com", "relevance": 6, "modes": ["context"]})
        db["set_stage"]("e2", "researched")

        text = result_text(db["list_entities"](mode="example", stage="new"))
        assert "Ex New" in text
        assert "Ex Done" not in text
        assert "Ctx New" not in text

    def test_no_results(self, db):
        self._seed_entities(db)
        text = result_text(db["list_entities"](stage="researched"))
        assert "No entities found" in text

    def test_rejected_stage_filter(self, db):
        self._seed_entities(db)
        db["reject_entity"]("e5", "irrelevant")

        text = result_text(db["list_entities"](stage="rejected"))
        assert "Rel 0" in text
