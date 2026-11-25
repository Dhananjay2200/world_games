"""
Admin Authentication Route using JWT.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
from app.config import get_settings
from app.utils.logging import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token: Optional[str] = None
    token_type: str = "bearer"
    username: Optional[str] = None
    status: Optional[str] = "success"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    settings = get_settings()
    username = (req.username or "").strip()
    password = (req.password or "").strip()

    expected_user = settings.ADMIN_USERNAME.strip()
    expected_pwd = settings.ADMIN_PASSWORD.strip()

    logger.info(f"Login attempt for user: '{username}'")

    if username.lower() == expected_user.lower() and password == expected_pwd:
        token = create_access_token({"sub": username, "role": "admin"})
        return {
            "access_token": token,
            "token": token,  # Provide both keys for compatibility
            "token_type": "bearer",
            "username": username,
            "status": "success",
        }

    logger.warning(f"Failed login attempt for user: '{username}'")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid administrator credentials. Please check your username and password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/verify")
def verify_token(token: str = Depends(oauth2_scheme)):
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return {"status": "authenticated", "user": payload.get("sub"), "role": payload.get("role")}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token expired or invalid.",
        )
