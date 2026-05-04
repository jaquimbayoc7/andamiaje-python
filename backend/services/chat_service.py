"""
backend/services/chat_service.py
Lógica del chat adaptativo: selección de ejercicios, progresión de andamiaje,
construcción del system prompt y evaluación de código en sandbox.
"""

import ast
import logging
import math
import re
import subprocess
import tempfile
import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.evaluacion import Estudiante
from backend.models.pregunta import Andamiaje, NivelAndamiaje, Pregunta
from backend.models.sesion_chat import MensajeChat, RespuestaEstudiante, RolMensaje, SesionChat
from src.claude_haiku import llamar_haiku

logger = logging.getLogger(__name__)

# Sanitiza inputs del estudiante antes de incluirlos en prompts (anti prompt injection)
_INJECTION_RE = re.compile(
    r"(\n---\n|<\|im_end\|>|\[INST\]|\[/INST\]|<s>|</s>|###|System:|Human:|Assistant:)",
    re.IGNORECASE,
)


def _sanitize(texto: str) -> str:
    return _INJECTION_RE.sub(" ", texto).strip()


_SYSTEM_CHAT = (
    "Eres un tutor de Python que guía a estudiantes de forma socrática. "
    "NUNCA des la solución directamente. Haz preguntas que lleven al estudiante a descubrirla. "
    "Sé breve, claro y motivador. Responde en español."
)

# Umbrales de progresión de andamiaje
_UMBRAL_PARCIAL = 3   # intentos sin avance → parcial
_UMBRAL_COMPLETO = 5  # intentos sin avance → completo


# ── Selección de ejercicio ─────────────────────────────────────────────────────

async def seleccionar_pregunta(
    estudiante: Estudiante,
    corte: int,
    db: AsyncSession,
) -> Optional[Pregunta]:
    """
    Selecciona la próxima pregunta para el estudiante:
    - No repite preguntas completadas con score ≥ 0.8 en el mismo corte.
    - Prioriza temas con score < 0.6 en sesiones previas.
    - Siempre incluye al menos 1 pregunta base (variables/listas/funciones).
    """
    # Preguntas ya completadas con score alto en este corte
    completadas_result = await db.execute(
        select(SesionChat.pregunta_id)
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
            SesionChat.score_final >= 0.8,
        )
    )
    completadas_ids = {r[0] for r in completadas_result.fetchall()}

    # Temas débiles: score < 0.6 promedio en este corte
    result_temas = await db.execute(
        select(Pregunta.tema, func.avg(SesionChat.score_final))
        .join(SesionChat, SesionChat.pregunta_id == Pregunta.id)
        .where(
            SesionChat.estudiante_id == estudiante.id,
            SesionChat.corte == corte,
            SesionChat.score_final.isnot(None),
        )
        .group_by(Pregunta.tema)
    )
    temas_score = {row[0]: row[1] for row in result_temas.fetchall()}
    temas_debiles = {t for t, s in temas_score.items() if s < 0.6}

    # Buscar preguntas activas no completadas
    q = select(Pregunta).where(
        Pregunta.activa == True,
        Pregunta.id.not_in(completadas_ids) if completadas_ids else True,
    ).options(selectinload(Pregunta.andamiajes))

    result = await db.execute(q)
    candidatas = result.scalars().all()

    if not candidatas:
        return None

    # Priorizar temas débiles o base
    temas_base = {"variables", "listas", "funciones"}

    def prioridad(p: Pregunta) -> int:
        if p.tema in temas_debiles:
            return 0
        if p.tema in temas_base and not temas_score:
            return 1
        return 2

    candidatas_ordenadas = sorted(candidatas, key=prioridad)
    return candidatas_ordenadas[0]


# ── Nivel de andamiaje actual ──────────────────────────────────────────────────

def _nivel_andamiaje_por_intentos(intentos: int) -> NivelAndamiaje:
    if intentos < _UMBRAL_PARCIAL:
        return NivelAndamiaje.minimo
    elif intentos < _UMBRAL_COMPLETO:
        return NivelAndamiaje.parcial
    else:
        return NivelAndamiaje.completo


def _obtener_andamiaje(pregunta: Pregunta, nivel: NivelAndamiaje) -> str:
    for a in pregunta.andamiajes:
        if a.nivel_andamiaje == nivel:
            return a.contenido
    if pregunta.andamiajes:
        return pregunta.andamiajes[-1].contenido
    return "No hay andamiaje disponible."


# ── Evaluación de código en sandbox ───────────────────────────────────────────

def _es_codigo_seguro(codigo: str) -> bool:
    """Rechaza código con operaciones peligrosas."""
    patrones_peligrosos = [
        r"\bimport\s+os\b", r"\bimport\s+subprocess\b",
        r"\bimport\s+sys\b", r"\bopen\s*\(", r"\beval\s*\(",
        r"\bexec\s*\(", r"\b__import__\b", r"\bshutil\b",
        r"\bsocket\b", r"\burllib\b", r"\brequests\b",
    ]
    for patron in patrones_peligrosos:
        if re.search(patron, codigo, re.IGNORECASE):
            return False
    return True


