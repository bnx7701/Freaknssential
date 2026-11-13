
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config.settings import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD_HASH,
    JWT_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

password_hasher = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_admin_credentials(username: str, password: str) -> bool:
    if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
        return False

    if username != ADMIN_USERNAME:
        return False

    return password_hasher.verify(password, ADMIN_PASSWORD_HASH)


def create_access_token(username: str) -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": "admin",
        "exp": expires_at,
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired admin token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

        username = payload.get("sub")

        if (
            not username
            or username != ADMIN_USERNAME
            or payload.get("role") != "admin"
        ):
            raise unauthorized

        return username

    except InvalidTokenError:
        raise unauthorized
