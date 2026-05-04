"""
backend/services/analytics_service.py
Analítica descriptiva y predictiva (scikit-learn RandomForest).
"""

import logging
import os
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.evaluacion import Estudiante, Evaluacion
from backend.models.pregunta import Pregunta
from backend.models.prediccion_riesgo import PrediccionRiesgo
from backend.models.sesion_chat import SesionChat
from backend.models.usuario import Usuario
from src.claude_haiku import llamar_haiku

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "models" / "riesgo_model.pkl"

_TEMAS_FEATURES = ["variables", "listas", "funciones", "decoradores", "dataframes"]

# Cache del modelo en memoria
_modelo_cache: Optional[object] = None


def _cargar_modelo():
    global _modelo_cache
    if _modelo_cache is not None:
        return _modelo_cache
    if MODEL_PATH.exists():
        try:
            _modelo_cache = joblib.load(MODEL_PATH)
            logger.info("Modelo de riesgo cargado desde %s", MODEL_PATH)
        except Exception as exc:
            logger.warning("No se pudo cargar el modelo: %s", exc)
    return _modelo_cache


# ── Heatmap ───────────────────────────────────────────────────────────────────

async def calcular_heatmap(
    db: AsyncSession,
    curso_id: Optional[int] = None,
) -> dict:
    """
    Retorna score promedio por tema × nivel.
    """
    q = (
        select(
            Pregunta.tema,
            Pregunta.nivel,
            func.avg(SesionChat.score_final),
            func.count(SesionChat.id),
        )
        .join(SesionChat, SesionChat.pregunta_id == Pregunta.id)
        .where(SesionChat.score_final.isnot(None))
        .group_by(Pregunta.tema, Pregunta.nivel)
    )

    if curso_id:
        q = q.join(Estudiante, Estudiante.id == SesionChat.estudiante_id).where(
            Estudiante.curso_id == curso_id
        )

    result = await db.execute(q)
    filas = result.fetchall()

    heatmap: dict[str, dict] = {}
    for tema, nivel, avg_score, count in filas:
        if tema not in heatmap:
            heatmap[tema] = {}
        heatmap[tema][nivel.value if hasattr(nivel, "value") else nivel] = {
            "score_promedio": round(avg_score or 0, 3),
            "total_sesiones": count,
        }

    return heatmap


# ── Distribución de scores ────────────────────────────────────────────────────

async def distribucion_scores(
    db: AsyncSession,
    curso_id: Optional[int] = None,
) -> dict:
    """Retorna distribución de scores globales por corte."""
    q = (
        select(Evaluacion.corte, Evaluacion.score_global)
        .where(Evaluacion.score_global.isnot(None))
    )
    if curso_id:
        q = q.join(Estudiante, Estudiante.id == Evaluacion.estudiante_id).where(
            Estudiante.curso_id == curso_id
        )

    result = await db.execute(q)
    filas = result.fetchall()

    distribucion: dict[int, list[float]] = {1: [], 2: [], 3: []}
    for corte, score in filas:
        if corte in distribucion:
            distribucion[corte].append(score)

    return {
        corte: {
            "scores": scores,
            "promedio": round(sum(scores) / len(scores), 3) if scores else 0,
            "total": len(scores),
        }
        for corte, scores in distribucion.items()
    }


# ── Temas más débiles ─────────────────────────────────────────────────────────

async def temas_mas_debiles(
    db: AsyncSession,
    curso_id: Optional[int] = None,
    top_n: int = 5,
) -> list[dict]:
    """Retorna los N temas con menor score promedio."""
    q = (
        select(
            Pregunta.tema,
            func.avg(SesionChat.score_final).label("avg_score"),
            func.count(SesionChat.id).label("total"),
        )
        .join(SesionChat, SesionChat.pregunta_id == Pregunta.id)
        .where(SesionChat.score_final.isnot(None))
        .group_by(Pregunta.tema)
        .order_by(func.avg(SesionChat.score_final))
        .limit(top_n)
    )

    if curso_id:
        q = q.join(Estudiante, Estudiante.id == SesionChat.estudiante_id).where(
            Estudiante.curso_id == curso_id
        )

    result = await db.execute(q)
    return [
        {"tema": t, "score_promedio": round(avg or 0, 3), "total_sesiones": total}
        for t, avg, total in result.fetchall()
    ]


# ── Insight narrativo con Haiku ───────────────────────────────────────────────

async def generar_insight_grupo(
    resumen_estadistico: dict,
) -> str:
    """Genera insight en lenguaje natural sobre el grupo."""
    system = (
        "Eres un analista pedagógico experto. "
        "Basándote en estadísticas del grupo, genera un insight breve (2-3 oraciones) "
        "con observaciones y recomendaciones concretas. Responde en español."
    )
    prompt = (
        "Estadísticas del grupo:\n"
        + "\n".join(f"- {k}: {v}" for k, v in resumen_estadistico.items())
        + "\n\nGenera el insight pedagógico:"
    )
    respuesta = llamar_haiku(system, prompt, max_tokens=200, temperatura=0.5)
    return respuesta or "No se pudo generar el insight en este momento."


# ── Predicción de riesgo ──────────────────────────────────────────────────────

