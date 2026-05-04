"""
RETO SENIOR #10 — DataFrames
Tema: DataFrames con pandas
"""

METADATA = {
    "id": "sr_10",
    "nivel_rol": "senior",
    "tema": "dataframes",
    "enunciado": "Escribe una función `rolling_apply(df, col, n, func)` que aplique `func` a una ventana deslizante de tamaño n sobre la columna `col`, SIN usar df[col].rolling(). Retorna df con una nueva columna '{col}_rolling_{n}'.",
    "andamiaje_minimo": "Una ventana deslizante (rolling) de tamaño n sobre la posición i usa los elementos desde i-n+1 hasta i inclusive.",
    "andamiaje_parcial": "Convierte la columna a lista. Para cada posición i >= n-1, aplica `func(valores[i-n+1:i+1])`. Las primeras n-1 posiciones quedan como None.",
    "andamiaje_completo": "Obtén `valores = df[col].tolist()`. Crea `resultados = [None] * (n-1)`. Para i en `range(n-1, len(valores))`, agrega `func(valores[i-n+1:i+1])`. Crea `nuevo_df = df.copy()` y asigna `nuevo_df[f'{col}_rolling_{n}'] = resultados`. Retorna `nuevo_df`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# df con columna "val": [1, 2, 3, 4, 5]
# rolling_apply(df, "val", 3, sum)
# → nueva columna "val_rolling_3": [None, None, 6, 9, 12]
# rolling_apply(df, "val", 2, max)
# → nueva columna "val_rolling_2": [None, 2, 3, 4, 5]


import pandas as pd


def solucion_referencia(df, col, n, func):
    """Solución de referencia (no modificar)."""
    valores = df[col].tolist()
    resultados = [None] * (n - 1)
    for i in range(n - 1, len(valores)):
        resultados.append(func(valores[i - n + 1:i + 1]))
    nuevo_df = df.copy()
    nuevo_df[f"{col}_rolling_{n}"] = resultados
    return nuevo_df


def solucion_estudiante(df, col, n, func):
    """
    TU SOLUCIÓN AQUÍ.
    Aplica func sobre ventanas deslizantes de tamaño n, sin usar .rolling().

    Args:
        df: DataFrame de pandas
        col: nombre de la columna sobre la que calcular
        n: tamaño de la ventana
        func: función a aplicar sobre cada ventana (e.g. sum, max, mean)

    Returns:
        Nuevo DataFrame con columna adicional '{col}_rolling_{n}'
    """
    pass
