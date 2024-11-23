from dataclasses import dataclass


@dataclass
class BankStatementEntry:
    realization_date: str
    description: str
    note: str
    recepient_name: str
    recepient_account: str
    amount: float
    category: str = ""
    tags: list[str] = []
