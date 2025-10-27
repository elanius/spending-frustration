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

from dataclasses import dataclass
from enum import Enum, auto
import re
from datetime import datetime
from bson import ObjectId
from app.models import Asset, BankAccount, Counterparty, Details, Merchant, Transaction, TransactionType


class ParserError(Exception):
    """Generic parser error."""


HEADER_MARKER = "#Dátum zaúčtovania transakcie"
BANK_ID_MARKER = "mBank S.A."

DATE_RE = re.compile(r"\d{2}-\d{2}-\d{4}")


def match(data: str) -> bool:
    """Return True if the given raw text looks like an mBank SK statement."""
    return HEADER_MARKER in data and BANK_ID_MARKER in data


def _strip_text(value: str) -> str:
    return value.strip().strip("'\"").rstrip(";")


def _parse_amount(raw: str) -> float:
    raw = raw.strip().replace(" ", "")  # remove thousands spaces
    # standardize decimal comma
    raw = raw.replace(",", ".")
    if raw == "":
        raise ParserError("empty amount")
    return float(raw)


@dataclass
class Row:
    posting_date: str  # Dátum zaúčtovania transakcie
    execution_date: str  # Dátum uskutočnenia transakcie
    operation_type: str  # Popis operácie
    description: str  # Popis
    counterparty: str  # Platca/Príjemca
    account_number: str  # Číslo účtu platcu/príjemcu
    ks: str  # KS
    vs: str  # VS
    ss: str  # ŠS
    amount: str  # Suma transakcie
    balance: str  # Účtovný zostatok po transakcii


def _parse_card_payment(row: Row, tx: Transaction) -> Transaction:
    tx.transaction_type = TransactionType.CARD_PAYMENT
    match = re.search(r"^(.*?)\s*/(.*?)\s*DÁTUM VYKONANIA TRANSAKCIE:\s*(\d{4}-\d{2}-\d{2})$", row.description)
    if match:
        tx.counterparty = Counterparty(merchant=Merchant(name=match.group(1).strip()))
        tx.date = datetime.strptime(match.group(3), "%Y-%m-%d")
        tx.details.location = match.group(2).strip()
    else:
        raise ParserError("Unable to parse card payment description")
    return tx


def _parse_transfer(row: Row, tx: Transaction) -> Transaction:
    tx.transaction_type = TransactionType.TRANSFER
    tx.counterparty = Counterparty(bank=BankAccount(account_name=row.counterparty, iban=row.account_number))
    tx.details.symbols = {"ks": row.ks, "vs": row.vs, "ss": row.ss}
    return tx


def _parse_account_fee(row: Row, tx: Transaction) -> Transaction:
    tx.transaction_type = TransactionType.ACCOUNT_FEE
    tx.counterparty = Counterparty(bank=BankAccount(account_name="mBank"))
    return tx


def _parse_cancel_payment(row: Row, tx: Transaction) -> Transaction:
    tx.transaction_type = TransactionType.CANCEL_PAYMENT
    tx.counterparty = Counterparty(bank=BankAccount(account_name="mBank"))
    return tx


def _parse_withdrawal(row: Row, tx: Transaction) -> Transaction:
    # structure of text is the same as for card payment
    tx = _parse_card_payment(row, tx)
    tx.transaction_type = TransactionType.WITHDRAWAL
    return tx


def _parse_by_operation_type(row: Row, tx: Transaction) -> Transaction:
    tx.details.operation_type = row.operation_type
    tx.description = " ".join(row.description.split())

    if row.operation_type == "PLATBA KARTOU":
        return _parse_card_payment(row, tx)
    elif row.operation_type in ["POPLATOK ZA ZRÝCHLENÚ PLATBU", "POPL. ZA PREDEF. ZRÝCHLENÚ PLATBU"]:
        return _parse_account_fee(row, tx)
    elif row.operation_type == "STORNO DEBET.OPERÁCIE":
        return _parse_cancel_payment(row, tx)
    elif row.operation_type in [
        "INKASO",
        "MEDZIBANKOVÝ PREVOD",
        "POS VRÁTENIE TOVARU",
        "PRIJATÁ PLATBA MEDZIBANKOVÁ",
        "TRVALÁ PLATBA DO MBANK",
        "TRVALÁ PLATBA MEDZIBANKOVÁ",
        "ZRÝCHLENÁ PLATBA TUZEMSKÁ",
    ]:
        return _parse_transfer(row, tx)
    elif row.operation_type == "VÝBER V BANKOMATE":
        return _parse_withdrawal(row, tx)