async def _build_features(estudiante: Estudiante, corte: int, db: AsyncSession) -> list[float]:
    """Construye el vector de features para el modelo ML."""
    # Scores por tema
    result = await db.execute(
        select(Pregunta.tema, func.avg(SesionChat.score_final))
        .join(SesionChat, SesionChat.pregunta_id == Pregunta.id)
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
            SesionChat.score_final.isnot(None),
        )
        .group_by(Pregunta.tema)
    )
    scores_tema = {t: s for t, s in result.fetchall()}

    features = [scores_tema.get(tema, 0.0) for tema in _TEMAS_FEATURES]

    # Semestre normalizado (1-10)
    features.append(min(estudiante.semestre / 10.0, 1.0))

    # Intentos promedio
    result_int = await db.execute(
        select(func.avg(SesionChat.score_final))
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
        )
    )
    avg_score = result_int.scalar_one_or_none() or 0.0
    features.append(float(avg_score))

    # Tasa de sesiones completadas
    result_total = await db.execute(
        select(func.count(SesionChat.id)).where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
        )
    )
    result_comp = await db.execute(
        select(func.count(SesionChat.id)).where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
            SesionChat.score_final >= 0.7,
        )
    )
    total = result_total.scalar_one() or 1
    comp = result_comp.scalar_one() or 0
    features.append(comp / total)

    # Corte actual
    features.append(corte / 3.0)

    return features


async def predecir_riesgo(
    estudiante: Estudiante,
    corte: int,
    db: AsyncSession,
) -> dict:
    """
    Predice si el estudiante está en riesgo usando el modelo ML.
    Si no hay modelo, usa regla simple: score_global < 0.4 en primeras 3 sesiones.
    """
    # Regla temprana sin modelo
    result = await db.execute(
        select(func.count(SesionChat.id), func.avg(SesionChat.score_final))
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
        )
    )
    total_sesiones, avg_score = result.one()
    avg_score = avg_score or 0.0

    modelo = _cargar_modelo()

    if modelo and total_sesiones >= 3:
        features = await _build_features(estudiante, corte, db)
        X = np.array(features).reshape(1, -1)
        try:
            score_riesgo = float(modelo.predict_proba(X)[0][1])
            en_riesgo = score_riesgo > 0.5
        except Exception as exc:
            logger.warning("Error en predicción ML: %s", exc)
            en_riesgo = avg_score < 0.4
            score_riesgo = 1.0 - avg_score
    else:
        # Regla heurística
        en_riesgo = avg_score < 0.4 and total_sesiones >= 3
        score_riesgo = max(0.0, 1.0 - avg_score * 2)

    # Temas débiles
    result_temas = await db.execute(
        select(Pregunta.tema, func.avg(SesionChat.score_final))
        .join(SesionChat, SesionChat.pregunta_id == Pregunta.id)
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
            SesionChat.score_final.isnot(None),
        )
        .group_by(Pregunta.tema)
        .having(func.avg(SesionChat.score_final) < 0.6)
    )
    temas_debiles = [{"tema": t, "score": round(s or 0, 3)} for t, s in result_temas.fetchall()]

    return {
        "score_riesgo": round(score_riesgo, 3),
        "en_riesgo": en_riesgo,
        "temas_debiles": temas_debiles,
        "sesiones_analizadas": total_sesiones,
        "score_promedio": round(avg_score, 3),
    }


async def guardar_prediccion(
    estudiante: Estudiante,
    corte: int,
    prediccion: dict,
    db: AsyncSession,
) -> PrediccionRiesgo:
    """Persiste la predicción de riesgo."""
    result = await db.execute(
        select(PrediccionRiesgo).where(
            PrediccionRiesgo.estudiante_id == estudiante.id,
            PrediccionRiesgo.corte == corte,
        )
    )
    pred = result.scalar_one_or_none()

    if pred:
        pred.score_riesgo = prediccion["score_riesgo"]
        pred.en_riesgo = prediccion["en_riesgo"]
        pred.temas_debiles = prediccion.get("temas_debiles", [])
    else:
        pred = PrediccionRiesgo(
            estudiante_id=estudiante.id,
            corte=corte,
            curso_id=estudiante.curso_id or 1,
            score_riesgo=prediccion["score_riesgo"],
            en_riesgo=prediccion["en_riesgo"],
            temas_debiles=prediccion.get("temas_debiles", []),
        )
        db.add(pred)

    await db.flush()
    return pred


# ── Entrenamiento del modelo ──────────────────────────────────────────────────

async def entrenar_modelo(db: AsyncSession) -> dict:
    """
    Re-entrena el modelo RandomForest con todas las evaluaciones disponibles.
    Requiere mínimo 10 muestras con score definido.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
    except ImportError:
        return {"error": "scikit-learn no instalado"}

    # Cargar todos los estudiantes con evaluaciones
    result = await db.execute(select(Estudiante))
    estudiantes = result.scalars().all()

    X_list, y_list = [], []
    for est in estudiantes:
        for corte in (1, 2, 3):
            ev_result = await db.execute(
                select(Evaluacion.score_global).where(
                    Evaluacion.estudiante_id == est.id,
                    Evaluacion.corte == corte,
                )
            )
            ev = ev_result.scalar_one_or_none()
            if ev is None:
                continue

            features = await _build_features(est, corte, db)
            X_list.append(features)
            y_list.append(1 if ev < 0.6 else 0)  # en_riesgo si score < 0.6

    if len(X_list) < 10:
        return {"error": f"Datos insuficientes: {len(X_list)} muestras (mínimo 10)"}

    X = np.array(X_list)
    y = np.array(y_list)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    scores_cv = cross_val_score(modelo, X, y, cv=min(5, len(X_list)), scoring="roc_auc")
    modelo.fit(X, y)

    # Persistir modelo
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, MODEL_PATH)

    global _modelo_cache
    _modelo_cache = modelo

    return {
        "muestras": len(X_list),
        "roc_auc_cv": round(float(scores_cv.mean()), 3),
        "modelo_guardado": str(MODEL_PATH),
    }
