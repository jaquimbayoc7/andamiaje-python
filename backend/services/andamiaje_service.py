"""
backend/services/andamiaje_service.py
Genera los 3 niveles de andamiaje para una pregunta usando Claude Haiku.
"""

import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.pregunta import Andamiaje, NivelAndamiaje, Pregunta
from src.claude_haiku import llamar_haiku

logger = logging.getLogger(__name__)

_SYSTEM_ANDAMIAJE = (
    "Eres un tutor experto de Python para candidatos de entrevistas técnicas. "
    "Tu misión es generar pistas pedagógicas (andamiaje) para ayudar a un estudiante "
    "a resolver un ejercicio de Python. El andamiaje debe ser educativo, claro y preciso. "
    "Responde SOLO con el texto del andamiaje, sin encabezados ni explicaciones adicionales."
)

# Sanitiza inputs antes de enviar a Haiku (previene prompt injection)
_INJECTION_PATTERNS = re.compile(
    r"(\n---\n|<\|im_end\|>|\[INST\]|\[/INST\]|<s>|</s>|###|System:|Human:|Assistant:)",
    re.IGNORECASE,
)


def _sanitize(texto: str) -> str:
    return _INJECTION_PATTERNS.sub(" ", texto).strip()


def _prompt_andamiaje(enunciado: str, nivel_rol: str, nivel_andamiaje: str) -> str:
    guias = {
        "minimo": (
            "Proporciona una pista MUY sutil: solo una orientación conceptual de 1-2 oraciones "
            "que dirija al estudiante sin revelar la solución. No incluyas código."
        ),
        "parcial": (
            "Proporciona una pista PARCIAL: explica el concepto clave y muestra un fragmento "
            "de código ilustrativo (máximo 3 líneas) sin dar la solución completa."
        ),
        "completo": (
            "Proporciona andamiaje COMPLETO: explica el enfoque paso a paso e incluye "
            "la estructura del código (con partes clave pero dejando que el estudiante complete los detalles)."
        ),
    }
    return (
        f"Ejercicio de Python nivel {nivel_rol}:\n"
        f"{_sanitize(enunciado)}\n\n"
        f"Tipo de andamiaje: {nivel_andamiaje.upper()}\n"
        f"Instrucción: {guias[nivel_andamiaje]}"
    )


async def generar_andamiajes(
    pregunta: Pregunta,
    db: AsyncSession,
) -> list[Andamiaje]:
    """
    Genera los 3 niveles de andamiaje para una pregunta.
    Guarda los registros en la BD y retorna la lista.
    """
    niveles = [NivelAndamiaje.minimo, NivelAndamiaje.parcial, NivelAndamiaje.completo]
    andamiajes_creados: list[Andamiaje] = []

    for nivel in niveles:
        prompt = _prompt_andamiaje(pregunta.enunciado, pregunta.nivel.value, nivel.value)
        contenido = llamar_haiku(
            system_prompt=_SYSTEM_ANDAMIAJE,
            user_prompt=prompt,
            max_tokens=512,
            temperatura=0.5,
        )

        if not contenido:
            contenido = f"[Andamiaje {nivel.value} no disponible — genera uno manualmente]"
            logger.warning("Haiku no generó andamiaje %s para pregunta %d", nivel.value, pregunta.id)

        andamiaje = Andamiaje(
            pregunta_id=pregunta.id,
            nivel_andamiaje=nivel,
            contenido=contenido,
        )
        db.add(andamiaje)
        andamiajes_creados.append(andamiaje)

    await db.flush()
    return andamiajes_creados
