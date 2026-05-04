"""
RETO JUNIOR #04 — Tuplas
Tema: Manejo de tuplas
"""

METADATA = {
    "id": "jr_04",
    "nivel_rol": "junior",
    "tema": "tuplas",
    "enunciado": "Escribe una función `unpack_nested(t)` que reciba una tupla anidada ((a, b), (c, d)) y retorne los cuatro valores en una sola línea de desempaquetado.",
    "andamiaje_minimo": "Python permite desempaquetar estructuras anidadas en una sola asignación.",
    "andamiaje_parcial": "Puedes escribir `(a, b), (c, d) = t` para desempaquetar ambas tuplas internas a la vez.",
    "andamiaje_completo": "Usa `(a, b), (c, d) = t` en una sola línea dentro de la función, luego retorna `(a, b, c, d)`. Python desempaqueta recursivamente la estructura anidada.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# unpack_nested(((1, 2), (3, 4)))        → (1, 2, 3, 4)
# unpack_nested((("a", "b"), ("c", "d"))) → ("a", "b", "c", "d")
# unpack_nested(((True, 0), (None, 1)))  → (True, 0, None, 1)


def solucion_referencia(t):
    """Solución de referencia (no modificar)."""
    (a, b), (c, d) = t
    return a, b, c, d


def solucion_estudiante(t):
    """
    TU SOLUCIÓN AQUÍ.
    Desempaqueta ((a,b),(c,d)) en cuatro variables en una línea.

    Args:
        t: tupla anidada con estructura ((a, b), (c, d))

    Returns:
        Tupla plana (a, b, c, d)
    """
    pass
