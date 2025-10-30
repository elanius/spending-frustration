from fastapi import APIRouter, Depends
from typing import List
from app.auth import get_user_id
from app.db import DB

db = DB.get_instance()
router = APIRouter()


@router.get("", response_model=List[str])
def list_tags(user_id: str = Depends(get_user_id)):
    """Return all distinct tags for the current user."""
    return db.get_tags(user_id)
