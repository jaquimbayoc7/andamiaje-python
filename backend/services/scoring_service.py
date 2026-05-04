"""
backend/services/scoring_service.py
Calcula el score global de un estudiante en un corte y genera la ruta de aprendizaje.
"""

import json
import logging
import re
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.evaluacion import Estudiante, Evaluacion
from backend.models.curso import Curso
from backend.models.pregunta import Pregunta
from backend.models.sesion_chat import RespuestaEstudiante, SesionChat
from src.claude_haiku import llamar_haiku_json

logger = logging.getLogger(__name__)

_SYSTEM_RUTA = (
    "Eres un coach pedagógico experto en Python. "
    "Basándote en el desempeño del estudiante, genera una ruta de aprendizaje personalizada. "
    "Responde ÚNICAMENTE con JSON válido en el formato especificado, sin texto adicional."
)

_INJECTION_RE = re.compile(
    r"(\n---\n|<\|im_end\|>|\[INST\]|\[/INST\]|<s>|</s>|###)", re.IGNORECASE
)


def _sanitize(texto: str) -> str:
    return _INJECTION_RE.sub(" ", str(texto)).strip()


# ── Cálculo del score ─────────────────────────────────────────────────────────

async def calcular_score_global(
    estudiante: Estudiante,
    corte: int,
    db: AsyncSession,
) -> dict:
    """
    Calcula el score global del estudiante en el corte usando la fórmula:
    score_global = (pass_tests × 0.40) + (haiku_score × 0.30) + (bleu_score × 0.20) + (eficiencia_intentos × 0.10)
    eficiencia_intentos = max(0, 1 - (intentos - 1) × 0.1)

    Retorna dict con score_global, scores por tema, y métricas detalladas.
    """
    result = await db.execute(
        select(
            SesionChat,
            Pregunta.tema,
        )
        .join(Pregunta, Pregunta.id == SesionChat.pregunta_id)
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
        )
    )
    sesiones = result.fetchall()

    if not sesiones:
        return {"score_global": 0.0, "scores_por_tema": {}, "sesiones_evaluadas": 0}

    scores_sesiones = []
    scores_por_tema: dict[str, list[float]] = {}

    for sesion, tema in sesiones:
        # Obtener la última respuesta de la sesión
        resp_result = await db.execute(
            select(RespuestaEstudiante)
            .where(RespuestaEstudiante.sesion_id == sesion.id)
            .order_by(RespuestaEstudiante.intentos.desc())
            .limit(1)
        )
        respuesta = resp_result.scalar_one_or_none()

        if respuesta:
            eficiencia = max(0.0, 1.0 - (respuesta.intentos - 1) * 0.1)
            score = (
                (1.0 if respuesta.passed_tests else 0.0) * 0.40
                + respuesta.haiku_score * 0.30
                + respuesta.bleu_score * 0.20
                + eficiencia * 0.10
            )
        elif sesion.score_final is not None:
            score = sesion.score_final
        else:
            score = 0.0

        score = round(score, 4)
        scores_sesiones.append(score)

        if tema not in scores_por_tema:
            scores_por_tema[tema] = []
        scores_por_tema[tema].append(score)

    score_global = round(sum(scores_sesiones) / len(scores_sesiones), 4) if scores_sesiones else 0.0
    scores_por_tema_avg = {t: round(sum(v) / len(v), 4) for t, v in scores_por_tema.items()}

    return {
        "score_global": score_global,
        "scores_por_tema": scores_por_tema_avg,
        "sesiones_evaluadas": len(scores_sesiones),
    }


# ── Ruta de aprendizaje ───────────────────────────────────────────────────────

