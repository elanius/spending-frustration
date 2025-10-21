from pydantic import BaseModel, EmailStr, ConfigDict, Field
from bson import ObjectId
from datetime import datetime


class User(BaseModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    email: EmailStr
    hashed_password: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Transaction(BaseModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    user_id: ObjectId
    date: datetime
    amount: float
    merchant: str
    category: str | None = None
    tags: list[str] | None = None
    notes: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RuleDB(BaseModel):
    rule: str
    name: str | None = None
    active: bool = True


class UserRules(BaseModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    user_id: ObjectId
    rules: list[RuleDB]

    model_config = ConfigDict(arbitrary_types_allowed=True)
