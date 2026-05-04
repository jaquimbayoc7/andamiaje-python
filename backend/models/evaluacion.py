"""
backend/models/evaluacion.py
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True)
    semestre: Mapped[int] = mapped_column(Integer)
    programa_academico: Mapped[str] = mapped_column(String(200))
    curso_id: Mapped[int | None] = mapped_column(ForeignKey("cursos.id"), nullable=True)

    usuario: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="perfil_estudiante"
    )
    curso: Mapped["Curso"] = relationship(  # type: ignore[name-defined]
        "Curso", back_populates="estudiantes"
    )
    sesiones: Mapped[list["SesionChat"]] = relationship(  # type: ignore[name-defined]
        "SesionChat", back_populates="estudiante"
    )
    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        "Evaluacion", back_populates="estudiante"
    )
    predicciones: Mapped[list["PrediccionRiesgo"]] = relationship(  # type: ignore[name-defined]
        "PrediccionRiesgo", back_populates="estudiante"
    )


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"))
    corte: Mapped[int] = mapped_column(Integer)  # 1, 2 o 3
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"))
    score_global: Mapped[float] = mapped_column(Float, default=0.0)
    ruta_aprendizaje: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    enviada_email: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    estudiante: Mapped["Estudiante"] = relationship("Estudiante", back_populates="evaluaciones")
