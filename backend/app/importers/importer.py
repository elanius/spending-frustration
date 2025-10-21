from pathlib import Path
from bson import ObjectId
from app.importers import mbank
from app.models import Transaction
from app.rules.rule_engine import RuleEngine
from app.db import transactions_collection


class Importer:
    def __init__(self, user_id: ObjectId):
        self._user_id = user_id

    def import_from_file(self, file_path: Path) -> int:
        try:
            with open(file_path, "r") as file:
                data = file.read()
                return self.import_from_data(data)
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
            return 0

    def import_from_data(self, data: str) -> int:
        transactions = self.parse_data(data)
        if transactions:
            rule_engine = RuleEngine(user_id=self._user_id)
            rule_engine.apply_rules(transactions)
            db_result = transactions_collection.insert_many(tx.model_dump(exclude_none=True) for tx in transactions)

            return len(db_result.inserted_ids)

        print("No valid transactions found.")
        return 0

    def parse_data(self, data: str) -> list[Transaction]:
        if mbank.match(data):
            return mbank.parse(data, self._user_id)
        return []
