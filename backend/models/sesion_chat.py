"""
backend/models/sesion_chat.py
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class RolMensaje(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class SesionChat(Base):
    __tablename__ = "sesiones_chat"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"))
    pregunta_id: Mapped[int] = mapped_column(ForeignKey("preguntas.id"))
    corte: Mapped[int] = mapped_column(Integer)  # 1, 2 o 3
    score_final: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    estudiante: Mapped["Estudiante"] = relationship(  # type: ignore[name-defined]
        "Estudiante", back_populates="sesiones"
    )
    pregunta: Mapped["Pregunta"] = relationship(  # type: ignore[name-defined]
        "Pregunta", back_populates="sesiones"
    )
    mensajes: Mapped[list["MensajeChat"]] = relationship(
        "MensajeChat", back_populates="sesion", cascade="all, delete-orphan"
    )
    respuestas: Mapped[list["RespuestaEstudiante"]] = relationship(
        "RespuestaEstudiante", back_populates="sesion", cascade="all, delete-orphan"
    )


class MensajeChat(Base):
    __tablename__ = "mensajes_chat"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sesion_id: Mapped[int] = mapped_column(ForeignKey("sesiones_chat.id"))
    rol: Mapped[RolMensaje] = mapped_column(Enum(RolMensaje))
    contenido: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    sesion: Mapped["SesionChat"] = relationship("SesionChat", back_populates="mensajes")


class RespuestaEstudiante(Base):
    __tablename__ = "respuestas_estudiante"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sesion_id: Mapped[int] = mapped_column(ForeignKey("sesiones_chat.id"))
    pregunta_id: Mapped[int] = mapped_column(ForeignKey("preguntas.id"))
    codigo_enviado: Mapped[str] = mapped_column(Text)
    passed_tests: Mapped[bool] = mapped_column(Boolean, default=False)
    bleu_score: Mapped[float] = mapped_column(Float, default=0.0)
    haiku_score: Mapped[float] = mapped_column(Float, default=0.0)
    intentos: Mapped[int] = mapped_column(Integer, default=1)

    sesion: Mapped["SesionChat"] = relationship("SesionChat", back_populates="respuestas")
    pregunta: Mapped["Pregunta"] = relationship("Pregunta", back_populates="respuestas")  # type: ignore[name-defined]
