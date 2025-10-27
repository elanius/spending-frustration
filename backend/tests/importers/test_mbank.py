import sys
from pathlib import Path

# Ensure backend root is importable
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.importers import mbank  # noqa: E402
from app.models import TransactionType  # noqa: E402


def test_mbank_match_and_parse():
    # Statement sample stored under tests/data/mbank
    data_path = Path(__file__).resolve().parents[1] / "data" / "mbank" / "01924152_240801_241031.csv"
    raw = data_path.read_text(encoding="utf-8")

    assert mbank.match(raw) is True, "Should detect mBank statement"

    # Provide a synthetic user_id placeholder now required by the parser
    transactions = mbank.parse(raw, "test-user-id")
    # Basic sanity checks
    assert len(transactions) > 50  # file contains many rows

    for tx in transactions:
        assert tx.user_id == "test-user-id"
        assert isinstance(tx.amount, float) and tx.amount != 0.0
        assert tx.date is not None and tx.date.year == 2024

        if tx.transaction_type is TransactionType.CARD_PAYMENT:
            assert tx.counterparty is not None
            assert tx.counterparty.merchant is not None
            assert tx.counterparty.merchant.name != ""
        elif tx.transaction_type is TransactionType.TRANSFER:
            assert tx.counterparty is not None
            assert tx.counterparty.bank is not None
            assert tx.counterparty.bank.iban is not None
        elif tx.transaction_type is TransactionType.ACCOUNT_FEE:
            assert tx.counterparty is not None
            assert tx.counterparty.bank is not None
            assert tx.counterparty.bank.account_name == "mBank"
        elif tx.transaction_type is TransactionType.WITHDRAWAL:
            assert tx.counterparty is not None
            assert tx.counterparty.merchant is not None
            assert tx.counterparty.merchant.name != ""
