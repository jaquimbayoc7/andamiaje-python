"""
RETO JUNIOR #03 — Listas
Tema: Manejo de listas
"""

METADATA = {
    "id": "jr_03",
    "nivel_rol": "junior",
    "tema": "listas",
    "enunciado": "Escribe una función `second_largest(lst)` que retorne el segundo elemento más grande SIN usar sort() ni sorted(). Retorna None si no existe.",
    "andamiaje_minimo": "Puedes encontrar el segundo mayor recorriendo la lista una o dos veces, rastreando los dos mayores.",
    "andamiaje_parcial": "Mantén dos variables: `primero` y `segundo`, inicializadas con -infinito. Actualiza ambas mientras recorres la lista.",
    "andamiaje_completo": "Inicializa `primero = segundo = float('-inf')`. Si `n > primero`, actualiza ambos. Si `primero > n > segundo`, actualiza solo `segundo`. Retorna `segundo` si no es -inf, sino None.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# second_largest([3, 1, 4, 1, 5, 9])  → 5
# second_largest([1, 1])               → None
# second_largest([5])                  → None
# second_largest([-1, -3, -2])         → -2


def solucion_referencia(lst):
    """Solución de referencia (no modificar)."""
    if len(lst) < 2:
        return None
    primero = segundo = float("-inf")
    for n in lst:
        if n > primero:
            segundo = primero
            primero = n
        elif n > segundo and n != primero:
            segundo = n
    return segundo if segundo != float("-inf") else None


def solucion_estudiante(lst):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna el segundo mayor elemento sin sort()/sorted().

    Args:
        lst: lista de números

    Returns:
        Segundo mayor número, o None si no existe
    """
    pass
