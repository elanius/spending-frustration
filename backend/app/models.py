from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from pydantic import field_validator
from bson import ObjectId


class User(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    username: str
    hashed_password: str
    email: EmailStr | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("id", mode="before")
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class Transaction(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str
    date: datetime
    amount: float
    merchant: str
    category: str | None = None
    tags: list[str] | None = None
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("id", mode="before")
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator("user_id", mode="before")
    def validate_user_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class RuleDB(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str
    rule: str
    active: bool = True

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("id", mode="before")
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_validator("user_id", mode="before")
    def validate_user_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


# Note: rules are now stored as separate documents in `rules` collection.
