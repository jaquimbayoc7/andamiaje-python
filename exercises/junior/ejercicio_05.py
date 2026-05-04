"""
RETO JUNIOR #05 — Tuplas
Tema: Manejo de tuplas
"""

METADATA = {
    "id": "jr_05",
    "nivel_rol": "junior",
    "tema": "tuplas",
    "enunciado": "Escribe una función `count_in_nested(data, value)` que cuente cuántas veces aparece `value` en todas las tuplas internas de una tupla de tuplas.",
    "andamiaje_minimo": "Las tuplas tienen un método `.count()` para contar ocurrencias.",
    "andamiaje_parcial": "Itera sobre las tuplas internas y usa `.count(valor)` en cada una. Suma los resultados.",
    "andamiaje_completo": "Usa un generador: `sum(t.count(value) for t in data)`. Esto recorre cada tupla interna y cuenta cuántas veces aparece `value` en ella, sumando todo.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# count_in_nested(((1, 2, 1), (3, 1)), 1)       → 3
# count_in_nested(((1, 2), (3, 4)), 5)           → 0
# count_in_nested((("a", "a"), ("a",)), "a")     → 3
# count_in_nested((), 1)                          → 0


def solucion_referencia(data, value):
    """Solución de referencia (no modificar)."""
    return sum(t.count(value) for t in data)


def solucion_estudiante(data, value):
    """
    TU SOLUCIÓN AQUÍ.
    Cuenta cuántas veces aparece `value` en todas las tuplas internas.

    Args:
        data: tupla de tuplas
        value: valor a buscar

    Returns:
        Entero con el total de ocurrencias
    """
    pass
