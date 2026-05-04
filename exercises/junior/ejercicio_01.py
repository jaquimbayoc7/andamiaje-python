"""
RETO JUNIOR #01 — Variables
Tema: Manejo de variables
"""

METADATA = {
    "id": "jr_01",
    "nivel_rol": "junior",
    "tema": "variables",
    "enunciado": "Escribe una función `swap(a, b)` que intercambie dos variables SIN usar una variable temporal. Debe funcionar con cualquier tipo de dato.",
    "andamiaje_minimo": "Python permite asignar múltiples variables en una sola línea.",
    "andamiaje_parcial": "Usa la asignación múltiple: `a, b = expresion`. Python evalúa el lado derecho antes de asignar.",
    "andamiaje_completo": "Escribe `a, b = b, a` — Python empaqueta el lado derecho como tupla y luego desempaqueta. Retorna la tupla `(a, b)` al final.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# swap(1, 2)        → (2, 1)
# swap("x", "y")   → ("y", "x")
# swap([1], [2])    → ([2], [1])
# swap(5, 5)        → (5, 5)


def solucion_referencia(a, b):
    """Solución de referencia (no modificar)."""
    a, b = b, a
    return a, b


def solucion_estudiante(a, b):
    """
    TU SOLUCIÓN AQUÍ.
    Intercambia a y b sin variable temporal.

    Args:
        a: primer valor (cualquier tipo)
        b: segundo valor (cualquier tipo)

    Returns:
        Tupla (b_original, a_original)
    """
    pass
