import argparse
from pathlib import Path

from app.db import get_user_id, transactions_collection
from app.importers.importer import Importer


def main():  # pragma: no cover - utility script
    parser = argparse.ArgumentParser(description="Import bank statements into MongoDB")
    parser.add_argument("--user", required=True, help="User to associate transactions with")
    parser.add_argument("--file", type=Path, required=True, help="Statement file path (CSV export)")
    args = parser.parse_args()

    user_id = get_user_id(args.user)
    importer = Importer(user_id)
    transaction_count = importer.import_from_file(args.file)

    print(f"Imported {transaction_count} transactions for user {args.user}")

    transactions_collection.insert_many


if __name__ == "__main__":  # pragma: no cover
    main()
