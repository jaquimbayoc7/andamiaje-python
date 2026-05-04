"""
RETO JUNIOR #07 — Diccionarios
Tema: Manejo de diccionarios
"""

METADATA = {
    "id": "jr_07",
    "nivel_rol": "junior",
    "tema": "diccionarios",
    "enunciado": "Escribe una función `merge_sum(d1, d2)` que una dos diccionarios. Si una clave existe en ambos, SUMA los valores. Las claves únicas de cada diccionario se conservan tal cual.",
    "andamiaje_minimo": "El método `.get(clave, 0)` retorna el valor o 0 si la clave no existe, útil para sumar.",
    "andamiaje_parcial": "Copia d1 en el resultado. Luego itera d2: para cada clave, suma su valor al existente usando `resultado.get(k, 0) + v`.",
    "andamiaje_completo": "Crea `resultado = dict(d1)`. Luego `for k, v in d2.items(): resultado[k] = resultado.get(k, 0) + v`. Retorna resultado.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# merge_sum({"a": 1, "b": 2}, {"b": 3, "c": 4})  → {"a": 1, "b": 5, "c": 4}
# merge_sum({}, {"x": 10})                          → {"x": 10}
# merge_sum({"k": 5}, {})                           → {"k": 5}
# merge_sum({"a": 1}, {"a": -1})                    → {"a": 0}


def solucion_referencia(d1, d2):
    """Solución de referencia (no modificar)."""
    resultado = dict(d1)
    for k, v in d2.items():
        resultado[k] = resultado.get(k, 0) + v
    return resultado


def solucion_estudiante(d1, d2):
    """
    TU SOLUCIÓN AQUÍ.
    Fusiona dos dicts sumando los valores de claves repetidas.

    Args:
        d1: primer diccionario (valores numéricos)
        d2: segundo diccionario (valores numéricos)

    Returns:
        Diccionario fusionado con valores sumados
    """
    pass
