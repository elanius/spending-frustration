"""CSV Upload Router.

Parses a CSV file and inserts transaction documents. Required columns:
date, amount, merchant. Optional: category, tags, notes.
Returns insertion summary + sample + per-row errors.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional
from io import StringIO
import csv
from datetime import datetime
from app.auth import get_user_id
from app.db import db

router = APIRouter()

# All transaction insertion now goes through db.insert_transaction


REQUIRED_COLUMNS = {"date", "amount", "merchant"}
OPTIONAL_COLUMNS = {"category", "tags", "notes"}
ALL_COLUMNS = REQUIRED_COLUMNS.union(OPTIONAL_COLUMNS)


def get_user_document(email: str):
    try:
        return db.get_user_id(email)
    except ValueError:
        raise HTTPException(status_code=401, detail="User not found")


def parse_date(value: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value}")


def normalize_tags(raw_tags: Optional[str]):
    if raw_tags is None or raw_tags.strip() == "":
        return []
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


@router.post("")
async def upload_statement(file: UploadFile = File(...), current_email: str = Depends(get_user_id)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    user_document = get_user_document(current_email)

    try:
        raw_bytes = await file.read()
        text = raw_bytes.decode("utf-8")
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}")

    reader = csv.DictReader(StringIO(text))
    header_columns = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - header_columns
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(sorted(missing))}",
        )

    unexpected = header_columns - ALL_COLUMNS

    inserted_documents: List[str] = []
    skipped_rows: List[dict] = []
    sample_rows: List[dict] = []

    for row_index, csv_row in enumerate(reader, start=1):
        try:
            date_value = parse_date(csv_row.get("date", ""))
            amount_raw = csv_row.get("amount", "").strip()
            if amount_raw == "":
                raise ValueError("amount empty")
            amount_value = float(amount_raw)
            merchant_value = csv_row.get("merchant", "").strip()
            if merchant_value == "":
                raise ValueError("merchant empty")
            category_value = (csv_row.get("category") or None) or None
            tags_value = normalize_tags(csv_row.get("tags")) if csv_row.get("tags") else []
            notes_value = (csv_row.get("notes") or None) or None

            document = {
                "user_id": str(user_document["_id"]),
                "date": date_value,
                "amount": amount_value,
                "merchant": merchant_value,
                "category": category_value,
                "tags": tags_value if tags_value else [],
                "notes": notes_value,
            }
            inserted_id = db.insert_transaction_for_user(
                str(user_document["_id"]), {k: v for k, v in document.items() if k != "user_id"}
            )
            inserted_documents.append(str(inserted_id))
            if len(sample_rows) < 5:
                sample_rows.append(
                    {
                        **{k: (str(v) if isinstance(v, datetime) else v) for k, v in document.items()},
                        "_id": str(inserted_id),
                    }
                )
        except Exception as row_exc:
            skipped_rows.append(
                {
                    "row_index": row_index,
                    "error": str(row_exc),
                    "raw": {k: v for k, v in csv_row.items()},
                }
            )

    return {
        "inserted": len(inserted_documents),
        "skipped": len(skipped_rows),
        "unexpected_columns": sorted(list(unexpected)),
        "sample": sample_rows,
        "errors": skipped_rows,
    }
