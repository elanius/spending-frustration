"""mBank (SK) statement importer.

The raw export is a semi-colon separated pseudo-CSV (";" as delimiter), with
values sometimes quoted, using comma as decimal separator and space as
thousands separator. We only care about transactional rows after the header
line beginning with::

    #Dátum zaúčtovania transakcie;#Dátum uskutočnenia transakcie; ...

Returned objects are pydantic ``Transaction`` models with a synthetic
``user_id`` placeholder. The application typically inserts transactions via
the upload router; external callers should overwrite ``user_id`` when
persisting.
"""

from __future__ import annotations

import re
from datetime import datetime
from bson import ObjectId
from app.models import Transaction

HEADER_MARKER = "#Dátum zaúčtovania transakcie"
BANK_ID_MARKER = "mBank S.A."

DATE_RE = re.compile(r"\d{2}-\d{2}-\d{4}")


def match(data: str) -> bool:
    """Return True if the given raw text looks like an mBank SK statement."""
    return HEADER_MARKER in data and BANK_ID_MARKER in data


def _parse_amount(raw: str) -> float:
    raw = raw.strip().replace(" ", "")  # remove thousands spaces
    # standardize decimal comma
    raw = raw.replace(",", ".")
    if raw == "":
        raise ValueError("empty amount")
    return float(raw)


def _clean_text(value: str) -> str:
    return value.strip().strip("'\"").strip()


def _extract_merchant(operation_type: str, description: str, counterparty: str) -> str:
    counterparty = _clean_text(counterparty)
    if counterparty and counterparty != "":
        return counterparty

    description = _clean_text(description)
    # For card payments the merchant sits at the start of the description followed by many spaces and 'DÁTUM'
    if description:
        # Cut off the execution date marker if present
        part = re.split(r"DÁTUM VYKONANIA TRANSAKCIE", description, 1)[0]
        # Collapse whitespace
        part = re.sub(r"\s+", " ", part).strip(" /")
        if part:
            return part

    op = _clean_text(operation_type)
    return op or "UNKNOWN"


def parse(data: str, user_id: ObjectId) -> list[Transaction]:
    """Parse mBank statement text into a list of ``Transaction`` objects.

    Notes:
        * ``user_id`` is a fresh ObjectId placeholder; integrate layer should overwrite.
        * Only rows whose first field matches a posting date pattern are considered.
        * Amount keeps its sign (credits positive, debits negative as present in file).
    """

    if not match(data):  # quick guard
        return []

    lines = [ln for ln in data.splitlines() if ln.strip() != ""]

    # Find header index
    try:
        header_idx = next(i for i, ln in enumerate(lines) if ln.startswith(HEADER_MARKER))
    except StopIteration:
        return []

    transactions: list[Transaction] = []

    for raw_line in lines[header_idx + 1 :]:
        if not raw_line or raw_line.startswith("#"):
            continue
        parts = raw_line.split(";")
        # Expect at least 11 columns (some final empty because of trailing ;) )
        if len(parts) < 11:
            continue
        posting_date = parts[0].strip()
        if not DATE_RE.fullmatch(posting_date):
            # end if we encounter a non-date after data started (summary/footer)
            continue
        try:
            date_obj = datetime.strptime(posting_date, "%d-%m-%Y")
        except ValueError:
            continue

        operation_type = parts[2]
        description = parts[3]
        counterparty = parts[4]
        amount_raw = parts[9]

        try:
            amount = _parse_amount(amount_raw)
        except Exception:  # pragma: no cover - skip malformed line
            continue

        merchant = _extract_merchant(operation_type, description, counterparty)

        tx = Transaction(
            user_id=user_id,
            date=date_obj,
            amount=amount,
            merchant=merchant,
            category=None,
            tags=[],
            notes=None,
        )
        transactions.append(tx)

    return transactions
