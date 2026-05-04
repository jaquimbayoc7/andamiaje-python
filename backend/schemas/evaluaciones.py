"""
backend/schemas/evaluaciones.py
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RutaAprendizaje(BaseModel):
    temas_fuertes: list[str] = []
    temas_a_reforzar: list[str] = []
    ejercicios_recomendados: list[dict] = []
    recursos_externos: list[dict] = []
    mensaje_motivacional: str = ""


class EvaluacionSalida(BaseModel):
    id: int
    corte: int
    curso_id: int
    score_global: float
    ruta_aprendizaje: Optional[dict] = None
    enviada_email: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluacionDetalle(EvaluacionSalida):
    estudiante_id: int


class EnviarEmailResponse(BaseModel):
    enviado: bool
    mensaje: str
