import argparse
import os
from spending_frustration.load_bank_statement import Loader
from spending_frustration.rules import Categorize


def main():
    parser = argparse.ArgumentParser(description="Parse bank statements from a folder containing .csv files.")
    parser.add_argument("folder", type=str, help="Path to the folder containing .csv files")

    args = parser.parse_args()
    folder_path = args.folder

    if not os.path.isdir(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    loader = Loader(folder_path)
    entries = loader.load_entries()

    categorize = Categorize
    categorized_entries = categorize.categorize_entries(entries)


if __name__ == "__main__":
    main()
