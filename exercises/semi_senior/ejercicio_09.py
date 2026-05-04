"""
RETO SEMI-SENIOR #09 — Sets
Tema: Sets
"""

METADATA = {
    "id": "ss_09",
    "nivel_rol": "semi_senior",
    "tema": "sets",
    "enunciado": "Escribe una función `elements_in_exactly_k(sets_list, k)` que retorne un set con todos los elementos que aparecen en EXACTAMENTE k de los sets dados (ni más, ni menos).",
    "andamiaje_minimo": "Necesitas contar en cuántos sets aparece cada elemento, luego filtrar los que aparecen exactamente k veces.",
    "andamiaje_parcial": "Usa `collections.Counter`. Para cada set en la lista, itera sus elementos y cuenta. Luego filtra los que tienen conteo exactamente igual a k.",
    "andamiaje_completo": "Importa `Counter`. Usa `Counter(elem for s in sets_list for elem in s)` para contar apariciones. Luego `{elem for elem, cnt in conteo.items() if cnt == k}`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# elements_in_exactly_k([{1,2}, {2,3}, {3,4}], 1)  → {1, 4}    (aparecen en 1 set)
# elements_in_exactly_k([{1,2}, {2,3}, {3,4}], 2)  → {2, 3}    (aparecen en 2 sets)
# elements_in_exactly_k([], 1)                       → set()
# elements_in_exactly_k([{1}], 2)                   → set()


from collections import Counter


def solucion_referencia(sets_list, k):
    """Solución de referencia (no modificar)."""
    conteo = Counter(elem for s in sets_list for elem in s)
    return {elem for elem, cnt in conteo.items() if cnt == k}


def solucion_estudiante(sets_list, k):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna elementos que aparecen en exactamente k de los sets dados.

    Args:
        sets_list: lista de sets
        k: número exacto de apariciones requerido

    Returns:
        Set de elementos con exactamente k apariciones
    """
    pass
