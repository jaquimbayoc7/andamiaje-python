"""
RETO SENIOR #06 — DataFrames
Tema: DataFrames con pandas y similitud de strings
"""

METADATA = {
    "id": "sr_06",
    "nivel_rol": "senior",
    "tema": "dataframes",
    "enunciado": "Escribe una función `fuzzy_merge(df1, df2, col_left, col_right, threshold=80)` que una dos DataFrames encontrando la mejor coincidencia de texto entre col_left y col_right usando similitud difusa (ratio de Levenshtein). Solo incluye coincidencias con score >= threshold.",
    "andamiaje_minimo": "Necesitas comparar cada fila de df1 con todas las filas de df2 y encontrar la mejor coincidencia de texto.",
    "andamiaje_parcial": "Usa `thefuzz.fuzz.ratio(str1, str2)` para calcular la similitud (0-100). Para cada fila de df1, encuentra la fila de df2 con el mayor ratio. Si supera el umbral, combínalas.",
    "andamiaje_completo": "Itera `df1.iterrows()`. Para cada fila, recorre `df2.iterrows()` y calcula `fuzz.ratio(fila1[col_left], fila2[col_right])`. Guarda el mejor score y fila. Si `score >= threshold`, combina los dicts de ambas filas y agrega `fuzzy_score`. Retorna `pd.DataFrame(filas_resultado)`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# df1: name_a → ["Python Developer", "Data Engineer"]
# df2: name_b → ["Python Dev", "Data Analyst"]
# fuzzy_merge(df1, df2, "name_a", "name_b", threshold=70)
# → combina "Python Developer" con "Python Dev" (ratio ≈ 89)


import pandas as pd
from thefuzz import fuzz


def solucion_referencia(df1, df2, col_left, col_right, threshold=80):
    """Solución de referencia (no modificar)."""
    filas = []
    for _, row1 in df1.iterrows():
        mejor_score = 0
        mejor_fila = None
        for _, row2 in df2.iterrows():
            score = fuzz.ratio(str(row1[col_left]), str(row2[col_right]))
            if score > mejor_score:
                mejor_score = score
                mejor_fila = row2
        if mejor_score >= threshold and mejor_fila is not None:
            combinada = {**row1.to_dict(), **mejor_fila.to_dict(), "fuzzy_score": mejor_score}
            filas.append(combinada)
    return pd.DataFrame(filas)


def solucion_estudiante(df1, df2, col_left, col_right, threshold=80):
    """
    TU SOLUCIÓN AQUÍ.
    Fusiona dos DataFrames usando similitud de strings (fuzzy matching).

    Args:
        df1: primer DataFrame
        df2: segundo DataFrame
        col_left: columna de texto en df1
        col_right: columna de texto en df2
        threshold: porcentaje mínimo de similitud (0-100)

    Returns:
        DataFrame con filas que superan el umbral de similitud
    """
    pass
