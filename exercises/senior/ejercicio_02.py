"""
RETO SENIOR #02 — Funciones
Tema: Decoradores avanzados
"""

METADATA = {
    "id": "sr_02",
    "nivel_rol": "senior",
    "tema": "funciones",
    "enunciado": "Escribe un decorador factory `validar_tipos(**expected_types)` que valide los tipos de los argumentos en tiempo de ejecución. Ejemplo: @validar_tipos(x=int, y=str) lanza TypeError con un mensaje claro si los tipos no coinciden.",
    "andamiaje_minimo": "Necesitas tres capas: la función factory que recibe los tipos, el decorador que envuelve la función, y el wrapper que hace la validación.",
    "andamiaje_parcial": "Usa `inspect.signature(func).bind(*args, **kwargs).apply_defaults()` para obtener los argumentos por nombre. Luego verifica con `isinstance()` cada argumento que aparezca en `expected_types`.",
    "andamiaje_completo": "Usa `@functools.wraps(func)`. En el wrapper, haz `sig = inspect.signature(func); bound = sig.bind(*args, **kwargs); bound.apply_defaults()`. Itera `bound.arguments.items()` y lanza `TypeError` si `param in expected_types and not isinstance(valor, expected_types[param])`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# @validar_tipos(x=int, y=str)
# def greet(x, y): return f"{y} * {x}"
# greet(3, "hola")         → "hola * 3"
# greet("3", "hola")       → TypeError: Parámetro 'x': se esperaba int, se recibió str
# greet(3, 42)             → TypeError: Parámetro 'y': se esperaba str, se recibió int


import functools
import inspect


def solucion_referencia(**expected_types):
    """Solución de referencia (no modificar)."""
    def decorador(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for param, valor in bound.arguments.items():
                if param in expected_types:
                    tipo = expected_types[param]
                    if not isinstance(valor, tipo):
                        raise TypeError(
                            f"Parámetro '{param}': se esperaba {tipo.__name__}, "
                            f"se recibió {type(valor).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorador


def solucion_estudiante(**expected_types):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna un decorador que valida tipos de argumentos en tiempo de ejecución.

    Args:
        **expected_types: nombre_param=Tipo para cada argumento a validar

    Returns:
        Decorador que aplica la validación
    """
    pass
