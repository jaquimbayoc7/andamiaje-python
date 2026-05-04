"""
RETO JUNIOR #06 — Diccionarios
Tema: Manejo de diccionarios
"""

METADATA = {
    "id": "jr_06",
    "nivel_rol": "junior",
    "tema": "diccionarios",
    "enunciado": "Escribe una función `invert_dict(d)` que invierta un diccionario {k: v} → {v: [k1, k2, ...]}. Si varias claves comparten el mismo valor, agrúpalas en una lista.",
    "andamiaje_minimo": "Al invertir, los valores originales se convierten en claves. Pero varios valores originales pueden ser iguales.",
    "andamiaje_parcial": "Recorre `.items()`. Para cada (k, v), agrega k a la lista en `resultado[v]`. Usa `setdefault` o verifica si la clave ya existe.",
    "andamiaje_completo": "Crea un dict vacío. Para cada `k, v` en `d.items()`: si `v` no está en el resultado, crea `resultado[v] = [k]`; si ya está, haz `.append(k)`. Retorna el resultado.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# invert_dict({"a": 1, "b": 2})         → {1: ["a"], 2: ["b"]}
# invert_dict({"a": 1, "b": 1})         → {1: ["a", "b"]}
# invert_dict({})                         → {}
# invert_dict({"x": "y"})               → {"y": ["x"]}


def solucion_referencia(d):
    """Solución de referencia (no modificar)."""
    resultado = {}
    for k, v in d.items():
        if v not in resultado:
            resultado[v] = [k]
        else:
            resultado[v].append(k)
    return resultado


def solucion_estudiante(d):
    """
    TU SOLUCIÓN AQUÍ.
    Invierte {k: v} → {v: [k1, k2, ...]} agrupando claves con el mismo valor.

    Args:
        d: diccionario de entrada

    Returns:
        Diccionario invertido con listas de claves
    """
    pass
