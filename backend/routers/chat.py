"""
backend/routers/chat.py
Endpoints del chat adaptativo para estudiantes.
Rate limiting: 5 req/min en evaluar-codigo.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database import get_db
from backend.core.security import get_current_user, require_role
from backend.models.evaluacion import Estudiante
from backend.models.curso import Curso
from backend.models.pregunta import NivelAndamiaje, Pregunta
from backend.models.sesion_chat import MensajeChat, RespuestaEstudiante, RolMensaje, SesionChat
from backend.models.usuario import Usuario
from backend.schemas.chat import (
    EvaluarCodigoRequest,
    EvaluarCodigoResponse,
    IniciarSesionRequest,
    IniciarSesionResponse,
    MensajeRequest,
    MensajeResponse,
    SesionDetalle,
)
from backend.services.chat_service import (
    _nivel_andamiaje_por_intentos,
    _obtener_andamiaje,
    evaluar_con_haiku,
    ejecutar_codigo_sandbox,
    generar_respuesta_chat,
    seleccionar_pregunta,
)

router = APIRouter()

# Rate limiting simple para evaluar-codigo (5 req/min por estudiante)
_eval_attempts: dict[int, list[float]] = {}


def _check_eval_rate_limit(user_id: int) -> None:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).timestamp()
    attempts = [t for t in _eval_attempts.get(user_id, []) if now - t < 60]
    if len(attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Límite de evaluaciones: máximo 5 por minuto.",
        )
    attempts.append(now)
    _eval_attempts[user_id] = attempts


async def _get_perfil_estudiante(user: Usuario, db: AsyncSession) -> Estudiante:
    result = await db.execute(select(Estudiante).where(Estudiante.usuario_id == user.id))
    perfil = result.scalar_one_or_none()
    if not perfil:
        # Asignar el primer curso disponible en la BD
        curso_result = await db.execute(select(Curso.id).limit(1))
        curso_id = curso_result.scalar_one_or_none()
        # Auto-crear perfil para usuarios registrados nuevos
        perfil = Estudiante(
            usuario_id=user.id,
            semestre=1,
            programa_academico="Sin especificar",
            curso_id=curso_id,
        )
        db.add(perfil)
        await db.flush()
    return perfil


@router.post(
    "/iniciar",
    response_model=IniciarSesionResponse,
    dependencies=[Depends(require_role("estudiante"))],
)
async def iniciar_sesion(
    body: IniciarSesionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Inicia una nueva sesión de chat seleccionando la próxima pregunta."""
    if body.corte not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Corte debe ser 1, 2 o 3")

    perfil = await _get_perfil_estudiante(current_user, db)
    pregunta = await seleccionar_pregunta(perfil, body.corte, db)

    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay más preguntas disponibles para este corte. ¡Excelente trabajo!",
        )

    sesion = SesionChat(
        estudiante_id=perfil.id,
        pregunta_id=pregunta.id,
        corte=body.corte,
    )
    db.add(sesion)
    await db.flush()

    andamiaje_inicial = _obtener_andamiaje(pregunta, NivelAndamiaje.minimo)
    bienvenida = (
        f"¡Hola {current_user.nombre_completo.split()[0]}! "
        f"Trabajaremos en el ejercicio de **{pregunta.tema}**. "
        "Léelo con cuidado y dime: ¿qué enfoque se te ocurre para resolverlo?"
    )

    # Guardar mensaje de bienvenida
    msg = MensajeChat(
        sesion_id=sesion.id,
        rol=RolMensaje.assistant,
        contenido=bienvenida,
    )
    db.add(msg)
    await db.flush()

    return IniciarSesionResponse(
        sesion_id=sesion.id,
        pregunta_id=pregunta.id,
        titulo=pregunta.titulo,
        enunciado=pregunta.enunciado,
        nivel_andamiaje_actual=NivelAndamiaje.minimo.value,
        andamiaje=andamiaje_inicial,
        mensaje_bienvenida=bienvenida,
    )


