"""
RETO SENIOR #04 — Listas + Sets
Tema: Listas y conjuntos
"""

METADATA = {
    "id": "sr_04",
    "nivel_rol": "senior",
    "tema": "listas",
    "enunciado": "Escribe una función `combinations_k(lst, k)` que retorne todos los subconjuntos de `lst` de exactamente tamaño k, SIN usar itertools.combinations ni ninguna función de itertools.",
    "andamiaje_minimo": "Piensa en una solución recursiva: para elegir k elementos de n, elige el primero y luego k-1 del resto.",
    "andamiaje_parcial": "Caso base: si k==0, retorna [[]]. Para cada posición i, incluye `lst[i]` y combina con todas las combinaciones de tamaño k-1 de `lst[i+1:]`.",
    "andamiaje_completo": "Define `def combo(lst, k, start=0):`. Si `k==0`, return `[[]]`. Para i en range(start, len(lst)-k+1), para cada `rest` en `combo(lst, k-1, i+1)`, agrega `[lst[i]] + rest`. Retorna la lista acumulada.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# combinations_k([1,2,3], 2)  → [[1,2], [1,3], [2,3]]
# combinations_k([1,2,3], 0)  → [[]]
# combinations_k([1,2,3], 3)  → [[1,2,3]]
# combinations_k([], 1)        → []
# combinations_k([1,2,3], 4)  → []


def solucion_referencia(lst, k):
    """Solución de referencia (no modificar)."""
    def combo(lst, k, start=0):
        if k == 0:
            return [[]]
        resultado = []
        for i in range(start, len(lst) - k + 1):
            for rest in combo(lst, k - 1, i + 1):
                resultado.append([lst[i]] + rest)
        return resultado

    return combo(lst, k)


def solucion_estudiante(lst, k):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna todos los subconjuntos de tamaño k sin usar itertools.

    Args:
        lst: lista de elementos
        k: tamaño de cada subconjunto

    Returns:
        Lista de listas, cada una con k elementos
    """
    pass
