import argparse
from pathlib import Path

from app.db import DB
from app.importers.importer import Importer

db = DB.get_instance()


def main():  # pragma: no cover - utility script
    parser = argparse.ArgumentParser(description="Import bank statements into MongoDB")
    parser.add_argument("--username", required=True, help="User to associate transactions with")
    parser.add_argument("--file", type=Path, required=True, help="Statement file path (CSV export)")
    args = parser.parse_args()

    user = db.get_user(args.username)
    importer = Importer(user.id)
    transaction_count = importer.import_from_file(args.file)

    print(f"Imported {transaction_count} transactions for user {args.username}")

    # Placeholder: additional post-import processing could go here


if __name__ == "__main__":  # pragma: no cover
    main()
