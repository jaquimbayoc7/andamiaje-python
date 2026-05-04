"""
RETO JUNIOR #10 — Listas + Funciones
Tema: Listas y funciones
"""

METADATA = {
    "id": "jr_10",
    "nivel_rol": "junior",
    "tema": "listas",
    "enunciado": "Escribe una función `flatten_one_level(lst)` que aplane una lista exactamente UN nivel. [[1,2],[3,[4]]] → [1,2,3,[4]]. NO aplanes recursivamente los niveles más profundos.",
    "andamiaje_minimo": "Recorre la lista: si un elemento es lista, extiende el resultado con sus elementos; si no, agrégalo directamente.",
    "andamiaje_parcial": "Usa `isinstance(item, list)` para decidir. Si es lista, usa `resultado.extend(item)`; si no, usa `resultado.append(item)`.",
    "andamiaje_completo": "Crea una lista vacía `resultado`. Recorre `lst`: si `isinstance(item, list)`, llama `resultado.extend(item)` (agrega sus elementos, no la sublista). Sino, `resultado.append(item)`. Retorna resultado.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# flatten_one_level([[1, 2], [3, 4]])        → [1, 2, 3, 4]
# flatten_one_level([[1, 2], [3, [4]]])      → [1, 2, 3, [4]]   ← [4] no se aplana
# flatten_one_level([1, [2, 3], 4])          → [1, 2, 3, 4]
# flatten_one_level([])                       → []
# flatten_one_level([[]])                     → []


def solucion_referencia(lst):
    """Solución de referencia (no modificar)."""
    resultado = []
    for item in lst:
        if isinstance(item, list):
            resultado.extend(item)
        else:
            resultado.append(item)
    return resultado


def solucion_estudiante(lst):
    """
    TU SOLUCIÓN AQUÍ.
    Aplana la lista exactamente un nivel. No aplana sublistas anidadas.

    Args:
        lst: lista que puede contener sublistas

    Returns:
        Lista aplanada un nivel
    """
    pass
