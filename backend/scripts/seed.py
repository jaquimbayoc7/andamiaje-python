"""
backend/scripts/seed.py
Importa los 30 ejercicios de exercises/ como preguntas iniciales en la BD.
Crea: 1 admin, 2 docentes, 3 estudiantes, 2 cursos y las preguntas.

Uso: python -m backend.scripts.seed
"""

import asyncio
import importlib
import inspect
import sys
from pathlib import Path

# Asegura que la raíz del proyecto esté en el path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from backend.core.database import AsyncSessionLocal
from backend.core.security import hash_password
from backend.models.curso import Curso
from backend.models.evaluacion import Estudiante
from backend.models.pregunta import NivelPregunta, Pregunta
from backend.models.usuario import RolUsuario, Usuario

NIVELES = {
    "junior": NivelPregunta.junior,
    "semi_senior": NivelPregunta.semi_senior,
    "senior": NivelPregunta.senior,
}

EJERCICIOS_DIR = ROOT / "exercises"

# ── Datos de seed ─────────────────────────────────────────────────────────────

USUARIOS_SEED = [
    # Admin
    {
        "nombre_completo": "Administrador General",
        "email": "admin@andamiaje.com",
        "password": "Admin1234!",
        "rol": RolUsuario.admin,
    },
    # Docentes
    {
        "nombre_completo": "Carlos Méndez",
        "email": "cmendez@andamiaje.com",
        "password": "Docente1234!",
        "rol": RolUsuario.docente,
    },
    {
        "nombre_completo": "Laura Ríos",
        "email": "lrios@andamiaje.com",
        "password": "Docente1234!",
        "rol": RolUsuario.docente,
    },
    # Estudiantes
    {
        "nombre_completo": "Sofía Herrera",
        "email": "sherrera@andamiaje.com",
        "password": "Estudiante1234!",
        "rol": RolUsuario.estudiante,
    },
    {
        "nombre_completo": "Andrés Mora",
        "email": "amora@andamiaje.com",
        "password": "Estudiante1234!",
        "rol": RolUsuario.estudiante,
    },
    {
        "nombre_completo": "Valeria Castro",
        "email": "vcastro@andamiaje.com",
        "password": "Estudiante1234!",
        "rol": RolUsuario.estudiante,
    },
]

CURSOS_SEED = [
    {"nombre": "Python Fundamentals 2026-1", "docente_email": "cmendez@andamiaje.com", "periodo": "2026-1"},
    {"nombre": "Python Avanzado 2026-1",     "docente_email": "lrios@andamiaje.com",   "periodo": "2026-1"},
]

ESTUDIANTES_SEED = [
    {"email": "sherrera@andamiaje.com", "semestre": 4, "programa": "Ingeniería de Sistemas", "curso": "Python Fundamentals 2026-1"},
    {"email": "amora@andamiaje.com",    "semestre": 6, "programa": "Ingeniería de Sistemas", "curso": "Python Fundamentals 2026-1"},
    {"email": "vcastro@andamiaje.com",  "semestre": 8, "programa": "Ciencia de Datos",       "curso": "Python Avanzado 2026-1"},
]


# ── Carga de ejercicios ───────────────────────────────────────────────────────

def _cargar_ejercicios() -> list[dict]:
    ejercicios = []
    for nivel_dir in ("junior", "semi_senior", "senior"):
        nivel_path = EJERCICIOS_DIR / nivel_dir
        for py_file in sorted(nivel_path.glob("ejercicio_*.py")):
            module_path = f"exercises.{nivel_dir}.{py_file.stem}"
            try:
                mod = importlib.import_module(module_path)
                meta = getattr(mod, "METADATA", None)
                ref_fn = getattr(mod, "solucion_referencia", None)
                if not meta or not ref_fn:
                    continue
                solucion_ref = inspect.getsource(ref_fn)
                ejercicios.append({
                    "titulo": meta.get("enunciado", py_file.stem)[:300],
                    "enunciado": meta.get("enunciado", ""),
                    "solucion_referencia": solucion_ref,
                    "nivel": nivel_dir,
                    "tema": meta.get("tema", "general"),
                })
            except Exception as e:
                print(f"  [!] Error cargando {module_path}: {e}")
    return ejercicios


