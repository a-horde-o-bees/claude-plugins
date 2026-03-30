"""Condition operator tests — Django __operator syntax on read_records."""

import json


def parse(result: str):
    return json.loads(result)


class TestConditionOperators:
    """Test all Django __operator conditions."""

    def _seed_entities(self, db):
        for i, (name, rel) in enumerate([
            ("Rel 9", 9), ("Rel 7", 7), ("Rel 5", 5), ("Rel 3", 3), ("Rel 0", 0),
        ], 1):
            db["create"]("entities", {"name": name, "url": f"https://e{i}.com", "relevance": rel})

    def test_equality(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"relevance": 7}))
        assert len(result) == 1
        assert result[0]["name"] == "Rel 7"

    def test_gte(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"relevance__gte": 7}))
        assert len(result) == 2

    def test_gt(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"relevance__gt": 7}))
        assert len(result) == 1

    def test_lte(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"relevance__lte": 3}))
        assert len(result) == 2

    def test_lt(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"relevance__lt": 3}))
        assert len(result) == 1

    def test_ne(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"relevance__ne": 0}))
        assert len(result) == 4

    def test_like(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"name__like": "Rel 9%"}))
        assert len(result) == 1

    def test_null_true(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"last_modified__null": True}))
        assert isinstance(result, list)

    def test_null_false(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"last_modified__null": False}))
        assert isinstance(result, list)

    def test_combined_conditions(self, db):
        self._seed_entities(db)
        result = parse(db["read"]("entities", {"relevance__gte": 5, "relevance__lte": 7}))
        assert len(result) == 2
        assert all(5 <= e["relevance"] <= 7 for e in result)
