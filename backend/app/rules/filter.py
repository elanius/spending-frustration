from .condition import Condition
from app.models import Transaction

ALLOWED_FIELDS = {"merchant", "amount", "notes", "category", "tags"}
ALLOWED_OPERATORS = {"==", "contains", ">", ">=", "<", "<="}


LOGICAL_TOKENS = {"AND", "OR"}


class Filter:
    def __init__(self, conditions: list[Condition], logical_operator: str):
        self._conditions = conditions
        self._logical_operator = logical_operator

    @property
    def conditions(self) -> list[Condition]:
        return self._conditions

    @property
    def logical_operator(self) -> str:
        return self._logical_operator

    def matches(self, transaction: Transaction) -> bool:
        if self._logical_operator == "AND":
            return all(condition.evaluate(transaction) for condition in self._conditions)
        if self._logical_operator == "OR":
            return any(condition.evaluate(transaction) for condition in self._conditions)
        raise ValueError(f"Unsupported logical operator: {self._logical_operator}")
