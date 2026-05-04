"""
tests/conftest.py — Fixtures compartidos entre test_junior, test_semi_senior y test_senior.
"""
import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def df_simple():
    """DataFrame genérico 5x3 para pruebas rápidas."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "nombre": ["Ana", "Luis", "Pedro", "María", "Carlos"],
        "puntaje": [85.0, 90.0, 78.5, 92.0, 88.0],
    })


@pytest.fixture
def df_con_nulos():
    """DataFrame con valores nulos y duplicados."""
    return pd.DataFrame({
        "nombre": ["Ana", "Luis", "Ana", None],
        "edad": [25.0, None, 25.0, 30.0],
        "ciudad": ["Bogotá", "Medellín", "Bogotá", "Cali"],
    })


@pytest.fixture
def lista_docs_basica():
    """Documentos de texto para pruebas de índice invertido."""
    return [
        "Python es genial",
        "Java es popular",
        "Python y Java son lenguajes",
    ]


@pytest.fixture
def df_ventas():
    """DataFrame de ventas por región para pruebas de agregación."""
    np.random.seed(0)
    return pd.DataFrame({
        "region": ["Norte"] * 5 + ["Sur"] * 5 + ["Centro"] * 5,
        "product": list("ABCDEABCDEABCDE"),
        "sales": np.random.randint(100, 1000, 15),
    })
