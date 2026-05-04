"""
backend/models/usuario.py
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class RolUsuario(str, enum.Enum):
    admin = "admin"
    docente = "docente"
    estudiante = "estudiante"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario), default=RolUsuario.estudiante)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    cursos_docente: Mapped[list["Curso"]] = relationship(  # type: ignore[name-defined]
        "Curso", back_populates="docente", foreign_keys="Curso.docente_id"
    )
    preguntas: Mapped[list["Pregunta"]] = relationship(  # type: ignore[name-defined]
        "Pregunta", back_populates="docente"
    )
    perfil_estudiante: Mapped[list["Estudiante"]] = relationship(  # type: ignore[name-defined]
        "Estudiante", back_populates="usuario"
    )
