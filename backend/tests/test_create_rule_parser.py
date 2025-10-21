from app.rules.filter import Filter, FilterParseError
from app.rules.parser import parse_rule


def test_parse_single_condition_numeric():
    parsed = parse_rule("amount > 100 -> #big")
    flt = parsed.filter
    assert flt.logical_operator == "AND"
    assert len(flt.conditions) == 1
    condition = flt.conditions[0]
    assert condition.field == "amount"
    assert condition.operator == ">"
    assert condition.value == 100
    assert parsed.action.category is None
    assert parsed.action.tags == ["big"]


def test_parse_and_conditions_with_category_and_tags():
    line = "merchant contains Lidl AND amount >= 10 -> @groceries #food #essentials"
    parsed = parse_rule(line)
    flt = parsed.filter
    assert flt.logical_operator == "AND"
    assert len(flt.conditions) == 2
    assert parsed.action.category == "groceries"
    assert set(parsed.action.tags) == {"food", "essentials"}
    fields = {c.field for c in flt.conditions}
    assert fields == {"merchant", "amount"}


def test_parse_or_conditions():
    line = "merchant contains Lidl OR merchant contains Kaufland -> @groceries"
    parsed = parse_rule(line)
    flt = parsed.filter
    assert flt.logical_operator == "OR"
    assert len(flt.conditions) == 2
    assert parsed.action.category == "groceries"
    assert parsed.action.tags == []


def test_parse_multiple_lines():
    lines = [
        "amount > 100 -> #big",
        "amount > 200 -> #bigger",
    ]
    parsed = [parse_rule(line) for line in lines]
    assert len(parsed) == 2


def test_mixed_logical_operators_error():
    line = "amount > 10 AND merchant contains Lidl OR merchant contains Kaufland -> #x"
    try:
        parse_rule(line)
    except FilterParseError as e:
        assert "Mixed logical operators" in str(e)
    else:
        raise AssertionError("Expected FilterParseError for mixed logical operators")


# ---------------- Additional syntax / validation error cases ---------------- #


def assert_parse_error(line: str, contains: str, use_rule: bool = True):
    try:
        if use_rule:
            parse_rule(line)
        else:
            Filter.parse(line)
    except FilterParseError as e:
        assert contains in str(e), f"Expected '{contains}' in error, got: {e}"  # noqa: E501
    else:
        raise AssertionError(f"Expected FilterParseError for line: {line}")


def test_error_missing_arrow():
    # This is a rule (should have ->) so rule parser complains.
    assert_parse_error("amount > 10 #tag", "must contain '->'")


def test_error_empty_expression():
    assert_parse_error("   -> @cat", "Empty filter")


def test_error_empty_result():
    assert_parse_error("amount > 5 ->   ", "Empty action")


def test_error_unknown_field():
    assert_parse_error("merchantX > 5 -> #tag", "Unknown field")


def test_error_no_operator():
    assert_parse_error("amount 50 -> #tag", "No operator found")


def test_error_multiple_categories():
    assert_parse_error("amount > 10 -> @food @extra", "Multiple categories")


def test_error_empty_category_token():
    assert_parse_error("amount > 10 -> @ #food", "Empty category token")


def test_error_empty_tag_token():
    assert_parse_error("amount > 10 -> #", "Empty tag token")


def test_error_unexpected_token():
    assert_parse_error("amount > 10 -> food", "Unexpected action token")
