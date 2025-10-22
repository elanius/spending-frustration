import logging
from app.models import Transaction
from app.db import db
from app.rules.rule import Rule
from app.rules.parser import parse_rule

logger = logging.getLogger(__name__)


class RuleEngine:
    def __init__(self, user_id: str):
        self._user_id = user_id  # stored as string externally
        self._rules: list[Rule] = self._load_rules()

    def _load_rules(self) -> list[Rule]:
        docs = db.get_rules(self._user_id)
        if not docs:
            return []

        rules = [parse_rule(r.rule) for r in docs if r.active]
        return rules

    def apply_rules(self, transactions: list[Transaction]) -> list[Transaction]:
        modified_transactions = []
        for transaction in transactions:
            for rule in self._rules:
                if rule.evaluate(transaction):
                    modified_transactions.append(transaction)

        return modified_transactions
