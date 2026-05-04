"""
RETO SEMI-SENIOR #05 — DataFrames
Tema: DataFrames con pandas
"""

METADATA = {
    "id": "ss_05",
    "nivel_rol": "semi_senior",
    "tema": "dataframes",
    "enunciado": "Escribe una función `top3_by_region(df)` que, dado un DataFrame de ventas con columnas 'region', 'product', 'sales', retorne los 3 productos con mayor venta total por región. Usa solo groupby y nlargest.",
    "andamiaje_minimo": "Agrupa por región y producto, suma ventas, luego selecciona los 3 mayores por región.",
    "andamiaje_parcial": "Primero `groupby(['region','product'])['sales'].sum()`, luego `.reset_index()`. Después agrupa por región y aplica `nlargest(3, 'sales')`.",
    "andamiaje_completo": "Usa: `df.groupby(['region','product'])['sales'].sum().reset_index().groupby('region').apply(lambda g: g.nlargest(3, 'sales')).reset_index(drop=True)`. El lambda selecciona los 3 mayores por grupo.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# DataFrame: region, product, sales
# Para 'Norte': retorna los 3 productos con mayor suma de ventas en esa región

import pandas as pd


def solucion_referencia(df):
    """Solución de referencia (no modificar)."""
    return (
        df.groupby(["region", "product"])["sales"]
        .sum()
        .reset_index()
        .groupby("region")
        .apply(lambda g: g.nlargest(3, "sales"))
        .reset_index(drop=True)
    )


def solucion_estudiante(df):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna top-3 productos por total de ventas por región.

    Args:
        df: DataFrame con columnas 'region', 'product', 'sales'

    Returns:
        DataFrame con los top-3 por región
    """
    pass
