from abc import ABC, abstractmethod
from spending_frustration.struct_types import BankStatementEntry


class Rule(ABC):
    @abstractmethod
    def match(self, entry: BankStatementEntry) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply_rule(self, entry: BankStatementEntry) -> BankStatementEntry:
        raise NotImplementedError


class Categorize:
    def __init__(self):
        self.rules: list[Rule] = []

    def categorize_entries(self, entries: list[BankStatementEntry]) -> list[BankStatementEntry]:
        categorized_entries: list[BankStatementEntry] = []
        for entry in entries:
            categorized_entries.append(self._categorize(entry))
        return categorized_entries

    def _categorize(self, entry: BankStatementEntry):
        for rule in self.rules:
            if rule.match(entry):
                return rule.apply_rule(entry)
        return "Unknown"
