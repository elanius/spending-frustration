from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from bson import ObjectId
from datetime import datetime


class DBUser(BaseModel):
    _id: Optional[ObjectId] = None
    email: EmailStr
    hashed_password: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DBTransaction(BaseModel):
    _id: Optional[ObjectId] = None
    user_id: ObjectId
    date: datetime
    amount: float
    merchant: str
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DBRule(BaseModel):
    _id: Optional[ObjectId] = None
    user_id: ObjectId
    conditions: list  # store raw list of dicts; routers validate structure
    logical_operator: str
    priority: int
    action: dict  # {category, tags}

    model_config = ConfigDict(arbitrary_types_allowed=True)
