"""
RETO SEMI-SENIOR #01 — Diccionarios + Listas
Tema: Diccionarios y listas
"""

METADATA = {
    "id": "ss_01",
    "nivel_rol": "semi_senior",
    "tema": "diccionarios",
    "enunciado": "Escribe una función `group_by(data, key)` que agrupe una lista de dicts por una clave dada. Retorna un dict donde cada clave apunta a una lista de registros que la comparten.",
    "andamiaje_minimo": "Piensa en construir un diccionario donde cada valor sea una lista de elementos que comparten la misma clave de agrupación.",
    "andamiaje_parcial": "Recorre `data`, extrae `item.get(key)` como clave de agrupación. Si ya existe en el resultado, haz `.append(item)`. Si no, créala con `[item]`.",
    "andamiaje_completo": "Crea `resultado = {}`. Para cada `item` en `data`, obtén `k = item.get(key)`. Si `k not in resultado`, escribe `resultado[k] = []`. Luego `resultado[k].append(item)`. Retorna resultado.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# data = [{"city": "Bogotá", "name": "Ana"}, {"city": "Medellín", "name": "Luis"}, {"city": "Bogotá", "name": "Pedro"}]
# group_by(data, "city") → {"Bogotá": [{"city":"Bogotá","name":"Ana"}, {"city":"Bogotá","name":"Pedro"}], "Medellín": [...]}
# group_by([], "x")       → {}


def solucion_referencia(data, key):
    """Solución de referencia (no modificar)."""
    resultado = {}
    for item in data:
        k = item.get(key)
        if k not in resultado:
            resultado[k] = []
        resultado[k].append(item)
    return resultado


def solucion_estudiante(data, key):
    """
    TU SOLUCIÓN AQUÍ.
    Agrupa una lista de dicts por el valor de una clave dada.

    Args:
        data: lista de diccionarios
        key: clave de agrupación

    Returns:
        Dict {valor_clave: [registros que comparten ese valor]}
    """
    pass