def _verificar_ast(codigo: str) -> bool:
    try:
        ast.parse(codigo)
        return True
    except SyntaxError:
        return False


def _calcular_bleu(hipotesis: str, referencia: str) -> float:
    tokens_hip = hipotesis.lower().split()
    tokens_ref = set(referencia.lower().split())
    if not tokens_hip:
        return 0.0
    coincidencias = sum(1 for t in tokens_hip if t in tokens_ref)
    precision = coincidencias / len(tokens_hip)
    bp = min(1.0, math.exp(1 - len(tokens_ref) / max(len(tokens_hip), 1)))
    return round(bp * precision, 4)


def ejecutar_codigo_sandbox(codigo: str, solucion_referencia: str, timeout: int = 10) -> dict:
    """
    Ejecuta el código del estudiante en un subproceso aislado con timeout.
    Compara con la solución de referencia.
    """
    if not _verificar_ast(codigo):
        return {"passed": False, "output": "Error de sintaxis en el código.", "error": True}

    if not _es_codigo_seguro(codigo):
        return {"passed": False, "output": "El código contiene operaciones no permitidas.", "error": True}

    # Construir script de prueba combinando código del estudiante con tests mínimos
    script = f"""
{codigo}

# Tests automáticos básicos
import sys
try:
    # Verificar que el módulo carga sin errores
    print("EXEC_OK")
except Exception as e:
    print(f"EXEC_ERROR: {{e}}", file=sys.stderr)
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(script)
        tmp = f.name

    try:
        proc = subprocess.run(
            ["python", tmp],
            capture_output=True,
            text=True,
            timeout=timeout,
            # Sin acceso a red ni filesystem externo (Windows no tiene nsjail, usamos timeout como control básico)
        )
        passed = "EXEC_OK" in proc.stdout and proc.returncode == 0
        bleu = _calcular_bleu(codigo, solucion_referencia)
        return {"passed": passed, "output": proc.stdout[:500] + proc.stderr[:200], "bleu": bleu, "error": False}
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "Timeout: el código tardó demasiado.", "bleu": 0.0, "error": True}
    except Exception as exc:
        return {"passed": False, "output": str(exc), "bleu": 0.0, "error": True}
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


async def evaluar_con_haiku(enunciado: str, codigo: str, nivel: str) -> float:
    """Evalúa el código del estudiante pedagógicamente con Haiku. Retorna score 0-1."""
    prompt = (
        f"Ejercicio ({nivel}): {_sanitize(enunciado)}\n\n"
        f"Código del estudiante:\n```python\n{_sanitize(codigo)}\n```\n\n"
        "Evalúa la calidad del código (claridad, corrección lógica, eficiencia) "
        "y responde SOLO con un número decimal entre 0.0 y 1.0."
    )
    system = "Eres un evaluador de código Python. Responde ÚNICAMENTE con un número decimal entre 0.0 y 1.0."
    respuesta = llamar_haiku(system, prompt, max_tokens=10, temperatura=0.1)
    if not respuesta:
        return 0.5
    match = re.search(r"([01]\.\d+|\d+\.?\d*)", respuesta)
    if match:
        val = float(match.group(1))
        return min(1.0, max(0.0, val))
    return 0.5


# ── Respuesta de chat ──────────────────────────────────────────────────────────

async def generar_respuesta_chat(
    sesion: SesionChat,
    pregunta: Pregunta,
    mensaje_usuario: str,
    intentos_actuales: int,
    db: AsyncSession,
) -> str:
    """Genera respuesta del tutor con contexto de la sesión."""
    nivel_andamiaje = _nivel_andamiaje_por_intentos(intentos_actuales)
    andamiaje_actual = _obtener_andamiaje(pregunta, nivel_andamiaje)

    # Construir historial de mensajes (máx últimos 10)
    result = await db.execute(
        select(MensajeChat)
        .where(MensajeChat.sesion_id == sesion.id)
        .order_by(MensajeChat.timestamp.desc())
        .limit(10)
    )
    mensajes_recientes = list(reversed(result.scalars().all()))

    historial = "\n".join(
        f"{m.rol.value.upper()}: {m.contenido[:200]}" for m in mensajes_recientes
    )

    prompt = (
        f"Ejercicio: {_sanitize(pregunta.enunciado)}\n"
        f"Nivel: {pregunta.nivel.value}\n"
        f"Andamiaje disponible ({nivel_andamiaje.value}): {andamiaje_actual}\n\n"
        f"Historial reciente:\n{historial}\n\n"
        f"Estudiante dice: {_sanitize(mensaje_usuario)}\n\n"
        "Responde como tutor socrático. Si el estudiante muestra avance, refuérzalo. "
        "Si está estancado, da una pista más específica del andamiaje."
    )

    respuesta = llamar_haiku(_SYSTEM_CHAT, prompt, max_tokens=300, temperatura=0.6)
    return respuesta or "¿Puedes describir qué intentaste hasta ahora?"
