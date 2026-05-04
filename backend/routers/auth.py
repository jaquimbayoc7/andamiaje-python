"""
backend/routers/auth.py
Endpoints de autenticación: register, login, me.
Rate limiting básico en login/register.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.models.usuario import RolUsuario, Usuario
from backend.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UsuarioPublico

router = APIRouter()

# Rate limiting simple en memoria (por IP)
_login_attempts: dict[str, list[float]] = {}
_LIMIT = 10  # max intentos por minuto


def _check_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc).timestamp()
    attempts = [t for t in _login_attempts.get(ip, []) if now - t < 60]
    if len(attempts) >= _LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espera un minuto.",
        )
    attempts.append(now)
    _login_attempts[ip] = attempts


@router.post("/register", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    _check_rate_limit(request)

    existing = await db.execute(select(Usuario).where(Usuario.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")

    user = Usuario(
        nombre_completo=body.nombre_completo,
        email=body.email,
        password_hash=hash_password(body.password),
        rol=RolUsuario(body.rol),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    _check_rate_limit(request)

    result = await db.execute(select(Usuario).where(Usuario.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")

    token = create_access_token(str(user.id), user.rol.value)
    return {"access_token": token}


@router.get("/me", response_model=UsuarioPublico)
async def me(current_user: Annotated[Usuario, Depends(get_current_user)]):
    return current_user
