"""
tests/test_semi_senior.py
Tests pytest para los 10 ejercicios Semi-Senior.
Se prueban las soluciones de referencia — siempre deben pasar.
"""

import sys
import os

import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exercises.semi_senior.ejercicio_01 import solucion_referencia as group_by
from exercises.semi_senior.ejercicio_02 import solucion_referencia as deep_get
from exercises.semi_senior.ejercicio_03 import solucion_referencia as keys_with_intersection
from exercises.semi_senior.ejercicio_04 import solucion_referencia as clean_dataframe
from exercises.semi_senior.ejercicio_05 import solucion_referencia as top3_by_region
from exercises.semi_senior.ejercicio_06 import solucion_referencia as tuples_to_nested_dict
from exercises.semi_senior.ejercicio_07 import solucion_referencia as pipeline
from exercises.semi_senior.ejercicio_08 import solucion_referencia as dict_diff
from exercises.semi_senior.ejercicio_09 import solucion_referencia as elements_in_exactly_k
from exercises.semi_senior.ejercicio_10 import solucion_referencia as long_to_wide


# ── Ss 01: Group By ───────────────────────────────────────────────────────────
class TestSs01GroupBy:
    def test_basico(self):
        data = [{"city": "Bogotá", "n": "Ana"}, {"city": "Medellín", "n": "Luis"}, {"city": "Bogotá", "n": "Pedro"}]
        result = group_by(data, "city")
        assert len(result["Bogotá"]) == 2
        assert len(result["Medellín"]) == 1

    def test_lista_vacia(self):
        assert group_by([], "x") == {}

    def test_clave_inexistente(self):
        data = [{"a": 1}, {"b": 2}]
        result = group_by(data, "x")
        assert None in result


# ── Ss 02: Deep Get ───────────────────────────────────────────────────────────
class TestSs02DeepGet:
    def test_ruta_existente(self):
        d = {"a": {"b": {"c": 42}}}
        assert deep_get(d, "a.b.c") == 42

    def test_ruta_inexistente(self):
        d = {"a": {"b": {"c": 42}}}
        assert deep_get(d, "a.b.x") is None

    def test_default_personalizado(self):
        assert deep_get({}, "a.b", default=-1) == -1

    def test_valor_en_key_hoja(self):
        assert deep_get({"a": 1}, "a") == 1

    def test_anidamiento_parcial(self):
        assert deep_get({"a": 1}, "a.b") is None


# ── Ss 03: Keys with Intersection ────────────────────────────────────────────
class TestSs03KeysWithIntersection:
    def test_basico(self):
        d = {"a": [1, 2], "b": [3, 4], "c": [2, 5]}
        assert sorted(keys_with_intersection(d, {2, 9})) == ["a", "c"]

    def test_sin_interseccion(self):
        d = {"a": [1, 2], "b": [3, 4]}
        assert keys_with_intersection(d, {9}) == []

    def test_dict_vacio(self):
        assert keys_with_intersection({}, {1}) == []

    def test_ignora_no_listas(self):
        d = {"x": [1], "y": "hola"}
        assert keys_with_intersection(d, {1}) == ["x"]


# ── Ss 04: Clean DataFrame ────────────────────────────────────────────────────
class TestSs04CleanDataframe:
    @pytest.fixture
    def df_sucio(self):
        return pd.DataFrame({
            "First Name": ["Ana", "Luis", "Ana", None],
            "Age 2023": [25.0, None, 25.0, 30.0],
        })

    def test_elimina_duplicados(self, df_sucio):
        result = clean_dataframe(df_sucio)
        assert len(result) < len(df_sucio)

    def test_rellena_nan(self, df_sucio):
        result = clean_dataframe(df_sucio)
        assert result.select_dtypes(include="number").isna().sum().sum() == 0

    def test_snake_case_columnas(self, df_sucio):
        result = clean_dataframe(df_sucio)
        for col in result.columns:
            assert col == col.lower()
            assert " " not in col

    def test_no_modifica_original(self, df_sucio):
        original_cols = list(df_sucio.columns)
        clean_dataframe(df_sucio)
        assert list(df_sucio.columns) == original_cols


