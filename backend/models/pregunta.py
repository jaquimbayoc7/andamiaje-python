"""
backend/models/pregunta.py
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class NivelPregunta(str, enum.Enum):
    junior = "junior"
    semi_senior = "semi_senior"
    senior = "senior"


class NivelAndamiaje(str, enum.Enum):
    minimo = "minimo"
    parcial = "parcial"
    completo = "completo"


class Pregunta(Base):
    __tablename__ = "preguntas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(300))
    enunciado: Mapped[str] = mapped_column(Text)
    solucion_referencia: Mapped[str] = mapped_column(Text)
    nivel: Mapped[NivelPregunta] = mapped_column(Enum(NivelPregunta))
    tema: Mapped[str] = mapped_column(String(100))
    docente_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    docente: Mapped["Usuario"] = relationship(  # type: ignore[name-defined]
        "Usuario", back_populates="preguntas"
    )
    andamiajes: Mapped[list["Andamiaje"]] = relationship(
        "Andamiaje", back_populates="pregunta", cascade="all, delete-orphan"
    )
    sesiones: Mapped[list["SesionChat"]] = relationship(  # type: ignore[name-defined]
        "SesionChat", back_populates="pregunta"
    )
    respuestas: Mapped[list["RespuestaEstudiante"]] = relationship(  # type: ignore[name-defined]
        "RespuestaEstudiante", back_populates="pregunta"
    )


class Andamiaje(Base):
    __tablename__ = "andamiajes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pregunta_id: Mapped[int] = mapped_column(ForeignKey("preguntas.id"))
    nivel_andamiaje: Mapped[NivelAndamiaje] = mapped_column(Enum(NivelAndamiaje))
    contenido: Mapped[str] = mapped_column(Text)

    pregunta: Mapped["Pregunta"] = relationship("Pregunta", back_populates="andamiajes")
