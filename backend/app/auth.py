# auth.py: Authentication utilities for FastAPI
import os
import logging
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional


# Password hashing context
# Use pbkdf2_sha256 for broader compatibility in minimal test environments where
# certain bcrypt backends may not behave well (long password detection edge cases).
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = "CHANGE_ME_TO_A_RANDOM_SECRET"  # Should be set from env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 24))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Log token creation (do not log the token itself)
    try:
        sub = data.get("sub")
    except Exception:
        sub = None
    logger.info("Created access token for subject=%s", sub)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("Decoded access token for subject=%s", payload.get("sub"))
        return payload
    except JWTError:
        logger.warning("Failed to decode access token")
        return None


def get_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return payload["sub"]
