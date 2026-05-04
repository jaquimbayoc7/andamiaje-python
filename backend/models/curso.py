"""
backend/models/curso.py
"""

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    docente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    periodo: Mapped[str] = mapped_column(String(20))  # ej: 2026-1
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    docente: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="cursos_docente", foreign_keys=[docente_id]
    )
    estudiantes: Mapped[list["Estudiante"]] = relationship(  # type: ignore[name-defined]
        "Estudiante", back_populates="curso"
    )
