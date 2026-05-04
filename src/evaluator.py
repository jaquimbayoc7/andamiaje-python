"""
src/evaluator.py
Framework de evaluación que combina métricas técnicas y pedagógicas.
Métricas técnicas: AST válido, BLEU-1, pass@k simulado via pytest.
Métricas pedagógicas: rúbrica 6D evaluada por Claude Haiku.
"""

import ast
import json
import math
import os
import subprocess
import tempfile
import logging
from typing import Optional

from src.claude_haiku import llamar_haiku_json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_EVALUADOR = (
    "Eres un evaluador pedagógico experto en Python para candidatos de entrevistas "
    "técnicas en Colombia. Evalúa la calidad del andamiaje (hint) proporcionado al "
    "candidato según el ejercicio y su perfil.\n\n"
    "Responde ÚNICAMENTE con JSON válido. No incluyas texto fuera del JSON."
)

_PLANTILLA_EVALUACION = """
EJERCICIO: {enunciado}
NIVEL DEL CANDIDATO: {nivel}
ANDAMIAJE PROPORCIONADO: {andamiaje}
NIVEL DE ANDAMIAJE ESPERADO: {nivel_andamiaje}

Evalúa el andamiaje y responde con este JSON exacto:
{{
  "score_total": 0.0,
  "rubrica": {{
    "claridad": 3,
    "progresion": 3,
    "correccion": 3,
    "motivacion": 3,
    "autonomia": 3,
    "eficiencia_algoritmica": 3
  }},
  "nivel_andamiaje_detectado": "parcial",
  "adecuado_para_nivel": true,
  "observaciones": "<máx 2 oraciones en español>"
}}

Reemplaza los valores con tu evaluación real.
"""


# ── Métricas técnicas ─────────────────────────────────────────────────────────

def verificar_ast(codigo: str) -> bool:
    """Verifica que el código Python tenga sintaxis válida."""
    try:
        ast.parse(codigo)
        return True
    except SyntaxError:
        return False


def calcular_bleu_simple(hipotesis: str, referencia: str) -> float:
    """
    BLEU-1 simplificado a nivel de tokens (sin dependencia nltk).
    Para BLEU-4 completo usar nltk.translate.bleu_score.
    """
    tokens_hip = hipotesis.lower().split()
    tokens_ref = set(referencia.lower().split())

    if not tokens_hip:
        return 0.0

    coincidencias = sum(1 for t in tokens_hip if t in tokens_ref)
    precision = coincidencias / len(tokens_hip)
    bp = min(1.0, math.exp(1 - len(tokens_ref) / max(len(tokens_hip), 1)))
    return round(bp * precision, 4)


def ejecutar_tests_pytest(codigo_solucion: str, archivo_test: str) -> dict:
    """
    Ejecuta tests pytest sobre un código solución en entorno temporal aislado.

    Args:
        codigo_solucion: Código Python a evaluar
        archivo_test: Ruta absoluta al archivo de test pytest

    Returns:
        Dict con {passed, failed, total, score, output}
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(codigo_solucion)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", archivo_test, "-v", "--tb=short", "-q"],
            capture_output=True, text=True, timeout=30,
        )
        lineas = proc.stdout.split("\n")
        passed = sum(1 for l in lineas if " PASSED" in l)
        failed = sum(1 for l in lineas if " FAILED" in l or " ERROR" in l)
        total = passed + failed
        return {
            "passed": passed,
            "failed": failed,
            "total": total,
            "score": round(passed / total, 4) if total > 0 else 0.0,
            "output": proc.stdout[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"passed": 0, "failed": 1, "total": 1, "score": 0.0, "output": "Timeout"}
    except Exception as exc:
        return {"passed": 0, "failed": 1, "total": 1, "score": 0.0, "output": str(exc)}
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ── Métricas pedagógicas ──────────────────────────────────────────────────────

def evaluar_andamiaje_haiku(
    enunciado: str,
    nivel: str,
    andamiaje: str,
    nivel_andamiaje: str,
) -> Optional[dict]:
    """
    Evalúa la calidad pedagógica del andamiaje usando Claude Haiku.

    Returns:
        Dict con score_total, rúbrica y observaciones, o None si falla
    """
    prompt = _PLANTILLA_EVALUACION.format(
        enunciado=enunciado,
        nivel=nivel,
        andamiaje=andamiaje,
        nivel_andamiaje=nivel_andamiaje,
    )
    return llamar_haiku_json(SYSTEM_PROMPT_EVALUADOR, prompt, max_tokens=512)


# ── Evaluación completa ───────────────────────────────────────────────────────

def evaluar_ejercicio_completo(
    enunciado: str,
    nivel: str,
    solucion_generada: str,
    solucion_referencia: str,
    andamiaje: str,
    nivel_andamiaje: str,
    archivo_test: Optional[str] = None,
) -> dict:
    """
    Evaluación completa: métricas técnicas + pedagógicas.

    Returns:
        Dict consolidado con todas las métricas y un score_combinado
    """
    resultado = {
        "enunciado_preview": enunciado[:80] + "...",
        "nivel": nivel,
        "nivel_andamiaje": nivel_andamiaje,
        "metricas_tecnicas": {},
        "metricas_pedagogicas": {},
        "score_combinado": 0.0,
    }

    # ── Técnicas ──
    resultado["metricas_tecnicas"]["ast_valido"] = verificar_ast(solucion_generada)
    resultado["metricas_tecnicas"]["bleu_1"] = calcular_bleu_simple(
        solucion_generada, solucion_referencia
    )

    if archivo_test and os.path.exists(archivo_test):
        resultado["metricas_tecnicas"]["pytest"] = ejecutar_tests_pytest(
            solucion_generada, archivo_test
        )
        pass_score = resultado["metricas_tecnicas"]["pytest"]["score"]
    else:
        pass_score = resultado["metricas_tecnicas"]["bleu_1"]

    # ── Pedagógicas ──
    eval_ped = evaluar_andamiaje_haiku(enunciado, nivel, andamiaje, nivel_andamiaje)
    if eval_ped:
        resultado["metricas_pedagogicas"] = eval_ped
        score_ped = float(eval_ped.get("score_total", 0.0))
    else:
        score_ped = 0.0

    resultado["score_combinado"] = round(0.5 * pass_score + 0.5 * score_ped, 4)
    return resultado