def _parse_one_transaction(raw_line: str, user_id: ObjectId, bank_account: BankAccount) -> Transaction | None:
    parts = raw_line.split(";")
    # Expect at least 11 columns (some final empty because of trailing ;) )
    if len(parts) < 11:
        return None

    for i in range(len(parts)):
        parts[i] = _strip_text(parts[i])

    row = Row(*parts[:11])

    tx = Transaction(
        user_id=user_id,
        asset=Asset(bank=bank_account),
        counterparty=None,
        date=datetime.strptime(row.posting_date, "%d-%m-%Y"),
        amount=_parse_amount(row.amount),
        transaction_type=None,
        details=Details(balance=_parse_amount(row.balance)),
    )

    tx = _parse_by_operation_type(row, tx)
    return tx


class ParseState(Enum):
    ITERATE = auto()
    TRANSACTIONS = auto()
    CURRENCY = auto()
    ACCOUNT_TYPE = auto()
    IBAN = auto()
    BIC = auto()


def parse(data: str, user_id: ObjectId) -> list[Transaction]:
    """Parse mBank statement text into a list of ``Transaction`` objects."""

    transactions: list[Transaction] = []

    account_name = None
    currency = None
    iban = None
    bic = None

    bank_account: BankAccount | None = None

    parser_state = ParseState.ITERATE

    for line in data.splitlines():
        line = _strip_text(line)
        if line == "":
            continue

        if parser_state == ParseState.TRANSACTIONS:
            if bank_account is None:
                if account_name is None:
                    raise ParserError("Account name not found during parsing")
                if iban is None:
                    raise ParserError("IBAN not found during parsing")
                if bic is None:
                    raise ParserError("BIC not found during parsing")

                bank_account = BankAccount(
                    account_name=account_name,
                    iban=iban,
                    bic=bic,
                )

            tx = _parse_one_transaction(line, user_id, bank_account)
            if tx:
                tx.details.currency = currency
                transactions.append(tx)

        elif parser_state == ParseState.ITERATE:
            if line.startswith("#Mena účtu:"):
                parser_state = ParseState.CURRENCY
            elif line.startswith("#Typ účtu:"):
                parser_state = ParseState.ACCOUNT_TYPE
            elif line.startswith("#IBAN:"):
                parser_state = ParseState.IBAN
            elif line.startswith("#BIC:"):
                parser_state = ParseState.BIC
            elif line.startswith(HEADER_MARKER):
                parser_state = ParseState.TRANSACTIONS

        elif parser_state == ParseState.CURRENCY:
            currency = line.strip()
            parser_state = ParseState.ITERATE

        elif parser_state == ParseState.ACCOUNT_TYPE:
            account_name = line.strip()
            parser_state = ParseState.ITERATE

        elif parser_state == ParseState.IBAN:
            iban = line.strip()
            parser_state = ParseState.ITERATE

        elif parser_state == ParseState.BIC:
            bic = line.strip()
            parser_state = ParseState.ITERATE

    lines = [ln for ln in data.splitlines() if ln.strip() != ""]

    # Find header index
    try:
        header_idx = next(i for i, ln in enumerate(lines) if ln.startswith(HEADER_MARKER))
    except StopIteration:
        return []

    transactions: list[Transaction] = []

    for raw_line in lines[header_idx + 1 :]:
        tx = _parse_one_transaction(raw_line, user_id, bank_account)
        if tx:
            transactions.append(tx)

    return transactions
