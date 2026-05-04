"""
backend/routers/preguntas.py
CRUD de preguntas para docentes y admins.
"""

import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database import get_db
from backend.core.security import get_current_user, require_role
from backend.models.pregunta import NivelPregunta, Pregunta
from backend.models.usuario import Usuario
from backend.schemas.preguntas import (
    ImportarCSVResultado,
    PreguntaActualizar,
    PreguntaCrear,
    PreguntaResumen,
    PreguntaSalida,
)
from backend.services.andamiaje_service import generar_andamiajes

router = APIRouter()


async def _get_pregunta_o_404(pregunta_id: int, db: AsyncSession) -> Pregunta:
    result = await db.execute(
        select(Pregunta)
        .where(Pregunta.id == pregunta_id)
        .options(selectinload(Pregunta.andamiajes))
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return p


@router.get("/", response_model=list[PreguntaResumen])
async def listar_preguntas(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    nivel: str | None = None,
    tema: str | None = None,
    solo_activas: bool = True,
):
    """Lista preguntas. Docente ve solo las suyas + las del sistema; admin ve todas."""
    q = select(Pregunta)
    if solo_activas:
        q = q.where(Pregunta.activa == True)
    if nivel:
        try:
            q = q.where(Pregunta.nivel == NivelPregunta(nivel))
        except ValueError:
            raise HTTPException(status_code=400, detail="Nivel inválido")
    if tema:
        q = q.where(Pregunta.tema.ilike(f"%{tema}%"))
    if current_user.rol.value == "docente":
        q = q.where(
            (Pregunta.docente_id == current_user.id) | (Pregunta.docente_id == None)
        )
    result = await db.execute(q.order_by(Pregunta.created_at.desc()))
    return result.scalars().all()


@router.post(
    "/",
    response_model=PreguntaSalida,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("docente", "admin"))],
)
async def crear_pregunta(
    body: PreguntaCrear,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Crea pregunta y genera los 3 andamiajes con Haiku."""
    pregunta = Pregunta(
        titulo=body.titulo,
        enunciado=body.enunciado,
        solucion_referencia=body.solucion_referencia,
        nivel=NivelPregunta(body.nivel),
        tema=body.tema,
        docente_id=current_user.id,
    )
    db.add(pregunta)
    await db.flush()

    await generar_andamiajes(pregunta, db)
    await db.refresh(pregunta, attribute_names=["andamiajes"])
    return pregunta


@router.get("/{pregunta_id}", response_model=PreguntaSalida)
async def obtener_pregunta(
    pregunta_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    return await _get_pregunta_o_404(pregunta_id, db)


@router.patch(
    "/{pregunta_id}",
    response_model=PreguntaSalida,
    dependencies=[Depends(require_role("docente", "admin"))],
)
async def actualizar_pregunta(
    pregunta_id: int,
    body: PreguntaActualizar,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    pregunta = await _get_pregunta_o_404(pregunta_id, db)
    if current_user.rol.value == "docente" and pregunta.docente_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes editar esta pregunta")

    for campo, valor in body.model_dump(exclude_unset=True).items():
        if campo == "nivel" and valor:
            setattr(pregunta, campo, NivelPregunta(valor))
        else:
            setattr(pregunta, campo, valor)

    await db.flush()
    await db.refresh(pregunta, attribute_names=["andamiajes"])
    return pregunta


@router.delete(
    "/{pregunta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("docente", "admin"))],
)
async def eliminar_pregunta(
    pregunta_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    pregunta = await _get_pregunta_o_404(pregunta_id, db)
    if current_user.rol.value == "docente" and pregunta.docente_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes eliminar esta pregunta")
    await db.delete(pregunta)


@router.post(
    "/importar-csv",
    response_model=ImportarCSVResultado,
    dependencies=[Depends(require_role("docente", "admin"))],
)
async def importar_csv(
    archivo: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    generar_andamiaje: bool = True,
):
    """
    Importa preguntas desde CSV.
    Columnas: titulo,enunciado,solucion_referencia,nivel,tema
    """
    contenido = await archivo.read()
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = contenido.decode("latin-1")

    reader = csv.DictReader(io.StringIO(texto))
    creadas = 0
    errores: list[str] = []
    campos_requeridos = {"titulo", "enunciado", "solucion_referencia", "nivel", "tema"}

    for i, fila in enumerate(reader, start=2):  # fila 1 = header
        if not campos_requeridos.issubset(set(fila.keys())):
            errores.append(f"Fila {i}: faltan columnas requeridas")
            continue
        try:
            nivel = NivelPregunta(fila["nivel"].strip().lower())
        except ValueError:
            errores.append(f"Fila {i}: nivel inválido '{fila['nivel']}'")
            continue

        pregunta = Pregunta(
            titulo=fila["titulo"].strip()[:300],
            enunciado=fila["enunciado"].strip(),
            solucion_referencia=fila["solucion_referencia"].strip(),
            nivel=nivel,
            tema=fila["tema"].strip()[:100],
            docente_id=current_user.id,
        )
        db.add(pregunta)
        await db.flush()

        if generar_andamiaje:
            await generar_andamiajes(pregunta, db)

        creadas += 1

    return ImportarCSVResultado(creadas=creadas, errores=errores)
