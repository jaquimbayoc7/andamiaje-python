"""
RETO JUNIOR #09 — Funciones
Tema: Manejo de funciones
"""

METADATA = {
    "id": "jr_09",
    "nivel_rol": "junior",
    "tema": "funciones",
    "enunciado": "Escribe una función `sum_numerics(*args)` que acepte cualquier cantidad de argumentos de tipos mixtos y retorne la suma solo de los numéricos (int o float). Ignora strings, booleanos, None, etc.",
    "andamiaje_minimo": "Puedes filtrar los argumentos usando `isinstance()` para verificar el tipo.",
    "andamiaje_parcial": "Usa `isinstance(x, (int, float))` para identificar numéricos. Cuidado: `bool` es subclase de `int` en Python, exclúyelo si es necesario.",
    "andamiaje_completo": "Usa `sum(x for x in args if isinstance(x, (int, float)) and not isinstance(x, bool))` para sumar solo los enteros y flotantes, excluyendo booleanos.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# sum_numerics(1, 2, 3)               → 6
# sum_numerics(1, "hello", 2.5, None) → 3.5
# sum_numerics()                       → 0
# sum_numerics(True, 1, 2)            → 3  (True excluido)
# sum_numerics("a", "b")              → 0


def solucion_referencia(*args):
    """Solución de referencia (no modificar)."""
    return sum(x for x in args if isinstance(x, (int, float)) and not isinstance(x, bool))


def solucion_estudiante(*args):
    """
    TU SOLUCIÓN AQUÍ.
    Suma solo los argumentos numéricos (int, float), ignorando el resto.

    Args:
        *args: argumentos mixtos de cualquier tipo

    Returns:
        Suma de los valores numéricos
    """
    pass
