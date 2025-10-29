from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel
from fastapi import HTTPException
from app.auth import get_user_id
from app.db import DB
from app.rules.parser import parse_rule

db = DB.get_instance()
router = APIRouter()


class RuleIn(BaseModel):
    rule: str
    active: bool = True


class RuleUpdate(BaseModel):
    rule: Optional[str] = None
    active: Optional[bool] = None


class RuleOut(BaseModel):
    id: str
    rule: str
    active: bool


@router.get("", response_model=List[RuleOut])
def list_rules(user_id: str = Depends(get_user_id)):
    rules = db.get_rules(user_id=user_id)
    return [RuleOut(id=r.id or "", rule=r.rule, active=r.active) for r in rules]


@router.post("", status_code=201, response_model=RuleOut)
def create_rule(rule_in: RuleIn, user_id: str = Depends(get_user_id)):
    parse_rule(rule_in.rule)
    # Create as a plain dict to let DB layer handle ObjectId conversion
    doc = {"rule": rule_in.rule, "active": rule_in.active}
    inserted_id = db.add_rule(user_id, doc, priority=0)
    return RuleOut(id=inserted_id, rule=rule_in.rule, active=rule_in.active)


@router.get("/export", response_model=list[str])
def export_rules(user_id: str = Depends(get_user_id)):
    rules = db.get_rules(user_id=user_id)
    # return rules as text. Every rule on its own line
    return [r.rule for r in rules]


@router.post("/import", status_code=201)
def import_rules(rules: list[str], user_id: str = Depends(get_user_id)):
    for rule in rules:
        parse_rule(rule)
        db.add_rule(user_id, {"rule": rule, "active": True}, priority=0)
    return {"message": "Rules imported"}


@router.put("/{rule_id}", response_model=RuleOut)
def update_rule(rule_id: str, update: RuleUpdate, user_id: str = Depends(get_user_id)):
    # validate fields
    update_data = {k: v for k, v in update.model_dump(exclude_unset=True).items() if v is not None}
    if "rule" in update_data:
        parse_rule(update_data["rule"])

    existing = db.get_rule(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found")
    if existing.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    ok = db.update_rule(rule_id, update_data)
    if not ok:
        raise HTTPException(status_code=404, detail="Rule not found or not modified")
    updated = db.get_rule(rule_id)
    return RuleOut(id=updated.id or "", rule=updated.rule, active=updated.active)


@router.get("/{rule_id}", response_model=RuleOut)
def get_rule(rule_id: str, user_id: str = Depends(get_user_id)):
    existing = db.get_rule(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found")
    if existing.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return RuleOut(id=existing.id or "", rule=existing.rule, active=existing.active)


@router.delete("/{rule_id}")
def delete_rule(rule_id: str, user_id: str = Depends(get_user_id)):
    existing = db.get_rule(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found")
    if existing.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    ok = db.delete_rule(rule_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete")
    return {"message": "Rule deleted"}
