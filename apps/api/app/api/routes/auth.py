from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(tags=["auth"])


def _is_valid_admin_password(password: str) -> bool:
    password_hash = (settings.admin_password_hash or "").strip()
    if password_hash:
        try:
            return verify_password(password, password_hash)
        except Exception:
            return False

    return password == settings.admin_password


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if payload.username != settings.admin_username or not _is_valid_admin_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    token = create_access_token(subject=payload.username)
    return LoginResponse(access_token=token)
