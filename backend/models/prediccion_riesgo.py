"""
backend/models/prediccion_riesgo.py
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class PrediccionRiesgo(Base):
    __tablename__ = "predicciones_riesgo"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"))
    corte: Mapped[int] = mapped_column(Integer)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"))
    score_riesgo: Mapped[float] = mapped_column(Float, default=0.0)
    en_riesgo: Mapped[bool] = mapped_column(Boolean, default=False)
    temas_debiles: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notificado_docente: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    estudiante: Mapped["Estudiante"] = relationship(  # type: ignore[name-defined]
        "Estudiante", back_populates="predicciones"
    )
