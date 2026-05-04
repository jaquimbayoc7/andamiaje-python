"""
RETO SEMI-SENIOR #10 — DataFrames
Tema: DataFrames con pandas
"""

METADATA = {
    "id": "ss_10",
    "nivel_rol": "semi_senior",
    "tema": "dataframes",
    "enunciado": "Escribe una función `long_to_wide(df, index_col, col_col, val_col)` que pivote un DataFrame en formato largo a formato ancho SIN usar df.pivot_table() ni df.pivot() directamente.",
    "andamiaje_minimo": "Puedes construir el DataFrame wide iterando las filas y creando un diccionario de diccionarios.",
    "andamiaje_parcial": "Recorre las filas con `df.iterrows()`. Para cada fila, crea una entrada en un dict usando `index_col` como clave externa y `col_col` como clave interna del dict de valores.",
    "andamiaje_completo": "Crea `resultado = {}`. Para cada `_, row` en `iterrows()`: usa `row[index_col]` como clave. Si no existe, crea `resultado[key] = {index_col: key}`. Luego agrega `resultado[key][row[col_col]] = row[val_col]`. Convierte a DataFrame al final.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# df_long: id, variable, valor
#          1,  "a",      10
#          1,  "b",      20
#          2,  "a",      30
# long_to_wide(df, "id", "variable", "valor")
# → df_wide: id, a,  b
#             1, 10, 20
#             2, 30, NaN

import pandas as pd


def solucion_referencia(df, index_col, col_col, val_col):
    """Solución de referencia (no modificar)."""
    resultado = {}
    for _, row in df.iterrows():
        key = row[index_col]
        if key not in resultado:
            resultado[key] = {index_col: key}
        resultado[key][row[col_col]] = row[val_col]
    return pd.DataFrame(list(resultado.values()))


def solucion_estudiante(df, index_col, col_col, val_col):
    """
    TU SOLUCIÓN AQUÍ.
    Pivota un DataFrame de formato long a wide sin usar pivot_table() ni pivot().

    Args:
        df: DataFrame en formato long
        index_col: columna que será el índice del wide
        col_col: columna cuyos valores se convertirán en columnas
        val_col: columna con los valores

    Returns:
        DataFrame en formato wide
    """
    pass
