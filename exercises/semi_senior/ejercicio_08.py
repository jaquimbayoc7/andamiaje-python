"""
RETO SEMI-SENIOR #08 — Diccionarios
Tema: Diccionarios
"""

METADATA = {
    "id": "ss_08",
    "nivel_rol": "semi_senior",
    "tema": "diccionarios",
    "enunciado": "Escribe una función `dict_diff(d1, d2, prefix='')` que retorne un conjunto de rutas en notación de punto para todas las claves que difieren entre dos dicts (a cualquier profundidad). Una clave difiere si falta en alguno de los dos o tiene valores distintos.",
    "andamiaje_minimo": "Necesitas recorrer recursivamente ambos dicts. Cuando una clave existe en uno pero no en el otro, o sus valores difieren, regístrala.",
    "andamiaje_parcial": "Une las claves de ambos dicts. Para cada clave, si falta en alguno o los valores son distintos, agrégala al resultado. Si ambos valores son dicts, llama recursivamente.",
    "andamiaje_completo": "Combina `set(d1.keys()) | set(d2.keys())`. Para cada `k`, construye `clave_completa = f'{prefix}.{k}' if prefix else k`. Si `k` no está en los dos, agrégala. Si ambos valores son dicts, recúrsela. Si valores difieren, agrégala.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# dict_diff({"a": 1}, {"a": 2})              → {"a"}
# dict_diff({"a": 1, "b": 2}, {"a": 1})      → {"b"}
# dict_diff({"a": {"x": 1}}, {"a": {"x": 2}}) → {"a.x"}
# dict_diff({}, {})                            → set()


def solucion_referencia(d1, d2, prefix=""):
    """Solución de referencia (no modificar)."""
    diferencias = set()
    todas_claves = set(d1.keys()) | set(d2.keys())
    for k in todas_claves:
        clave_completa = f"{prefix}.{k}" if prefix else k
        if k not in d1 or k not in d2:
            diferencias.add(clave_completa)
        elif isinstance(d1[k], dict) and isinstance(d2[k], dict):
            diferencias |= solucion_referencia(d1[k], d2[k], clave_completa)
        elif d1[k] != d2[k]:
            diferencias.add(clave_completa)
    return diferencias


def solucion_estudiante(d1, d2, prefix=""):
    """
    TU SOLUCIÓN AQUÍ.
    Detecta todas las rutas en notación de punto donde los dicts difieren.

    Args:
        d1: primer diccionario
        d2: segundo diccionario
        prefix: prefijo acumulado para rutas anidadas (no modificar en llamada inicial)

    Returns:
        Set de rutas (strings con puntos) que difieren entre d1 y d2
    """
    pass
