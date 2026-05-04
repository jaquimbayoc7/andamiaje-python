"""
backend/schemas/auth.py
Schemas Pydantic para autenticación.
"""

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    rol: str = "estudiante"

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        if v not in {"admin", "docente", "estudiante"}:
            raise ValueError("Rol debe ser admin, docente o estudiante")
        return v

    @field_validator("password")
    @classmethod
    def password_minima(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioPublico(BaseModel):
    id: int
    nombre_completo: str
    email: str
    rol: str
    activo: bool

    model_config = {"from_attributes": True}
