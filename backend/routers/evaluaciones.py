"""
backend/routers/evaluaciones.py
Endpoints de evaluación y rutas de aprendizaje.
"""

import logging

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user, require_role
from backend.models.evaluacion import Estudiante, Evaluacion
from backend.models.usuario import Usuario
from backend.schemas.evaluaciones import EnviarEmailResponse, EvaluacionDetalle, EvaluacionSalida
from backend.services.email_service import enviar_email_evaluacion
from backend.services.scoring_service import calcular_y_guardar_evaluacion

logger = logging.getLogger(__name__)
router = APIRouter()


async def _get_perfil_o_404(user: Usuario, db: AsyncSession) -> Estudiante:
    result = await db.execute(select(Estudiante).where(Estudiante.usuario_id == user.id))
    perfil = result.scalar_one_or_none()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de estudiante no encontrado")
    return perfil


@router.post(
    "/calcular/{corte}",
    response_model=EvaluacionSalida,
    dependencies=[Depends(require_role("estudiante"))],
)
async def calcular_evaluacion(
    corte: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """
    Calcula (o recalcula) el score del corte indicado y genera la ruta de aprendizaje personalizada.

    - Analiza todas las sesiones de chat del corte usando Claude Haiku.
    - Genera temas fuertes, temas a reforzar, ejercicios recomendados y recursos externos.
    - **Envía automáticamente la ruta de aprendizaje por email** (requiere SendGrid configurado).
    - Si la evaluación ya existe para ese corte, la recalcula y actualiza.
    - `enviada_email: true` en la respuesta indica que el email fue enviado.
    """
    if corte not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Corte debe ser 1, 2 o 3")

    perfil = await _get_perfil_o_404(current_user, db)
    evaluacion = await calcular_y_guardar_evaluacion(perfil, corte, db)

    # Enviar email automáticamente con la ruta de aprendizaje
    try:
        enviado = await enviar_email_evaluacion(current_user, perfil, evaluacion)
        if enviado:
            evaluacion.enviada_email = True
            await db.flush()
            logger.info("Email de evaluación enviado automáticamente a %s", current_user.email)
        else:
            logger.warning("Email no enviado a %s (SendGrid no configurado)", current_user.email)
    except Exception as exc:
        logger.error("Error al enviar email automático: %s", exc)

    return evaluacion


@router.get(
    "/mis-evaluaciones",
    response_model=list[EvaluacionSalida],
    dependencies=[Depends(require_role("estudiante"))],
)
async def mis_evaluaciones(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    perfil = await _get_perfil_o_404(current_user, db)
    result = await db.execute(
        select(Evaluacion)
        .where(Evaluacion.estudiante_id == perfil.id)
        .order_by(Evaluacion.corte)
    )
    return result.scalars().all()


@router.get(
    "/{evaluacion_id}",
    response_model=EvaluacionSalida,
    dependencies=[Depends(require_role("estudiante", "docente", "admin"))],
)
async def obtener_evaluacion(
    evaluacion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    result = await db.execute(select(Evaluacion).where(Evaluacion.id == evaluacion_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    if current_user.rol.value == "estudiante":
        perfil = await _get_perfil_o_404(current_user, db)
        if ev.estudiante_id != perfil.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta evaluación")

    return ev


@router.post(
    "/enviar-email/{evaluacion_id}",
    response_model=EnviarEmailResponse,
    dependencies=[Depends(require_role("estudiante"))],
)
async def enviar_email(
    evaluacion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """
    Reenvía manualmente el email con el score y la ruta de aprendizaje de una evaluación.

    Útil si el envío automático de `calcular/{corte}` falló o el estudiante quiere recibirlo de nuevo.
    Requiere SendGrid configurado (`SENDGRID_API_KEY` en `.env`).
    """
    result = await db.execute(select(Evaluacion).where(Evaluacion.id == evaluacion_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    perfil = await _get_perfil_o_404(current_user, db)
    if ev.estudiante_id != perfil.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta evaluación")

    enviado = await enviar_email_evaluacion(current_user, perfil, ev)

    if enviado:
        ev.enviada_email = True
        await db.flush()
        return EnviarEmailResponse(enviado=True, mensaje="Email enviado exitosamente a " + current_user.email)

    return EnviarEmailResponse(enviado=False, mensaje="No se pudo enviar el email. Verifica la configuración de SendGrid.")
