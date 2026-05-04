"""
RETO SENIOR #05 — Diccionarios + Funciones
Tema: Funciones y memoización
"""

METADATA = {
    "id": "sr_05",
    "nivel_rol": "senior",
    "tema": "funciones",
    "enunciado": "Escribe un decorador `memoize_unhashable(func)` que memoice cualquier función, incluso si sus argumentos no son hashables (listas, dicts, sets). Debe soportar inspección del cache con `func.cache` y limpieza con `func.clear_cache()`.",
    "andamiaje_minimo": "El problema de memoizar argumentos unhashable es que no pueden ser claves de un dict directamente. Necesitas serializarlos a algo hashable.",
    "andamiaje_parcial": "Convierte los argumentos a JSON con `json.dumps(..., sort_keys=True, default=str)`. Usa el string resultante como clave del cache. Esto funciona para listas, dicts y la mayoría de estructuras anidadas.",
    "andamiaje_completo": "Usa `@functools.wraps(func)`. En el wrapper: intenta `clave = json.dumps((args, sorted(kwargs.items())), sort_keys=True, default=str)`. Si falla, usa `str(args)+str(kwargs)`. Expone `wrapper.cache = cache` y `wrapper.clear_cache = lambda: cache.clear()`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# @memoize_unhashable
# def suma_lista(lst): return sum(lst)
# suma_lista([1,2,3])  → 6  (se cachea)
# suma_lista([1,2,3])  → 6  (del cache)
# len(suma_lista.cache) → 1
# suma_lista.clear_cache()
# len(suma_lista.cache) → 0


import functools
import json


def solucion_referencia(func):
    """Solución de referencia (no modificar)."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            clave = json.dumps(
                (args, sorted(kwargs.items())), sort_keys=True, default=str
            )
        except (TypeError, ValueError):
            clave = str(args) + str(sorted(kwargs.items()))

        if clave not in cache:
            cache[clave] = func(*args, **kwargs)
        return cache[clave]

    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper


def solucion_estudiante(func):
    """
    TU SOLUCIÓN AQUÍ.
    Decorador que memoiza funciones con argumentos unhashable.

    Args:
        func: función a memoizar

    Returns:
        Función memoizada con atributos .cache y .clear_cache()
    """
    pass
