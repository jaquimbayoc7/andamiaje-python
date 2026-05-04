"""
RETO SEMI-SENIOR #06 — Tuplas + Diccionarios
Tema: Tuplas y diccionarios
"""

METADATA = {
    "id": "ss_06",
    "nivel_rol": "semi_senior",
    "tema": "tuplas",
    "enunciado": "Escribe una función `tuples_to_nested_dict(data, field1='val1', field2='val2')` que convierta una lista de 3-tuplas [(clave, v1, v2), ...] en un dict anidado {clave: {field1: v1, field2: v2}}.",
    "andamiaje_minimo": "Cada tupla tiene 3 elementos: la clave del dict externo y dos valores que formarán el dict interno.",
    "andamiaje_parcial": "Desempaqueta cada tupla como `k, v1, v2`. Crea el dict interno `{field1: v1, field2: v2}` y úsalo como valor en el resultado.",
    "andamiaje_completo": "Usa una comprensión de dict: `{k: {field1: v1, field2: v2} for k, v1, v2 in data}`. Desempaqueta cada tupla directamente en el for.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# tuples_to_nested_dict([("a", 1, 2), ("b", 3, 4)])
# → {"a": {"val1": 1, "val2": 2}, "b": {"val1": 3, "val2": 4}}
# tuples_to_nested_dict([], "x", "y") → {}


def solucion_referencia(data, field1="val1", field2="val2"):
    """Solución de referencia (no modificar)."""
    return {k: {field1: v1, field2: v2} for k, v1, v2 in data}


def solucion_estudiante(data, field1="val1", field2="val2"):
    """
    TU SOLUCIÓN AQUÍ.
    Convierte lista de tuplas (k, v1, v2) en dict anidado {k: {field1: v1, field2: v2}}.

    Args:
        data: lista de tuplas de 3 elementos
        field1: nombre del primer campo del dict interno
        field2: nombre del segundo campo del dict interno

    Returns:
        Dict anidado
    """
    pass
