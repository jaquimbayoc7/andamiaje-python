"""
RETO JUNIOR #02 — Listas
Tema: Manejo de listas
"""

METADATA = {
    "id": "jr_02",
    "nivel_rol": "junior",
    "tema": "listas",
    "enunciado": "Escribe una función `remove_duplicates(lst)` que elimine los elementos duplicados de una lista CONSERVANDO el orden original, SIN usar set().",
    "andamiaje_minimo": "Necesitas recordar qué elementos ya has visto mientras recorres la lista.",
    "andamiaje_parcial": "Usa una lista auxiliar para registrar los elementos vistos. Para cada elemento, agrégalo al resultado solo si no lo has visto antes.",
    "andamiaje_completo": "Recorre la lista con un for. Mantén una lista `vistos`. Si el elemento no está en `vistos`, agrégalo tanto a `vistos` como al resultado final.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# remove_duplicates([1, 2, 2, 3, 1])    → [1, 2, 3]
# remove_duplicates(["a", "b", "a"])    → ["a", "b"]
# remove_duplicates([])                  → []
# remove_duplicates([5, 5, 5])           → [5]


def solucion_referencia(lst):
    """Solución de referencia (no modificar)."""
    vistos = []
    resultado = []
    for item in lst:
        if item not in vistos:
            vistos.append(item)
            resultado.append(item)
    return resultado


def solucion_estudiante(lst):
    """
    TU SOLUCIÓN AQUÍ.
    Elimina duplicados preservando el orden. No usar set().

    Args:
        lst: lista de elementos

    Returns:
        Nueva lista sin duplicados, en el mismo orden de aparición
    """
    pass
