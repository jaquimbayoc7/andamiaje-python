"""
backend/schemas/chat.py
Schemas Pydantic para el chat adaptativo.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IniciarSesionRequest(BaseModel):
    corte: int  # 1, 2 o 3


class IniciarSesionResponse(BaseModel):
    sesion_id: int
    pregunta_id: int
    titulo: str
    enunciado: str
    nivel_andamiaje_actual: str
    andamiaje: str
    mensaje_bienvenida: str


class MensajeRequest(BaseModel):
    sesion_id: int
    contenido: str


class MensajeResponse(BaseModel):
    rol: str
    contenido: str
    nivel_andamiaje_actual: str
    timestamp: datetime


class EvaluarCodigoRequest(BaseModel):
    sesion_id: int
    codigo: str


class EvaluarCodigoResponse(BaseModel):
    passed_tests: bool
    bleu_score: float
    haiku_score: float
    intentos: int
    score_parcial: float
    feedback: str
    nivel_andamiaje_actual: str
    andamiaje_actualizado: Optional[str] = None
    sesion_completada: bool = False


class MensajeSalida(BaseModel):
    id: int
    rol: str
    contenido: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class SesionDetalle(BaseModel):
    id: int
    pregunta_id: int
    corte: int
    score_final: Optional[float]
    started_at: datetime
    ended_at: Optional[datetime]
    mensajes: list[MensajeSalida] = []

    model_config = {"from_attributes": True}