@router.post(
    "/mensaje",
    response_model=MensajeResponse,
    dependencies=[Depends(require_role("estudiante"))],
)
async def enviar_mensaje(
    body: MensajeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Envía un mensaje al tutor y recibe respuesta."""
    result = await db.execute(
        select(SesionChat)
        .where(SesionChat.id == body.sesion_id)
        .options(selectinload(SesionChat.estudiante))
    )
    sesion = result.scalar_one_or_none()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    perfil = await _get_perfil_estudiante(current_user, db)
    if sesion.estudiante_id != perfil.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")

    if sesion.ended_at:
        raise HTTPException(status_code=400, detail="Esta sesión ya terminó")

    # Contar intentos de código en esta sesión
    result_intentos = await db.execute(
        select(RespuestaEstudiante).where(RespuestaEstudiante.sesion_id == sesion.id)
    )
    intentos = len(result_intentos.scalars().all())

    # Cargar pregunta
    result_preg = await db.execute(
        select(Pregunta)
        .where(Pregunta.id == sesion.pregunta_id)
        .options(selectinload(Pregunta.andamiajes))
    )
    pregunta = result_preg.scalar_one()

    # Guardar mensaje del usuario
    msg_user = MensajeChat(
        sesion_id=sesion.id,
        rol=RolMensaje.user,
        contenido=body.contenido[:2000],
    )
    db.add(msg_user)
    await db.flush()

    # Generar respuesta del tutor
    respuesta = await generar_respuesta_chat(sesion, pregunta, body.contenido, intentos, db)

    msg_asst = MensajeChat(
        sesion_id=sesion.id,
        rol=RolMensaje.assistant,
        contenido=respuesta,
    )
    db.add(msg_asst)
    await db.flush()

    nivel_andamiaje = _nivel_andamiaje_por_intentos(intentos)

    return MensajeResponse(
        rol="assistant",
        contenido=respuesta,
        nivel_andamiaje_actual=nivel_andamiaje.value,
        timestamp=msg_asst.timestamp,
    )


@router.post(
    "/evaluar-codigo",
    response_model=EvaluarCodigoResponse,
    dependencies=[Depends(require_role("estudiante"))],
)
async def evaluar_codigo(
    body: EvaluarCodigoRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Evalúa el código enviado por el estudiante."""
    _check_eval_rate_limit(current_user.id)

    result = await db.execute(
        select(SesionChat).where(SesionChat.id == body.sesion_id)
    )
    sesion = result.scalar_one_or_none()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    perfil = await _get_perfil_estudiante(current_user, db)
    if sesion.estudiante_id != perfil.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")

    if sesion.ended_at:
        raise HTTPException(status_code=400, detail="Esta sesión ya terminó")

    # Contar intentos previos
    result_prev = await db.execute(
        select(RespuestaEstudiante).where(RespuestaEstudiante.sesion_id == sesion.id)
    )
    respuestas_previas = result_prev.scalars().all()
    intentos = len(respuestas_previas) + 1

    # Cargar pregunta
    result_preg = await db.execute(
        select(Pregunta)
        .where(Pregunta.id == sesion.pregunta_id)
        .options(selectinload(Pregunta.andamiajes))
    )
    pregunta = result_preg.scalar_one()

    # Ejecutar en sandbox
    sandbox_result = ejecutar_codigo_sandbox(body.codigo, pregunta.solucion_referencia)
    passed = sandbox_result["passed"]
    bleu = sandbox_result.get("bleu", 0.0)
    haiku_score = await evaluar_con_haiku(pregunta.enunciado, body.codigo, pregunta.nivel.value)

    # Guardar respuesta
    respuesta_est = RespuestaEstudiante(
        sesion_id=sesion.id,
        pregunta_id=pregunta.id,
        codigo_enviado=body.codigo[:5000],
        passed_tests=passed,
        bleu_score=bleu,
        haiku_score=haiku_score,
        intentos=intentos,
    )
    db.add(respuesta_est)

    # Score parcial
    eficiencia = max(0.0, 1.0 - (intentos - 1) * 0.1)
    score_parcial = (
        (1.0 if passed else 0.0) * 0.40
        + haiku_score * 0.30
        + bleu * 0.20
        + eficiencia * 0.10
    )
    score_parcial = round(score_parcial, 4)

    # Determinar nivel de andamiaje
    nivel_andamiaje = _nivel_andamiaje_por_intentos(intentos)
    andamiaje_txt = _obtener_andamiaje(pregunta, nivel_andamiaje)

    # Feedback del tutor
    if passed and score_parcial >= 0.7:
        feedback = f"¡Excelente! Tu código pasa las pruebas con un score de {score_parcial:.0%}. ¡Bien hecho!"
        sesion.score_final = score_parcial
        sesion.ended_at = datetime.now(timezone.utc)
        sesion_completada = True
    elif passed:
        feedback = f"El código funciona (score: {score_parcial:.0%}). Puedes mejorarlo aún más o continuar."
        sesion_completada = False
    else:
        feedback = sandbox_result.get("output", "El código no superó todas las pruebas. Revisa la lógica.")
        sesion_completada = False

    await db.flush()

    return EvaluarCodigoResponse(
        passed_tests=passed,
        bleu_score=bleu,
        haiku_score=haiku_score,
        intentos=intentos,
        score_parcial=score_parcial,
        feedback=feedback,
        nivel_andamiaje_actual=nivel_andamiaje.value,
        andamiaje_actualizado=andamiaje_txt if not passed else None,
        sesion_completada=sesion_completada,
    )


@router.get(
    "/sesion/{sesion_id}",
    response_model=SesionDetalle,
    dependencies=[Depends(require_role("estudiante", "docente", "admin"))],
)
async def obtener_sesion(
    sesion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    result = await db.execute(
        select(SesionChat)
        .where(SesionChat.id == sesion_id)
        .options(selectinload(SesionChat.mensajes))
    )
    sesion = result.scalar_one_or_none()
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    # Estudiantes solo ven su propia sesión
    if current_user.rol.value == "estudiante":
        perfil = await _get_perfil_estudiante(current_user, db)
        if sesion.estudiante_id != perfil.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta sesión")

    return sesion
