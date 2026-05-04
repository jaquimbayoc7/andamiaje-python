"""
RETO SEMI-SENIOR #02 — Diccionarios + Funciones
Tema: Diccionarios y funciones
"""

METADATA = {
    "id": "ss_02",
    "nivel_rol": "semi_senior",
    "tema": "diccionarios",
    "enunciado": "Escribe una función `deep_get(d, path, default=None)` que acceda de forma segura a claves anidadas de un dict usando notación de punto. Ej: deep_get(d, 'a.b.c') retorna d['a']['b']['c'] o default si alguna clave falta.",
    "andamiaje_minimo": "Divide la ruta en partes por el punto `.` y navega el diccionario clave por clave.",
    "andamiaje_parcial": "Usa `path.split('.')` para obtener la lista de claves. Recórrela actualizando `actual = actual[clave]`. Si en algún momento la clave no existe, retorna `default`.",
    "andamiaje_completo": "Divide con `claves = path.split('.')`. Inicializa `actual = d`. Para cada `clave` en `claves`: verifica `isinstance(actual, dict) and clave in actual`; si no, retorna `default`. Actualiza `actual = actual[clave]`. Al final retorna `actual`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# d = {"a": {"b": {"c": 42}}}
# deep_get(d, "a.b.c")         → 42
# deep_get(d, "a.b.x")         → None
# deep_get(d, "a.b.x", -1)     → -1
# deep_get({}, "a.b")           → None
# deep_get({"a": 1}, "a.b")    → None


def solucion_referencia(d, path, default=None):
    """Solución de referencia (no modificar)."""
    claves = path.split(".")
    actual = d
    for clave in claves:
        if isinstance(actual, dict) and clave in actual:
            actual = actual[clave]
        else:
            return default
    return actual


def solucion_estudiante(d, path, default=None):
    """
    TU SOLUCIÓN AQUÍ.
    Accede de forma segura a claves anidadas usando notación de punto.

    Args:
        d: diccionario (posiblemente anidado)
        path: ruta con notación de punto, e.g. "a.b.c"
        default: valor a retornar si la ruta no existe

    Returns:
        Valor en la ruta o default si no existe
    """
    pass
