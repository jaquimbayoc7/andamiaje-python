"""
RETO SENIOR #07 — Variables + Funciones
Tema: Funciones de orden superior
"""

METADATA = {
    "id": "sr_07",
    "nivel_rol": "senior",
    "tema": "funciones",
    "enunciado": "Escribe una función `curry(func)` que transforme cualquier función en su forma currificada. curry(f)(a)(b)(c) debe ser equivalente a f(a, b, c). Debe funcionar para funciones con cualquier número de parámetros.",
    "andamiaje_minimo": "La currificación convierte f(a,b,c) en f(a)(b)(c). Necesitas saber cuántos argumentos acepta la función.",
    "andamiaje_parcial": "Usa `inspect.signature(func)` para obtener el número de parámetros. La función currificada acumula argumentos hasta tener suficientes y luego llama a `func`.",
    "andamiaje_completo": "Obtén `n = len(inspect.signature(func).parameters)`. Define `@functools.wraps(func)` una función `currificada(*args)`: si `len(args) >= n`, llama `func(*args[:n])`; si no, retorna `lambda *more: currificada(*(args + more))`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# @curry
# def suma(a, b, c): return a + b + c
# suma(1)(2)(3)     → 6
# suma(1, 2)(3)     → 6
# suma(1)(2, 3)     → 6
# suma(1, 2, 3)     → 6


import functools
import inspect


def solucion_referencia(func):
    """Solución de referencia (no modificar)."""
    n = len(inspect.signature(func).parameters)

    @functools.wraps(func)
    def currificada(*args):
        if len(args) >= n:
            return func(*args[:n])
        return lambda *more: currificada(*(args + more))

    return currificada


def solucion_estudiante(func):
    """
    TU SOLUCIÓN AQUÍ.
    Convierte `func` en su forma currificada.

    Args:
        func: función a currificar

    Returns:
        Versión currificada de func
    """
    pass
