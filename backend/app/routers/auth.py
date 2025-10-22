from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.auth import get_password_hash, verify_password, create_access_token
from app.db import db
from app.models import User


router = APIRouter()


class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", status_code=201)
def register(user: UserRegister):
    # Check existing user
    try:
        existing = db.get_user(user.username)
        if existing:
            raise HTTPException(status_code=400, detail="User already registered")
    except ValueError:
        # not found -> proceed
        pass

    hashed_password = get_password_hash(user.password)
    user_model = User(username=user.username, email=user.email, hashed_password=hashed_password)
    inserted_id = db.create_user(user_model)
    return {"message": "User created", "user_id": str(inserted_id)}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = db.get_user(form_data.username)
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}
