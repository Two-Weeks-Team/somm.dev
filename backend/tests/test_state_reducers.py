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


def test_merge_dicts_with_nested_token_usage():
    current = {"marcel": {"input_tokens": 100, "output_tokens": 50}}
    incoming = {"isabella": {"input_tokens": 200, "output_tokens": 100}}
    result = merge_dicts(current, incoming)
    assert result == {
        "marcel": {"input_tokens": 100, "output_tokens": 50},
        "isabella": {"input_tokens": 200, "output_tokens": 100},
    }


def test_merge_dicts_handles_none_token_metadata():
    current = {"marcel": {"input_tokens": None, "output_tokens": None}}
    incoming = {"isabella": {"input_tokens": 100, "output_tokens": 50}}
    result = merge_dicts(current, incoming)
    assert "marcel" in result
    assert "isabella" in result
