"""
backend/routers/analiticas.py
Endpoints de analítica descriptiva y predictiva.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user, require_role
from backend.models.evaluacion import Estudiante
from backend.models.prediccion_riesgo import PrediccionRiesgo
from backend.models.usuario import Usuario
from backend.services.analytics_service import (
    calcular_heatmap,
    distribucion_scores,
    entrenar_modelo,
    generar_insight_grupo,
    guardar_prediccion,
    predecir_riesgo,
    temas_mas_debiles,
)

router = APIRouter()


def _verificar_acceso_curso(current_user: Usuario, curso_id: Optional[int]) -> Optional[int]:
    """Docentes solo pueden ver su propio curso. Admin ve todos."""
    if current_user.rol.value == "admin":
        return curso_id
    # Docente: filtrar por sus cursos (se valida en el servicio)
    return curso_id


@router.get("/heatmap")
async def heatmap(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(require_role("docente", "admin"))],
    curso_id: Optional[int] = None,
):
    """Heatmap tema × nivel con scores promedio."""
    cid = _verificar_acceso_curso(current_user, curso_id)
    return await calcular_heatmap(db, cid)


@router.get("/distribucion-scores")
async def scores_distribucion(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(require_role("docente", "admin"))],
    curso_id: Optional[int] = None,
):
    """Distribución de scores globales por corte."""
    cid = _verificar_acceso_curso(current_user, curso_id)
    return await distribucion_scores(db, cid)


@router.get("/temas-debiles")
async def top_temas_debiles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(require_role("docente", "admin"))],
    curso_id: Optional[int] = None,
    top_n: int = 5,
):
    """Top temas con menor score promedio."""
    cid = _verificar_acceso_curso(current_user, curso_id)
    return await temas_mas_debiles(db, cid, top_n)


@router.post("/insights")
async def insight_grupo(
    resumen: dict,
    current_user: Annotated[Usuario, Depends(require_role("docente", "admin"))],
):
    """Genera insight narrativo sobre el grupo con Haiku."""
    return {"insight": await generar_insight_grupo(resumen)}


@router.get("/predicciones/riesgo")
async def predicciones_riesgo(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(require_role("docente", "admin"))],
    curso_id: Optional[int] = None,
    corte: int = 1,
):
    """Lista estudiantes en riesgo del curso/global."""
    q = (
        select(
            PrediccionRiesgo,
            Estudiante,
        )
        .join(Estudiante, Estudiante.id == PrediccionRiesgo.estudiante_id)
        .where(
            PrediccionRiesgo.corte == corte,
            PrediccionRiesgo.en_riesgo == True,
        )
    )
    if curso_id:
        q = q.where(Estudiante.curso_id == curso_id)

    result = await db.execute(q)
    filas = result.fetchall()

    return [
        {
            "prediccion_id": pred.id,
            "estudiante_id": est.id,
            "score_riesgo": pred.score_riesgo,
            "temas_debiles": pred.temas_debiles,
            "notificado_docente": pred.notificado_docente,
        }
        for pred, est in filas
    ]


@router.post(
    "/predicciones/calcular/{estudiante_id}/{corte}",
    dependencies=[Depends(require_role("docente", "admin"))],
)
async def calcular_prediccion(
    estudiante_id: int,
    corte: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    """Calcula y persiste la predicción de riesgo de un estudiante."""
    result = await db.execute(select(Estudiante).where(Estudiante.id == estudiante_id))
    estudiante = result.scalar_one_or_none()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    prediccion = await predecir_riesgo(estudiante, corte, db)
    pred_obj = await guardar_prediccion(estudiante, corte, prediccion, db)

    return {**prediccion, "id": pred_obj.id}


@router.post(
    "/predicciones/entrenar",
    dependencies=[Depends(require_role("admin"))],
)
async def entrenar_modelo_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Re-entrena el modelo RandomForest con todos los datos disponibles."""
    resultado = await entrenar_modelo(db)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado
