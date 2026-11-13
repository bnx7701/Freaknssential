
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from pydantic import BaseModel

from backend.core.auth import (
    verify_admin_credentials,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenResponse)
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    if not verify_admin_credentials(
        form_data.username,
        form_data.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(form_data.username)

    return {
        "access_token": token,
        "token_type": "bearer",
    }
