import sys
from pathlib import Path
from bson import ObjectId

# Ensure backend root is importable
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.importers import mbank  # noqa: E402


def test_mbank_match_and_parse():
    # Statement sample stored under tests/data/mbank
    data_path = Path(__file__).resolve().parents[1] / "data" / "mbank" / "01924152_240801_241031.csv"
    raw = data_path.read_text(encoding="utf-8")

    assert mbank.match(raw) is True, "Should detect mBank statement"

    # Provide a synthetic user_id placeholder now required by the parser
    transactions = mbank.parse(raw, ObjectId())
    # Basic sanity checks
    assert len(transactions) > 50  # file contains many rows
    first = transactions[0]
    # Validate required fields populated
    assert first.date.year == 2024
    assert isinstance(first.amount, float)
    assert first.merchant != "" and first.merchant is not None
    # Ensure both positive (credits) and negative (debits) present
    amounts = {t.amount for t in transactions}
    assert any(a > 0 for a in amounts), "Expect at least one credit"
    assert any(a < 0 for a in amounts), "Expect at least one debit"
