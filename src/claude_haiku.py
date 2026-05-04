"""
src/claude_haiku.py
Wrapper para la API de Claude Haiku con:
- Retry exponencial (hasta 3 intentos)
- Rate limiting (máx 5 req/s)
- Anonimización de PII antes de cada llamada
- Sin logging de respuestas en texto plano
"""

import os
import re
import time
import json
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Patrones PII a anonimizar antes de enviar a la API ───────────────────────
_PII_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
    (re.compile(r'\b\d{8,10}\b'), '[CEDULA]'),
    (re.compile(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b'), '[NOMBRE]'),
]

_last_request_times: list = []
_RATE_LIMIT = 5  # máx req/s


def _anonimizar(texto: str) -> str:
    """Elimina PII del texto antes de enviarlo a la API."""
    for patron, reemplazo in _PII_PATTERNS:
        texto = patron.sub(reemplazo, texto)
    return texto


def _respetar_rate_limit() -> None:
    """Garantiza máximo 5 llamadas por segundo."""
    global _last_request_times
    now = time.time()
    _last_request_times = [t for t in _last_request_times if now - t < 1.0]
    if len(_last_request_times) >= _RATE_LIMIT:
        time.sleep(1.0 - (now - _last_request_times[0]) + 0.01)
    _last_request_times.append(time.time())


def llamar_haiku(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    temperatura: float = 0.7,
    max_intentos: int = 3,
) -> Optional[str]:
    """
    Llama a Claude Haiku con retry exponencial.

    Args:
        system_prompt: Instrucciones del sistema
        user_prompt: Mensaje del usuario (se anonimiza automáticamente)
        max_tokens: Máximo de tokens en la respuesta
        temperatura: Temperatura de generación (0.0-1.0)
        max_intentos: Número máximo de reintentos

    Returns:
        Texto de respuesta o None si todos los intentos fallan
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("Instala anthropic: pip install anthropic>=0.25.0")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or not api_key.startswith("sk-ant-"):
        logger.error(
            "ANTHROPIC_API_KEY no configurada o inválida. "
            "Copia .env.example como .env y agrega tu key."
        )
        return None

    client = anthropic.Anthropic(api_key=api_key)
    user_prompt_limpio = _anonimizar(user_prompt)

    for intento in range(max_intentos):
        try:
            _respetar_rate_limit()
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=max_tokens,
                temperature=temperatura,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt_limpio}],
            )
            return response.content[0].text
        except Exception as exc:
            espera = 2 ** intento
            logger.warning(
                "Intento %d/%d falló (%s). Reintentando en %ds...",
                intento + 1, max_intentos, type(exc).__name__, espera,
            )
            if intento < max_intentos - 1:
                time.sleep(espera)
            else:
                logger.error("Todos los intentos fallaron: %s", type(exc).__name__)
                return None
    return None


def llamar_haiku_json(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
) -> Optional[dict]:
    """
    Llama a Claude Haiku y parsea la respuesta como JSON.

    Returns:
        Dict parseado o None si falla
    """
    respuesta = llamar_haiku(
        system_prompt, user_prompt, max_tokens=max_tokens, temperatura=0.3
    )
    if not respuesta:
        return None

    # Extraer JSON si viene envuelto en bloque markdown
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', respuesta, re.DOTALL)
    if match:
        respuesta = match.group(1)

    try:
        return json.loads(respuesta.strip())
    except json.JSONDecodeError:
        pass

    # Intentar extraer el primer objeto JSON válido del texto
    match = re.search(r'\{.*\}', respuesta, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.error("No se pudo parsear la respuesta de Haiku como JSON")
    return None
