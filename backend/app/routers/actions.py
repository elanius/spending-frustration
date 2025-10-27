import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_user_id
from app.rules.rule_engine import RuleEngine
from app.db import DB

db = DB.get_instance()
router = APIRouter()
logger = logging.getLogger(__name__)


class RuleOut(BaseModel):
    success: bool
    details: str


@router.post("/apply_all_rules", response_model=RuleOut)
def apply_rules(user_id: str = Depends(get_user_id)):
    logger.info(f"Applying all rules for user {user_id}")
    rule_engine = RuleEngine(user_id)
    transactions = db.get_transactions(user_id)
    modified_transactions = rule_engine.apply_rules(transactions)
    for tx in modified_transactions:
        db.update_transaction(tx.id, tx)
    return RuleOut(success=True, details="All applicable rules have been applied.")
