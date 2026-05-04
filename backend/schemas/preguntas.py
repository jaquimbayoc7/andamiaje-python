"""
backend/schemas/preguntas.py
Schemas Pydantic para preguntas y andamiajes.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class AndamiajeSalida(BaseModel):
    id: int
    nivel_andamiaje: str
    contenido: str

    model_config = {"from_attributes": True}


class PreguntaCrear(BaseModel):
    titulo: str
    enunciado: str
    solucion_referencia: str
    nivel: str
    tema: str

    @field_validator("nivel")
    @classmethod
    def nivel_valido(cls, v: str) -> str:
        if v not in {"junior", "semi_senior", "senior"}:
            raise ValueError("Nivel debe ser junior, semi_senior o senior")
        return v


class PreguntaActualizar(BaseModel):
    titulo: Optional[str] = None
    enunciado: Optional[str] = None
    solucion_referencia: Optional[str] = None
    nivel: Optional[str] = None
    tema: Optional[str] = None
    activa: Optional[bool] = None


class PreguntaSalida(BaseModel):
    id: int
    titulo: str
    enunciado: str
    nivel: str
    tema: str
    activa: bool
    created_at: datetime
    docente_id: Optional[int] = None
    andamiajes: list[AndamiajeSalida] = []

    model_config = {"from_attributes": True}


class PreguntaResumen(BaseModel):
    """Versión liviana sin andamiajes ni solución de referencia."""
    id: int
    titulo: str
    nivel: str
    tema: str
    activa: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ImportarCSVResultado(BaseModel):
    creadas: int
    errores: list[str] = []