# ── Seed principal ────────────────────────────────────────────────────────────

async def seed():
    async with AsyncSessionLocal() as db:

        # ── 1. Usuarios ───────────────────────────────────────────────────────
        usuarios_por_email: dict[str, Usuario] = {}
        for datos in USUARIOS_SEED:
            res = await db.execute(select(Usuario).where(Usuario.email == datos["email"]))
            user = res.scalar_one_or_none()
            if not user:
                user = Usuario(
                    nombre_completo=datos["nombre_completo"],
                    email=datos["email"],
                    password_hash=hash_password(datos["password"]),
                    rol=datos["rol"],
                )
                db.add(user)
                await db.flush()
                print(f"  [+] {datos['rol'].value:10s} creado: {datos['email']} / {datos['password']}")
            else:
                print(f"  [=] {datos['rol'].value:10s} ya existe: {datos['email']}")
            usuarios_por_email[datos["email"]] = user

        # ── 2. Cursos ─────────────────────────────────────────────────────────
        cursos_por_nombre: dict[str, Curso] = {}
        for datos in CURSOS_SEED:
            res = await db.execute(select(Curso).where(Curso.nombre == datos["nombre"]))
            curso = res.scalar_one_or_none()
            if not curso:
                docente = usuarios_por_email[datos["docente_email"]]
                curso = Curso(
                    nombre=datos["nombre"],
                    docente_id=docente.id,
                    periodo=datos["periodo"],
                )
                db.add(curso)
                await db.flush()
                print(f"  [+] Curso creado: {datos['nombre']} (docente: {datos['docente_email']})")
            else:
                print(f"  [=] Curso ya existe: {datos['nombre']}")
            cursos_por_nombre[datos["nombre"]] = curso

        # ── 3. Perfiles de estudiante ─────────────────────────────────────────
        for datos in ESTUDIANTES_SEED:
            user = usuarios_por_email[datos["email"]]
            res = await db.execute(select(Estudiante).where(Estudiante.usuario_id == user.id))
            if not res.scalar_one_or_none():
                curso = cursos_por_nombre[datos["curso"]]
                perfil = Estudiante(
                    usuario_id=user.id,
                    semestre=datos["semestre"],
                    programa_academico=datos["programa"],
                    curso_id=curso.id,
                )
                db.add(perfil)
                await db.flush()
                print(f"  [+] Perfil estudiante: {datos['email']} -> {datos['curso']}")
            else:
                print(f"  [=] Perfil ya existe: {datos['email']}")

        # ── 4. Preguntas (desde exercises/) ───────────────────────────────────
        ejercicios = _cargar_ejercicios()
        creados = 0
        for ej in ejercicios:
            existe = await db.execute(select(Pregunta).where(Pregunta.titulo == ej["titulo"]))
            if existe.scalar_one_or_none():
                continue
            pregunta = Pregunta(
                titulo=ej["titulo"],
                enunciado=ej["enunciado"],
                solucion_referencia=ej["solucion_referencia"],
                nivel=NIVELES[ej["nivel"]],
                tema=ej["tema"],
                activa=True,
            )
            db.add(pregunta)
            creados += 1

        await db.commit()
        print(f"  [+] {creados} preguntas creadas ({len(ejercicios)} totales en exercises/)")

    print("\nSeed completado.")
    print("\nCredenciales de acceso:")
    print("  Admin    -> admin@andamiaje.com      / Admin1234!")
    print("  Docente1 -> cmendez@andamiaje.com    / Docente1234!")
    print("  Docente2 -> lrios@andamiaje.com      / Docente1234!")
    print("  Est.1    -> sherrera@andamiaje.com   / Estudiante1234!")
    print("  Est.2    -> amora@andamiaje.com      / Estudiante1234!")
    print("  Est.3    -> vcastro@andamiaje.com    / Estudiante1234!")


if __name__ == "__main__":
    asyncio.run(seed())
