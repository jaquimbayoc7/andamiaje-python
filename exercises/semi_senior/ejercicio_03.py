"""
RETO SEMI-SENIOR #03 — Sets + Diccionarios
Tema: Sets y diccionarios
"""

METADATA = {
    "id": "ss_03",
    "nivel_rol": "semi_senior",
    "tema": "sets",
    "enunciado": "Escribe una función `keys_with_intersection(d, target_set)` que retorne una lista de claves del dict `d` cuyos valores (listas) tienen al menos un elemento en común con `target_set`.",
    "andamiaje_minimo": "Puedes verificar si dos conjuntos tienen elementos en común con el operador `&` o con `.intersection()`.",
    "andamiaje_parcial": "Recorre `d.items()`. Para cada `(k, v)`, verifica si `isinstance(v, list) and set(v) & target_set`. Si es verdadero, incluye `k` en el resultado.",
    "andamiaje_completo": "Usa una comprensión de lista: `[k for k, v in d.items() if isinstance(v, list) and set(v) & target_set]`. El operador `&` retorna los elementos comunes; si no está vacío, es truthy.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# d = {"a": [1, 2], "b": [3, 4], "c": [2, 5]}
# keys_with_intersection(d, {2, 9})   → ["a", "c"]
# keys_with_intersection(d, {9})      → []
# keys_with_intersection({}, {1})     → []
# d2 = {"x": [1], "y": "hola"}
# keys_with_intersection(d2, {1})     → ["x"]   (ignora no-listas)


def solucion_referencia(d, target_set):
    """Solución de referencia (no modificar)."""
    return [k for k, v in d.items() if isinstance(v, list) and set(v) & target_set]


def solucion_estudiante(d, target_set):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna claves cuyos valores (listas) tienen intersección con target_set.

    Args:
        d: diccionario con valores de tipo lista
        target_set: set de elementos a buscar

    Returns:
        Lista de claves con intersección no vacía
    """
    pass
