import re
from typing import Any, Iterable

from app.rules.filter import Filter
from app.rules.rule import Rule
from app.rules.action import Action

from .condition import Condition


def _tokenize(expression_text: str) -> tuple[list[str], str]:
    parts = re.split(r"\s+(AND|OR)\s+", expression_text.strip(), flags=re.IGNORECASE)
    if len(parts) == 1:
        return [parts[0].strip()], "AND"
    condition_tokens: list[str] = []
    logical_operators: list[str] = []

    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            if part.strip():
                condition_tokens.append(part.strip())
        else:
            logical_operators.append(part.upper())

    if not logical_operators:
        return condition_tokens, "AND"

    first = logical_operators[0]
    if any(op != first for op in logical_operators):
        raise ValueError("Mixed logical operators not supported")

    return condition_tokens, first


def _parse_condition(line: str) -> Condition:
    operator_pattern = r"(==|contains|>=|<=|>|<)"
    match = re.search(operator_pattern, line)
    if not match:
        raise ValueError(f"No operator found in condition: '{line}'")
    operator = match.group(1)
    left, right = line.split(operator, 1)
    field_name = left.strip()
    raw_value = right.strip()

    # strip quotes
    if (raw_value.startswith('"') and raw_value.endswith('"')) or (
        raw_value.startswith("'") and raw_value.endswith("'")
    ):
        value: Any = raw_value[1:-1]
    else:
        try:
            value = float(raw_value) if "." in raw_value else int(raw_value)
        except ValueError:
            value = raw_value

    return Condition(field=field_name, operator=operator, value=value)


def parse_filter(line: str) -> Filter:
    filter_part = line.strip()
    cond_strings, logical_op = _tokenize(filter_part)
    conditions: list[Condition] = []
    for cs in cond_strings:
        conditions.append(_parse_condition(cs))

    return Filter(conditions=conditions, logical_operator=logical_op)


def parse_action(text: str) -> Action:
    tokens = [t.strip() for t in re.split(r"[\s,]+", text.strip()) if t.strip()]
    category: str | None = None
    tags: list[str] = []
    for token in tokens:
        if token.startswith("@"):
            if category is not None:
                raise ValueError("Multiple categories specified")
            category = token[1:]
            if not category:
                raise ValueError("Empty category token '@'")
        elif token.startswith("#"):
            tag = token[1:]
            if not tag:
                raise ValueError("Empty tag token '#'")
            if tag not in tags:
                tags.append(tag)
        else:
            raise ValueError(f"Unexpected action token '{token}' (expected @category or #tag)")
    return Action(category=category, tags=tags)


def parse_rule(rule_text: str) -> Rule:
    if "->" not in rule_text:
        raise ValueError("Rule must contain '->' separating filter and action")

    left, right = re.split(r"->", rule_text, maxsplit=1)
    filter_part = left.strip()
    action_part = right.strip()
    if not filter_part:
        raise ValueError("Filter part is empty")
    if not action_part:
        raise ValueError("Action part is empty")

    filter_obj = parse_filter(filter_part)
    action_obj = parse_action(action_part)

    return Rule(filter=filter_obj, action=action_obj, raw_rule=rule_text)


def parse_rule_lines(lines: Iterable[str]) -> list[Rule]:
    rules: list[Rule] = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rules.append(parse_rule(line))

    return rules