async def generar_ruta_aprendizaje(
    estudiante: Estudiante,
    corte: int,
    score_global: float,
    scores_por_tema: dict,
    db: AsyncSession,
) -> dict:
    """Genera la ruta de aprendizaje personalizada usando Claude Haiku."""
    temas_fuertes = [t for t, s in scores_por_tema.items() if s >= 0.7]
    temas_debiles = [t for t, s in scores_por_tema.items() if s < 0.6]

    # Preguntas que el estudiante no ha completado (para recomendar)
    completadas_result = await db.execute(
        select(SesionChat.pregunta_id)
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
            SesionChat.score_final >= 0.7,
        )
    )
    completadas_ids = {r[0] for r in completadas_result.fetchall()}

    # Buscar ejercicios de temas débiles no completados
    candidatas_result = await db.execute(
        select(Pregunta.id, Pregunta.titulo, Pregunta.tema, Pregunta.nivel)
        .where(
            Pregunta.activa == True,
            Pregunta.tema.in_(temas_debiles) if temas_debiles else False,
            Pregunta.id.not_in(completadas_ids) if completadas_ids else True,
        )
        .limit(3)
    )
    candidatas = candidatas_result.fetchall()

    ejercicios_rec = [
        {"id": str(p.id), "titulo": _sanitize(p.titulo), "razon": f"Reforzar {p.tema}"}
        for p in candidatas
    ]

    prompt = f"""
Estudiante en corte {corte} con score global: {score_global:.0%}
Temas fuertes: {', '.join(temas_fuertes) if temas_fuertes else 'ninguno aún'}
Temas a reforzar: {', '.join(temas_debiles) if temas_debiles else 'todos van bien'}
Semestre: {estudiante.semestre}
Programa: {_sanitize(estudiante.programa_academico)}

Genera una ruta de aprendizaje con este JSON exacto:
{{
  "temas_fuertes": {json.dumps(temas_fuertes, ensure_ascii=False)},
  "temas_a_reforzar": {json.dumps(temas_debiles, ensure_ascii=False)},
  "ejercicios_recomendados": {json.dumps(ejercicios_rec, ensure_ascii=False)},
  "recursos_externos": [
    {{"titulo": "nombre del recurso", "url": "https://...", "tipo": "video|docs|ejercicio"}}
  ],
  "mensaje_motivacional": "mensaje de 1-2 oraciones motivador y personalizado"
}}

Completa los recursos_externos con 2-3 recursos reales de Python relacionados con los temas a reforzar.
Personaliza el mensaje_motivacional según el desempeño.
"""

    try:
        ruta = llamar_haiku_json(_SYSTEM_RUTA, prompt, max_tokens=800)
    except Exception as exc:
        logger.warning("Haiku no disponible para ruta de aprendizaje: %s", exc)
        ruta = None

    if not ruta:
        # Fallback sin Haiku
        ruta = {
            "temas_fuertes": temas_fuertes,
            "temas_a_reforzar": temas_debiles,
            "ejercicios_recomendados": ejercicios_rec,
            "recursos_externos": [
                {"titulo": "Python Docs", "url": "https://docs.python.org/3/", "tipo": "docs"},
            ],
            "mensaje_motivacional": f"¡Vas bien con un {score_global:.0%}! Sigue practicando los temas que tienes pendientes.",
        }

    # Normalizar: garantizar que ejercicios_recomendados y recursos_externos sean listas de dicts
    for key in ("ejercicios_recomendados", "recursos_externos"):
        items = ruta.get(key, [])
        if isinstance(items, list):
            ruta[key] = [
                item if isinstance(item, dict) else {"titulo": str(item), "razon": "", "url": "#", "tipo": "recurso"}
                for item in items
            ]

    return ruta


# ── Guardar o actualizar evaluación ──────────────────────────────────────────

async def calcular_y_guardar_evaluacion(
    estudiante: Estudiante,
    corte: int,
    db: AsyncSession,
) -> Evaluacion:
    """Calcula el score, genera la ruta y persiste la evaluación."""
    resultado = await calcular_score_global(estudiante, corte, db)
    score_global = resultado["score_global"]
    scores_por_tema = resultado["scores_por_tema"]

    ruta = await generar_ruta_aprendizaje(estudiante, corte, score_global, scores_por_tema, db)

    # Buscar evaluación existente para este corte
    ev_result = await db.execute(
        select(Evaluacion).where(
            Evaluacion.estudiante_id == estudiante.id,
            Evaluacion.corte == corte,
        )
    )
    evaluacion = ev_result.scalar_one_or_none()

    if evaluacion:
        evaluacion.score_global = score_global
        evaluacion.ruta_aprendizaje = ruta
    else:
        # Resolver curso_id: usar el del estudiante o el primero disponible en la BD
        curso_id = estudiante.curso_id
        if not curso_id:
            curso_result = await db.execute(select(Curso.id).limit(1))
            curso_id = curso_result.scalar_one_or_none()
        if not curso_id:
            raise ValueError("No hay cursos disponibles en la BD para asignar la evaluación")

        evaluacion = Evaluacion(
            estudiante_id=estudiante.id,
            corte=corte,
            curso_id=curso_id,
            score_global=score_global,
            ruta_aprendizaje=ruta,
        )
        db.add(evaluacion)

    await db.flush()
    return evaluacion
