from spending_frustration.mbank_loader import MBankLoader
from pathlib import Path

from spending_frustration.struct_types import BankStatementEntry


class Loader:
    def __init__(self, path_dir):
        self.path_dir = path_dir
        self.files = [file for file in Path(self.path_dir).glob("*.csv") if file.is_file()]

    def load_entries(self):
        entries: list[BankStatementEntry] = []
        for file_path in self.files:
            with open(file_path, "r") as file:
                mbank_loader = MBankLoader(file.read())
                entries.extend(mbank_loader.parse())

        return entries
