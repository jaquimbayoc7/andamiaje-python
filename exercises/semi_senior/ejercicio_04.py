"""
RETO SEMI-SENIOR #04 — DataFrames
Tema: DataFrames con pandas
"""

METADATA = {
    "id": "ss_04",
    "nivel_rol": "semi_senior",
    "tema": "dataframes",
    "enunciado": "Escribe una función `clean_dataframe(df)` que: (1) elimine filas duplicadas, (2) rellene NaN en columnas numéricas con la mediana de la columna, (3) normalice los nombres de columnas a snake_case (minúsculas, espacios/caracteres especiales → guion bajo).",
    "andamiaje_minimo": "Pandas tiene métodos built-in para cada uno de estos tres pasos. Aplícalos en orden.",
    "andamiaje_parcial": "Usa `df.drop_duplicates()`, luego `df[col].fillna(df[col].median())` en un loop para columnas numéricas, y un regex para normalizar nombres de columnas.",
    "andamiaje_completo": "1) `df = df.drop_duplicates()`. 2) Para cada col en `df.select_dtypes(include='number').columns`, haz `df[col] = df[col].fillna(df[col].median())`. 3) `df.columns = [re.sub(r'[^a-z0-9]', '_', col.strip().lower()) for col in df.columns]`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# DataFrame con duplicados, NaN y columnas "First Name", "Age 2023"
# → sin duplicados, NaN reemplazados por mediana, columnas: "first_name", "age_2023"


import re
import pandas as pd


def solucion_referencia(df):
    """Solución de referencia (no modificar)."""
    df = df.copy()
    df = df.drop_duplicates()
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    df.columns = [re.sub(r"[^a-z0-9]+", "_", col.strip().lower()).strip("_")
                  for col in df.columns]
    return df


def solucion_estudiante(df):
    """
    TU SOLUCIÓN AQUÍ.
    Limpia el DataFrame: dedup, rellena NaN numéricos con mediana, snake_case en columnas.

    Args:
        df: pandas DataFrame de entrada

    Returns:
        DataFrame limpio (copia, no modifica el original)
    """
    pass
