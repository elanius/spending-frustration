from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel, field_validator, ConfigDict, Field
from datetime import datetime
from bson import ObjectId
from app.auth import get_current_user
from app.db import db, users_collection

router = APIRouter()

transactions_collection = db["transactions"]


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


class TransactionResponse(TransactionBase):
    id: str = Field(alias="_id")
    user_id: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    @field_validator("id", "user_id", mode="before")
    @classmethod
    def object_id_to_str(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value


def get_user(email: str):
    user_document = users_collection.find_one({"email": email})
    if not user_document:
        raise HTTPException(status_code=401, detail="User not found")
    return user_document


def oid(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    return ObjectId(id_str)


@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    current_email: str = Depends(get_current_user),
):
    user = get_user(current_email)
    query_filter = {"user_id": user["_id"]}
    skip = (page - 1) * limit
    cursor = transactions_collection.find(query_filter, sort={"date": -1})
    cursor = cursor.skip(skip).limit(limit)
    return [
        TransactionResponse.model_validate(transaction_document)
        for transaction_document in cursor
    ]


@router.get("/filter", response_model=List[TransactionResponse])
def filter_transactions(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    merchant_contains: Optional[str] = None,
    current_email: str = Depends(get_current_user),
):
    user = get_user(current_email)
    query_filter = {"user_id": user["_id"]}
    if date_from or date_to:
        query_filter["date"] = {}
        if date_from:
            query_filter["date"]["$gte"] = date_from
        if date_to:
            query_filter["date"]["$lte"] = date_to
    if category:
        query_filter["category"] = category
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            query_filter["tags"] = {"$all": tag_list}
    if amount_min is not None or amount_max is not None:
        query_filter["amount"] = {}
        if amount_min is not None:
            query_filter["amount"]["$gte"] = amount_min
        if amount_max is not None:
            query_filter["amount"]["$lte"] = amount_max
    if merchant_contains:
        query_filter["merchant"] = {"$regex": merchant_contains, "$options": "i"}
    cursor = transactions_collection.find(query_filter).sort("date", -1)
    return [
        TransactionResponse.model_validate(transaction_document)
        for transaction_document in cursor
    ]


@router.get("/{tx_id}", response_model=TransactionResponse)
def get_transaction(tx_id: str, current_email: str = Depends(get_current_user)):
    user = get_user(current_email)
    doc = transactions_collection.find_one({"_id": oid(tx_id), "user_id": user["_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse.model_validate(doc)


@router.patch("/{tx_id}")
def patch_transaction(
    tx_id: str, patch: TransactionPatch, current_email: str = Depends(get_current_user)
):
    user = get_user(current_email)
    update_data = {
        field_name: field_value
        for field_name, field_value in patch.model_dump(exclude_unset=True).items()
        if field_value is not None
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = transactions_collection.update_one(
        {"_id": oid(tx_id), "user_id": user["_id"]}, {"$set": update_data}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction updated"}
