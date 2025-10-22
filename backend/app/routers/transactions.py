from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.auth import get_user_id
from app.db import db
from app.models import Transaction

router = APIRouter()


class TransactionBase(BaseModel):
    date: datetime
    amount: float
    merchant: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    notes: Optional[str] = None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        return value


class TransactionCreate(TransactionBase):
    pass


class TransactionPatch(BaseModel):
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_patch_tags(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        return value


@router.get("", response_model=List[Transaction])
def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    current_user: str = Depends(get_user_id),
):
    return db.get_transactions(current_user)


@router.get("/filter", response_model=List[Transaction])
def filter_transactions(
    merchant_contains: Optional[str] = None,
    current_user: str = Depends(get_user_id),
):
    # Simple filter implementation used by tests: filter by merchant substring
    docs = db._transactions_collection.find({"user_id": __import__("bson").ObjectId(current_user)})
    results: list[Transaction] = []
    for d in docs:
        m = d.get("merchant", "")
        if merchant_contains is None or merchant_contains.lower() in m.lower():
            results.append(Transaction.model_validate(d))
    return results


@router.get("/{tx_id}", response_model=Transaction)
def get_transaction(tx_id: str, current_user: str = Depends(get_user_id)):
    tx = db.get_transaction(tx_id)
    if not tx:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Transaction not found")
    if tx.user_id != current_user:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Not allowed")
    return tx


@router.patch("/{tx_id}")
def patch_transaction(tx_id: str, patch: TransactionPatch, current_user: str = Depends(get_user_id)):
    update_data = {
        field_name: field_value
        for field_name, field_value in patch.model_dump(exclude_unset=True).items()
        if field_value is not None
    }
    if not update_data:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="No fields to update")

    # Ensure transaction exists and belongs to current user
    tx = db.get_transaction(tx_id)
    if not tx:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Transaction not found")
    if tx.user_id != current_user:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Not allowed")

    ok = db.update_transaction(tx_id, update_data)
    if not ok:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Transaction not found or not modified")
    return {"message": "Transaction updated"}
