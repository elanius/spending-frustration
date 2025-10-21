from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
from app.auth import get_current_user
from app.db import db, users_collection

router = APIRouter()

# Local collection reference (no global helper to keep dependencies minimal)
rules_collection = db["rules"]


# --------- Pydantic Models (local, Pydantic v2) ---------


class RuleBase(BaseModel):
    conditions: List[Condition]
    logical_operator: str = "AND"
    priority: int = Field(ge=0)
    action: Action

    @field_validator("logical_operator")
    @classmethod
    def validate_op(cls, operator_value):
        if operator_value not in {"AND", "OR"}:
            raise ValueError("logical_operator must be AND or OR")
        return operator_value


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    conditions: Optional[List[Condition]] = None
    logical_operator: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)
    action: Optional[Action] = None

    @field_validator("logical_operator")
    @classmethod
    def validate_update_op(cls, operator_value):
        if operator_value is None:
            return operator_value
        if operator_value not in {"AND", "OR"}:
            raise ValueError("logical_operator must be AND or OR")
        return operator_value


class RuleOut(RuleBase):
    id: ObjectId = Field(alias="_id")
    user_id: ObjectId

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


# --------- Helpers (kept local) ---------
def parse_object_id(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    return ObjectId(id_str)


def get_user_document(email: str):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def doc_to_rule_out(doc) -> RuleOut:
    # Use model_validate for alias population
    return RuleOut.model_validate(doc)


# --------- Endpoints ---------
@router.get("", response_model=List[RuleOut])
def list_rules(current_email: str = Depends(get_current_user)):
    user = get_user_document(current_email)
    cursor = rules_collection.find({"user_id": user["_id"]}).sort("priority", -1)
    return [doc_to_rule_out(rule_document) for rule_document in cursor]


@router.post("", status_code=201)
def create_rule(rule: RuleCreate, current_email: str = Depends(get_current_user)):
    user = get_user_document(current_email)
    doc = rule.model_dump()
    doc["user_id"] = user["_id"]
    result = rules_collection.insert_one(doc)
    created = rules_collection.find_one({"_id": result.inserted_id})
    return doc_to_rule_out(created)


@router.get("/{rule_id}", response_model=RuleOut)
def get_rule(rule_id: str, current_email: str = Depends(get_current_user)):
    user = get_user_document(current_email)
    oid = parse_object_id(rule_id)
    doc = rules_collection.find_one({"_id": oid, "user_id": user["_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Rule not found")
    return doc_to_rule_out(doc)


@router.put("/{rule_id}")
def update_rule(rule_id: str, update: RuleUpdate, current_email: str = Depends(get_current_user)):
    user = get_user_document(current_email)
    oid = parse_object_id(rule_id)
    update_data = {
        field_name: field_value
        for field_name, field_value in update.model_dump(exclude_unset=True).items()
        if field_value is not None
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = rules_collection.update_one({"_id": oid, "user_id": user["_id"]}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule updated"}


@router.delete("/{rule_id}")
def delete_rule(rule_id: str, current_email: str = Depends(get_current_user)):
    user = get_user_document(current_email)
    oid = parse_object_id(rule_id)
    res = rules_collection.delete_one({"_id": oid, "user_id": user["_id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted"}
