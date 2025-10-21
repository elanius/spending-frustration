from app.rules.action import Action
from app.rules.filter import Filter
from app.models import Transaction


class Rule:
    def __init__(self, filter: Filter, action: Action, raw_rule: str):
        self._filter = filter
        self._action = action
        self._raw_rule = raw_rule

    def evaluate(self, transaction: Transaction):
        if self._filter.matches(transaction):
            self._action.apply(transaction)
            return True
        return False

    def __str__(self):
        return self._raw_rule
