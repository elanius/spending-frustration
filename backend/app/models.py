from pydantic import BaseModel, EmailStr, ConfigDict, Field
from enum import StrEnum
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


# who sends how much to whom and when,
# for what [goods, services, gifts],
# how [cash, card, transfer]
# details: message for recipient, notes for self


class TransactionType(StrEnum):
    CARD_PAYMENT = "card_payment"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    ACCOUNT_FEE = "account_fee"
    CANCEL_PAYMENT = "cancel_payment"


class AccountType(StrEnum):
    BANK = "bank"
    WALLET = "wallet"


class BankAccount(BaseModel):
    account_name: str
    iban: str | None = None
    bic: str | None = None


class Wallet(BaseModel):
    wallet_name: str


class Merchant(BaseModel):
    name: str


class Asset(BaseModel):
    bank: BankAccount | None = None
    wallet: Wallet | None = None


class Counterparty(BaseModel):
    bank: BankAccount | None = None
    wallet: Wallet | None = None
    merchant: Merchant | None = None


class Details(BaseModel):
    message_for_recipient: str | None = None
    transaction_note: str | None = None
    balance: float | None = None
    currency: str | None = None
    operation_type: str | None = None
    location: str | None = None
    symbols: dict[str, str] | None = None


class Transaction(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str
    asset: Asset
    counterparty: Counterparty | None
    date: datetime
    amount: float
    transaction_type: TransactionType | None = None
    description: str | None = None
    goods_services: list[str] | None = None
    category: str | None = None
    tags: list[str] | None = None
    note: str | None = None
    details: Details | None = None

    model_config = ConfigDict(populate_by_name=True)

    @property
    def merchant(self) -> str | None:
        if self.counterparty and self.counterparty.merchant:
            return self.counterparty.merchant.name
        return None

    @property
    def counterparty_name(self) -> str | None:
        if self.counterparty:
            if self.counterparty.merchant:
                return self.counterparty.merchant.name
            if self.counterparty.bank:
                return self.counterparty.bank.account_name
            if self.counterparty.wallet:
                return self.counterparty.wallet.wallet_name
        return None

    @property
    def counterparty_iban(self) -> str | None:
        if self.counterparty and self.counterparty.bank:
            return self.counterparty.bank.iban
        return None

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
