"""
RETO SENIOR #03 — DataFrames
Tema: DataFrames con pandas y análisis estadístico
"""

METADATA = {
    "id": "sr_03",
    "nivel_rol": "senior",
    "tema": "dataframes",
    "enunciado": "Escribe una función `detect_data_drift(df1, df2, p_threshold=0.05)` que detecte deriva estadística entre dos DataFrames. Para cada columna numérica compartida, usa el test de Kolmogorov-Smirnov y retorna un DataFrame con columnas: column, statistic, p_value, drift_detected.",
    "andamiaje_minimo": "El test Kolmogorov-Smirnov compara dos distribuciones. Si el p-value es menor que el umbral, hay drift estadístico.",
    "andamiaje_parcial": "Usa `scipy.stats.ks_2samp(df1[col].dropna(), df2[col].dropna())`. Itera sobre las columnas numéricas comunes a ambos DataFrames.",
    "andamiaje_completo": "Identifica columnas comunes numéricas: `set(df1.select_dtypes(include='number').columns) & set(df2.select_dtypes(include='number').columns)`. Para cada una, llama `ks_2samp`. `drift_detected = pvalue < p_threshold`. Retorna `pd.DataFrame(reporte)`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# df1 con col 'age' ~ Normal(30, 5)
# df2 con col 'age' ~ Normal(50, 5)  → drift_detected = True
# df1 == df2 (mismo dataset)          → drift_detected = False


import pandas as pd
from scipy import stats


def solucion_referencia(df1, df2, p_threshold=0.05):
    """Solución de referencia (no modificar)."""
    cols_num1 = set(df1.select_dtypes(include="number").columns)
    cols_num2 = set(df2.select_dtypes(include="number").columns)
    cols_comunes = cols_num1 & cols_num2

    reporte = []
    for col in sorted(cols_comunes):
        stat, pvalue = stats.ks_2samp(df1[col].dropna(), df2[col].dropna())
        reporte.append({
            "columna": col,
            "test": "KS",
            "estadistico": round(stat, 4),
            "p_value": round(pvalue, 4),
            "drift_detectado": pvalue < p_threshold,
        })
    return pd.DataFrame(reporte)


def solucion_estudiante(df1, df2, p_threshold=0.05):
    """
    TU SOLUCIÓN AQUÍ.
    Detecta drift estadístico entre dos DataFrames usando el test KS.

    Args:
        df1: primer DataFrame (baseline)
        df2: segundo DataFrame (producción)
        p_threshold: umbral de p-value para declarar drift

    Returns:
        DataFrame con columnas: columna, test, estadistico, p_value, drift_detectado
    """
    pass