# ── Ss 05: Top 3 by Region ────────────────────────────────────────────────────
class TestSs05Top3ByRegion:
    @pytest.fixture
    def df_ventas(self):
        return pd.DataFrame({
            "region": ["Norte"] * 5 + ["Sur"] * 4,
            "product": ["A", "B", "C", "D", "E", "A", "B", "C", "D"],
            "sales": [100, 200, 300, 400, 500, 50, 150, 250, 350],
        })

    def test_retorna_dataframe(self, df_ventas):
        result = top3_by_region(df_ventas)
        assert isinstance(result, pd.DataFrame)

    def test_max_3_por_region(self, df_ventas):
        result = top3_by_region(df_ventas)
        for region, grp in result.groupby("region"):
            assert len(grp) <= 3


# ── Ss 06: Tuples to Nested Dict ─────────────────────────────────────────────
class TestSs06TuplesToNestedDict:
    def test_basico(self):
        result = tuples_to_nested_dict([("a", 1, 2), ("b", 3, 4)])
        assert result == {"a": {"val1": 1, "val2": 2}, "b": {"val1": 3, "val2": 4}}

    def test_vacio(self):
        assert tuples_to_nested_dict([]) == {}

    def test_campos_personalizados(self):
        result = tuples_to_nested_dict([("k", 10, 20)], field1="x", field2="y")
        assert result == {"k": {"x": 10, "y": 20}}


# ── Ss 07: Pipeline ───────────────────────────────────────────────────────────
class TestSs07Pipeline:
    def test_encadenado(self):
        doble = lambda x: x * 2
        mas_uno = lambda x: x + 1
        al_str = lambda x: str(x)
        assert pipeline(doble, mas_uno, al_str)(3) == "7"

    def test_sin_funciones(self):
        assert pipeline()(5) == 5

    def test_una_funcion(self):
        assert pipeline(lambda x: x ** 2)(4) == 16


# ── Ss 08: Dict Diff ──────────────────────────────────────────────────────────
class TestSs08DictDiff:
    def test_valores_distintos(self):
        assert dict_diff({"a": 1}, {"a": 2}) == {"a"}

    def test_clave_faltante(self):
        assert dict_diff({"a": 1, "b": 2}, {"a": 1}) == {"b"}

    def test_anidado(self):
        assert dict_diff({"a": {"x": 1}}, {"a": {"x": 2}}) == {"a.x"}

    def test_iguales(self):
        assert dict_diff({}, {}) == set()


# ── Ss 09: Elements in Exactly K ─────────────────────────────────────────────
class TestSs09ElementsInExactlyK:
    def test_k_1(self):
        result = elements_in_exactly_k([{1, 2}, {2, 3}, {3, 4}], 1)
        assert result == {1, 4}

    def test_k_2(self):
        result = elements_in_exactly_k([{1, 2}, {2, 3}, {3, 4}], 2)
        assert result == {2, 3}

    def test_lista_vacia(self):
        assert elements_in_exactly_k([], 1) == set()

    def test_sin_resultado(self):
        assert elements_in_exactly_k([{1}], 2) == set()


# ── Ss 10: Long to Wide ───────────────────────────────────────────────────────
class TestSs10LongToWide:
    @pytest.fixture
    def df_long(self):
        return pd.DataFrame({
            "id": [1, 1, 2, 2],
            "variable": ["a", "b", "a", "b"],
            "valor": [10, 20, 30, 40],
        })

    def test_retorna_dataframe(self, df_long):
        result = long_to_wide(df_long, "id", "variable", "valor")
        assert isinstance(result, pd.DataFrame)

    def test_columnas_pivoteadas(self, df_long):
        result = long_to_wide(df_long, "id", "variable", "valor")
        assert "a" in result.columns and "b" in result.columns

    def test_valores_correctos(self, df_long):
        result = long_to_wide(df_long, "id", "variable", "valor")
        fila_id1 = result[result["id"] == 1].iloc[0]
        assert fila_id1["a"] == 10
        assert fila_id1["b"] == 20
