import re

from spending_frustration.struct_types import BankStatementEntry


pattern = re.compile(
    r"(?P<date_posted>\d{2}-\d{2}-\d{4});"
    r"(?P<date_transaction>\d{2}-\d{2}-\d{4});"
    r'"(?P<operation_desc>.*?)";'
    r'"(?P<description>.*?)";'
    r'"(?P<payer_recipient>.*?)";'
    r"'(?P<account_number>.*?)';"
    r"(?P<ks>.*?);"
    r"(?P<vs>.*?);"
    r"(?P<ss>.*?);"
    r"(?P<transaction_amount>[-\d.,]*);"
    r"(?P<balance_after_transaction>[-\d., ]*);"
)


class MBankLoader:
    def __init__(self, content):
        self.content = content

    def parse(self) -> list[BankStatementEntry]:
        entries: list[BankStatementEntry] = []

        for match in pattern.finditer(self.content):
            transaction = match.groupdict()

            # Convert numeric fields to float and handle commas
            transaction_amount = float(transaction["transaction_amount"].replace(",", ".").replace(" ", ""))

            # Create a BankStatementEntry instance
            entry = BankStatementEntry(
                realization_date=transaction["date_transaction"],
                description=transaction["operation_desc"].strip(),
                note=transaction["description"].strip(),
                recepient_name=transaction["payer_recipient"].strip(),
                recepient_account=transaction["account_number"].strip(),
                amount=transaction_amount,
            )

            entries.append(entry)

        return entries
