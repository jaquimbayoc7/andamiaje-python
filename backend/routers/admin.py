"""
backend/routers/admin.py
Endpoints de administración: gestión de usuarios, cursos y alertas.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user, hash_password, require_role
from backend.models.curso import Curso
from backend.models.evaluacion import Estudiante
from backend.models.prediccion_riesgo import PrediccionRiesgo
from backend.models.usuario import RolUsuario, Usuario
from backend.schemas.auth import UsuarioPublico
from backend.services.email_service import enviar_alerta_docente

router = APIRouter()


# ── Schemas locales ───────────────────────────────────────────────────────────

class CrearUsuarioAdmin(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    rol: str = "estudiante"


class ActualizarUsuario(BaseModel):
    nombre_completo: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None


class AsignarCurso(BaseModel):
    curso_id: int


class CrearCurso(BaseModel):
    nombre: str
    docente_id: int
    periodo: str


# ── Usuarios ──────────────────────────────────────────────────────────────────

@router.get(
    "/usuarios",
    response_model=list[UsuarioPublico],
    dependencies=[Depends(require_role("admin"))],
)
async def listar_usuarios(
    db: Annotated[AsyncSession, Depends(get_db)],
    rol: Optional[str] = None,
):
    q = select(Usuario)
    if rol:
        try:
            q = q.where(Usuario.rol == RolUsuario(rol))
        except ValueError:
            raise HTTPException(status_code=400, detail="Rol inválido")
    result = await db.execute(q.order_by(Usuario.created_at.desc()))
    return result.scalars().all()


@router.post(
    "/usuarios",
    response_model=UsuarioPublico,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def crear_usuario(
    body: CrearUsuarioAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing = await db.execute(select(Usuario).where(Usuario.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email ya registrado")

    try:
        rol = RolUsuario(body.rol)
    except ValueError:
        raise HTTPException(status_code=400, detail="Rol inválido")

    user = Usuario(
        nombre_completo=body.nombre_completo,
        email=body.email,
        password_hash=hash_password(body.password),
        rol=rol,
    )
    db.add(user)
    await db.flush()
    return user


@router.patch(
    "/usuarios/{usuario_id}",
    response_model=UsuarioPublico,
    dependencies=[Depends(require_role("admin"))],
)
async def actualizar_usuario(
    usuario_id: int,
    body: ActualizarUsuario,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if body.nombre_completo:
        user.nombre_completo = body.nombre_completo
    if body.rol:
        try:
            user.rol = RolUsuario(body.rol)
        except ValueError:
            raise HTTPException(status_code=400, detail="Rol inválido")
    if body.activo is not None:
        user.activo = body.activo

    await db.flush()
    return user


@router.get(
    "/estudiantes",
    dependencies=[Depends(require_role("admin", "docente"))],
)
async def listar_estudiantes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    curso_id: Optional[int] = None,
):
    """
    Lista estudiantes con su perfil y curso asignado.

    - **admin**: ve todos los estudiantes. Filtrable por `?curso_id=`.
    - **docente**: ve solo sus estudiantes (de sus cursos) más los que no tienen curso asignado.

    Retorna: `estudiante_id`, `usuario_id`, `nombre_completo`, `email`, `semestre`,
    `programa_academico`, `curso_id`, `curso_nombre` (o `"Sin asignar"`).
    """
    q = (
        select(
            Estudiante.id,
            Estudiante.usuario_id,
            Estudiante.semestre,
            Estudiante.programa_academico,
            Estudiante.curso_id,
            Usuario.nombre_completo,
            Usuario.email,
            Curso.nombre.label("curso_nombre"),
        )
        .join(Usuario, Usuario.id == Estudiante.usuario_id)
        .outerjoin(Curso, Curso.id == Estudiante.curso_id)
    )

    if current_user.rol.value == "docente":
        # Cursos propios del docente
        cursos_result = await db.execute(
            select(Curso.id).where(Curso.docente_id == current_user.id)
        )
        mis_cursos_ids = [r[0] for r in cursos_result.fetchall()]
        # Ver sus estudiantes + los sin curso asignado
        from sqlalchemy import or_
        q = q.where(
            or_(
                Estudiante.curso_id.in_(mis_cursos_ids),
                Estudiante.curso_id.is_(None),
            )
        )
    elif curso_id:
        q = q.where(Estudiante.curso_id == curso_id)

    result = await db.execute(q.order_by(Curso.nombre.nullslast(), Usuario.nombre_completo))
    rows = result.mappings().all()
    return [
        {
            "estudiante_id": r["id"],
            "usuario_id": r["usuario_id"],
            "nombre_completo": r["nombre_completo"],
            "email": r["email"],
            "semestre": r["semestre"],
            "programa_academico": r["programa_academico"],
            "curso_id": r["curso_id"],
            "curso_nombre": r["curso_nombre"] or "Sin asignar",
        }
        for r in rows
    ]


@router.post(
    "/usuarios/{usuario_id}/asignar-curso",
    dependencies=[Depends(require_role("admin", "docente"))],
)
async def asignar_curso_estudiante(
    usuario_id: int,
    body: AsignarCurso,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """
    Asigna un curso a un estudiante (por su `usuario_id`).

    - **admin**: puede asignar a cualquier curso.
    - **docente**: solo puede asignar a sus propios cursos (devuelve 403 si intenta otro).

    Body: `{ "curso_id": <int> }`
    """
    result = await db.execute(select(Estudiante).where(Estudiante.usuario_id == usuario_id))
    perfil = result.scalar_one_or_none()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de estudiante no encontrado")

    # Verificar que el curso existe
    result_c = await db.execute(select(Curso).where(Curso.id == body.curso_id))
    curso = result_c.scalar_one_or_none()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    # Docente solo puede asignar a sus propios cursos
    if current_user.rol.value == "docente" and curso.docente_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo puedes asignar estudiantes a tus propios cursos")

    perfil.curso_id = body.curso_id
    await db.flush()
    return {"mensaje": "Curso asignado exitosamente"}


# ── Cursos ────────────────────────────────────────────────────────────────────

@router.get(
    "/cursos",
    dependencies=[Depends(require_role("admin", "docente"))],
)
async def listar_cursos(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    q = select(Curso)
    if current_user.rol.value == "docente":
        q = q.where(Curso.docente_id == current_user.id)
    result = await db.execute(q.order_by(Curso.id))
    cursos = result.scalars().all()
    return [
        {"id": c.id, "nombre": c.nombre, "periodo": c.periodo, "activo": c.activo, "docente_id": c.docente_id}
        for c in cursos
    ]


@router.post(
    "/cursos",
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def crear_curso(
    body: CrearCurso,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Verificar que el docente existe
    result = await db.execute(
        select(Usuario).where(Usuario.id == body.docente_id, Usuario.rol == RolUsuario.docente)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Docente no encontrado")

    curso = Curso(nombre=body.nombre, docente_id=body.docente_id, periodo=body.periodo)
    db.add(curso)
    await db.flush()
    return {"id": curso.id, "nombre": curso.nombre, "periodo": curso.periodo}


# ── Alertas ───────────────────────────────────────────────────────────────────

@router.post(
    "/alertas/notificar/{prediccion_id}",
    dependencies=[Depends(require_role("admin", "docente"))],
)
async def notificar_docente(
    prediccion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Envía alerta al docente sobre un estudiante en riesgo."""
    result = await db.execute(
        select(PrediccionRiesgo).where(PrediccionRiesgo.id == prediccion_id)
    )
    pred = result.scalar_one_or_none()
    if not pred:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    # Cargar datos del estudiante y docente
    result_est = await db.execute(select(Estudiante).where(Estudiante.id == pred.estudiante_id))
    estudiante = result_est.scalar_one()

    result_usr = await db.execute(select(Usuario).where(Usuario.id == estudiante.usuario_id))
    usuario_est = result_usr.scalar_one()

    result_curso = await db.execute(select(Curso).where(Curso.id == pred.curso_id))
    curso = result_curso.scalar_one_or_none()

    result_doc = await db.execute(
        select(Usuario).where(Usuario.id == (curso.docente_id if curso else None))
    )
    docente = result_doc.scalar_one_or_none()

    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")

    temas_debiles = [t.get("tema", "") for t in (pred.temas_debiles or [])]
    enviado = await enviar_alerta_docente(
        docente=docente,
        estudiante_nombre=usuario_est.nombre_completo,
        temas_debiles=temas_debiles,
        score_actual=pred.score_riesgo,
        curso_nombre=curso.nombre if curso else "Sin curso",
    )

    if enviado:
        pred.notificado_docente = True
        await db.flush()

    return {"enviado": enviado, "docente_email": docente.email}
