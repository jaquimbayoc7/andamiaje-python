"""
RETO SENIOR #08 — Tuplas + Diccionarios
Tema: Serialización de estructuras arbitrarias
"""

METADATA = {
    "id": "sr_08",
    "nivel_rol": "senior",
    "tema": "tuplas",
    "enunciado": "Escribe una función `serialize_roundtrip(obj)` que serialice cualquier estructura Python anidada (dicts, listas, tuplas, sets con primitivos) a JSON y de vuelta, PRESERVANDO los tipos originales (las tuplas siguen siendo tuplas, los sets siguen siendo sets, no se convierten a listas).",
    "andamiaje_minimo": "JSON nativo no distingue entre listas y tuplas, ni soporta sets. Necesitas un esquema de tipo personalizado.",
    "andamiaje_parcial": "Crea funciones `serializar(o)` y `deserializar(o)` que conviertan estructuras a dicts con `{'__type__': 'tuple', 'data': [...]}` y viceversa.",
    "andamiaje_completo": "En `serializar`: para dict, list, tuple, set, crea `{'__type__': nombre, 'data': [serializar(i) for i in o]}`. En `deserializar`: lee `__type__` y reconstruye el tipo original. Aplica recursivamente. Luego `serialize_roundtrip = lambda obj: deserializar(json.loads(json.dumps(serializar(obj))))`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# obj = {"a": (1, 2), "b": {3, 4}, "c": [5, (6, 7)]}
# result = serialize_roundtrip(obj)
# result["a"] == (1, 2)         → True  (sigue siendo tupla)
# result["b"] == {3, 4}         → True  (sigue siendo set)
# result["c"][1] == (6, 7)      → True  (tupla anidada preservada)


import json


def solucion_referencia(obj):
    """Solución de referencia (no modificar)."""
    def serializar(o):
        if isinstance(o, dict):
            return {"__type__": "dict", "data": {k: serializar(v) for k, v in o.items()}}
        if isinstance(o, list):
            return {"__type__": "list", "data": [serializar(i) for i in o]}
        if isinstance(o, tuple):
            return {"__type__": "tuple", "data": [serializar(i) for i in o]}
        if isinstance(o, set):
            return {"__type__": "set", "data": [serializar(i) for i in sorted(o, key=str)]}
        return {"__type__": type(o).__name__, "data": o}

    def deserializar(o):
        if not isinstance(o, dict) or "__type__" not in o:
            return o
        t = o["__type__"]
        if t == "dict":
            return {k: deserializar(v) for k, v in o["data"].items()}
        if t == "list":
            return [deserializar(i) for i in o["data"]]
        if t == "tuple":
            return tuple(deserializar(i) for i in o["data"])
        if t == "set":
            return set(deserializar(i) for i in o["data"])
        return o["data"]

    return deserializar(json.loads(json.dumps(serializar(obj))))


def solucion_estudiante(obj):
    """
    TU SOLUCIÓN AQUÍ.
    Serializa y deserializa preservando tipos (tuplas, sets, listas, dicts).

    Args:
        obj: estructura Python arbitraria anidada

    Returns:
        Copia de obj con los mismos tipos preservados tras un ciclo JSON
    """
    pass
