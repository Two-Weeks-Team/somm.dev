from app.graph.state import merge_dicts


def test_merge_dicts_combines_entries():
    left = {"a": 1}
    right = {"b": 2}
    assert merge_dicts(left, right) == {"a": 1, "b": 2}


def test_merge_dicts_overwrites_on_conflict():
    left = {"a": 1}
    right = {"a": 2}
    assert merge_dicts(left, right) == {"a": 2}


def test_merge_dicts_handles_missing_values():
    assert merge_dicts(None, None) == {}
    assert merge_dicts({"a": 1}, None) == {"a": 1}
    assert merge_dicts(None, {"b": 2}) == {"b": 2}
