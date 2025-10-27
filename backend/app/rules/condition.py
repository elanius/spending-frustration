from app.models import Transaction


class Condition:
    def __init__(self, field: str, operator: str, value: str | float | int):
        self._field = field
        self._operator = operator
        self._value = value

    @property
    def field(self) -> str:
        return self._field

    @property
    def operator(self) -> str:
        return self._operator

    @property
    def value(self) -> str | float | int:
        return self._value

    def _field_value(self, transaction: Transaction):
        if hasattr(transaction, self._field):
            return getattr(transaction, self._field, None)
        else:
            raise ValueError(f"Unsupported field: {self._field}")

    def evaluate(self, transaction: Transaction) -> bool:
        field_value = self._field_value(transaction)
        if field_value is None:
            return False
        if self._operator == "==":
            return field_value == self._value
        if self._operator == "contains":
            return isinstance(field_value, str) and self._value in field_value
        if self._operator == ">":
            return isinstance(field_value, (int, float)) and field_value > self._value
        if self._operator == ">=":
            return isinstance(field_value, (int, float)) and field_value >= self._value
        if self._operator == "<":
            return isinstance(field_value, (int, float)) and field_value < self._value
        if self._operator == "<=":
            return isinstance(field_value, (int, float)) and field_value <= self._value
        return False

    def to_mongo_query(self) -> dict:
        operator_map = {
            "==": "$eq",
            "contains": "$regex",
            ">": "$gt",
            ">=": "$gte",
            "<": "$lt",
            "<=": "$lte",
        }
        if self._operator not in operator_map:
            raise ValueError(f"Unsupported operator: {self._operator}")

        mongo_operator = operator_map[self._operator]
        return {self._field: {mongo_operator: self._value}}
