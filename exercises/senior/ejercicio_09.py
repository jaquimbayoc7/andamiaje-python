"""
RETO SENIOR #09 — Sets + Diccionarios
Tema: Sets y diccionarios
"""

METADATA = {
    "id": "sr_09",
    "nivel_rol": "senior",
    "tema": "sets",
    "enunciado": "Escribe una función `build_inverted_index(documents)` que construya un índice invertido a partir de una lista de strings. Retorna un dict {palabra: conjunto_de_ids} donde el id es el índice base-0 del documento. Sin distinción de mayúsculas, dividido por espacios.",
    "andamiaje_minimo": "Un índice invertido mapea cada palabra a los documentos que la contienen. Un set de IDs por palabra evita duplicados.",
    "andamiaje_parcial": "Itera sobre `enumerate(documents)`. Para cada `(doc_id, texto)`, convierte a minúsculas y divide por espacios. Para cada palabra, agrega `doc_id` al set correspondiente en el índice.",
    "andamiaje_completo": "Crea `indice = {}`. Para `doc_id, texto` en `enumerate(documents)`: `for palabra in set(texto.lower().split()):` — si `palabra not in indice`, crea `indice[palabra] = set()`. Luego `indice[palabra].add(doc_id)`. Retorna `indice`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# docs = ["Python es genial", "Java es popular", "Python y Java son lenguajes"]
# idx = build_inverted_index(docs)
# idx["python"]   → {0, 2}
# idx["es"]       → {0, 1}
# idx["genial"]   → {0}
# idx.get("ruby") → None


def solucion_referencia(documents):
    """Solución de referencia (no modificar)."""
    indice = {}
    for doc_id, texto in enumerate(documents):
        for palabra in set(texto.lower().split()):
            if palabra not in indice:
                indice[palabra] = set()
            indice[palabra].add(doc_id)
    return indice


def solucion_estudiante(documents):
    """
    TU SOLUCIÓN AQUÍ.
    Construye un índice invertido: {palabra: {doc_ids}}.

    Args:
        documents: lista de strings (documentos)

    Returns:
        Dict {palabra_en_minúsculas: set de índices de documentos}
    """
    pass
