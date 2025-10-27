"""Import textual rules for a user into single UserRules document.

Usage examples:
    python -m app.scripts.import_rules --user-email user@example.com --file rules.txt
    python -m app.scripts.import_rules --user-email user@example.com --rule 'merchant contains Coffee -> @coffee #caffeinated'
    cat rules.txt | python -m app.scripts.import_rules --user-email user@example.com --append

Behavior:
  * Reads rules from --rule flags, a file, stdin, or any combination.
  * Validates each rule using Filter.parse.
  * Stores/updates a single document in collection 'user_rules':
        { user_id: <ObjectId>, rules: [ {rule: <string>, name: <optional>, active: true}, ... ] }
  * By default replaces existing rules. Pass --append to extend instead.
  * --dry-run shows the resulting document without writing.

Lines beginning with '#' or blank lines are ignored when reading from file/stdin.
"""

import argparse
from pathlib import Path
from typing import Iterable

from app.db import DB
from app.rules.parser import parse_rule
from app.rules.rule import Rule
from app.models import User, RuleDB

db = DB.get_instance()


def read_rules_from_file(file_path: Path) -> list[str]:
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    else:
        raise SystemExit("No file path provided for reading rules")


def validate_rules(raw_lines: Iterable[str]) -> list[Rule]:
    parsed: list[Rule] = []
    for line in raw_lines:
        rule_str = line.strip()
        if not rule_str or rule_str.startswith("#"):
            continue
        try:
            parsed.append(parse_rule(rule_str))
        except ValueError as e:
            raise SystemExit(f"Invalid rule '{rule_str}': {e}")
    return parsed


def import_user_rules(user: str, rules: list[Rule], dry_run: bool):
    try:
        user_doc = db.get_user_id(user)
    except ValueError:
        raise SystemExit(f"User '{user}' not found")
    user = User.model_validate(user_doc)

    if dry_run:
        print("Dry run - would insert the following rules:")
        for r in rules:
            print(str(r))
        return

    for r in rules:
        rule_doc = RuleDB(user_id=user.id, rule=str(r), active=True)
        db.add_rule(user.id, rule_doc, priority=0)
    print(f"Inserted {len(rules)} rules for user {user}")


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Import textual rules for a user")
    parser.add_argument("--user", required=True)
    parser.add_argument("--file", type=Path, help="File containing rule lines (defaults to stdin if piped)")
    args = parser.parse_args(argv)

    raw_lines = read_rules_from_file(args.file)
    parsed_rules = validate_rules(raw_lines)
    import_user_rules(args.user, parsed_rules, dry_run=args.dry_run)


if __name__ == "__main__":  # pragma: no cover
    main()
