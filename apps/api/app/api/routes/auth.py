from fastapi import APIRouter, HTTPException, Request, status

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_rate_limit import clear_login_failures, is_login_allowed, register_login_failure

router = APIRouter(tags=["auth"])


def _is_valid_admin_password(password: str) -> bool:
    password_hash = (settings.admin_password_hash or "").strip()
    if password_hash:
        try:
            return verify_password(password, password_hash)
        except Exception:
            return False

    return password == settings.admin_password


def _identity(request: Request, username: str) -> str:
    client_host = getattr(request.client, "host", None) or "unknown"
    return f"{client_host}:{username.strip().lower()}"


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request) -> LoginResponse:
    login_identity = _identity(request, payload.username)

    if not is_login_allowed(login_identity):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много попыток входа. Попробуй позже.",
        )

    is_valid = payload.username == settings.admin_username and _is_valid_admin_password(payload.password)
    if not is_valid:
        register_login_failure(login_identity)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    clear_login_failures(login_identity)
    token = create_access_token(subject=payload.username)
    return LoginResponse(access_token=token)
