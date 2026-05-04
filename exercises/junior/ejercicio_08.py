"""
RETO JUNIOR #08 — Sets
Tema: Manejo de sets
"""

METADATA = {
    "id": "jr_08",
    "nivel_rol": "junior",
    "tema": "sets",
    "enunciado": "Escribe una función `words_only_in_a(text_a, text_b)` que retorne el conjunto de palabras que aparecen en text_a pero NO en text_b (sin distinguir mayúsculas/minúsculas).",
    "andamiaje_minimo": "Los sets tienen un operador para calcular la diferencia entre dos conjuntos.",
    "andamiaje_parcial": "Convierte cada texto en un set de palabras en minúsculas con `.lower().split()`. Luego usa el operador `-` para la diferencia.",
    "andamiaje_completo": "Crea `palabras_a = set(text_a.lower().split())` y `palabras_b = set(text_b.lower().split())`. Retorna `palabras_a - palabras_b`. El operador `-` entre sets da los elementos del primero que no están en el segundo.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# words_only_in_a("hello world foo", "world bar") → {"hello", "foo"}
# words_only_in_a("a b c", "a b c")               → set()
# words_only_in_a("Python is great", "Java is ok") → {"python", "great"}
# words_only_in_a("", "hello")                      → set()


def solucion_referencia(text_a, text_b):
    """Solución de referencia (no modificar)."""
    palabras_a = set(text_a.lower().split())
    palabras_b = set(text_b.lower().split())
    return palabras_a - palabras_b


def solucion_estudiante(text_a, text_b):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna palabras que aparecen en text_a pero no en text_b (sin distinción de mayúsculas).

    Args:
        text_a: primer texto
        text_b: segundo texto

    Returns:
        Set de palabras exclusivas de text_a
    """
    pass
