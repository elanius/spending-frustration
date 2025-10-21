"""Rule engine for string-based user rules stored in a single document.

Collection: ``user_rules``
Document shape:
    { "user_id": <ObjectId>, "rules": [ {"rule": "merchant contains Coffee -> @coffee #caffeinated", "name": "Coffee", "active": true }, ... ] }
"""

from bson import ObjectId

from app.models import Transaction, UserRules
from app.db import user_rules_collection
from app.rules.rule import Rule
from app.rules.parser import parse_rule


class RuleEngine:
    def __init__(self, user_id: ObjectId):
        self._user_id = user_id
        self._rules: list[Rule] = self._load_rules()

    def _load_rules(self) -> list[Rule]:
        doc = user_rules_collection.find_one({"user_id": self._user_id})
        if not doc:
            return []

        user_rules = UserRules.model_validate(doc)
        rules = [parse_rule(r.rule) for r in user_rules.rules if r.active]
        return rules

    def apply_rules(self, transactions: list[Transaction]) -> list[Transaction]:
        for transaction in transactions:
            for rule in self._rules:
                rule.evaluate(transaction)

        return transactions
