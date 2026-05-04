"""
tests/test_senior.py
Tests pytest para los 10 ejercicios Senior.
Se prueban las soluciones de referencia — siempre deben pasar.
"""

import sys
import os

import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exercises.senior.ejercicio_01 import solucion_referencia as make_lfu
from exercises.senior.ejercicio_02 import solucion_referencia as validar_tipos
from exercises.senior.ejercicio_03 import solucion_referencia as detect_data_drift
from exercises.senior.ejercicio_04 import solucion_referencia as combinations_k
from exercises.senior.ejercicio_05 import solucion_referencia as memoize_unhashable
from exercises.senior.ejercicio_06 import solucion_referencia as fuzzy_merge
from exercises.senior.ejercicio_07 import solucion_referencia as curry
from exercises.senior.ejercicio_08 import solucion_referencia as serialize_roundtrip
from exercises.senior.ejercicio_09 import solucion_referencia as build_inverted_index
from exercises.senior.ejercicio_10 import solucion_referencia as rolling_apply


# ── Sr 01: LFU Dict ───────────────────────────────────────────────────────────
class TestSr01LFUDict:
    def test_get_existente(self):
        lfu = make_lfu(2)
        lfu.put(1, 10)
        assert lfu.get(1) == 10

    def test_get_inexistente(self):
        lfu = make_lfu(2)
        assert lfu.get(99) == -1

    def test_eviccion_lfu(self):
        lfu = make_lfu(2)
        lfu.put(1, 1)
        lfu.put(2, 2)
        lfu.get(1)          # freq(1)=2, freq(2)=1
        lfu.put(3, 3)       # expulsa 2 (menor frecuencia)
        assert lfu.get(2) == -1
        assert lfu.get(3) == 3

    def test_capacidad_cero(self):
        lfu = make_lfu(0)
        lfu.put(1, 1)
        assert lfu.get(1) == -1


# ── Sr 02: Validar Tipos ──────────────────────────────────────────────────────
class TestSr02ValidarTipos:
    def test_tipos_correctos(self):
        @validar_tipos(x=int, y=str)
        def greet(x, y):
            return f"{y} * {x}"
        assert greet(3, "hola") == "hola * 3"

    def test_tipo_incorrecto_primer_arg(self):
        @validar_tipos(x=int)
        def func(x):
            return x
        with pytest.raises(TypeError):
            func("no_soy_int")

    def test_tipo_incorrecto_segundo_arg(self):
        @validar_tipos(x=int, y=str)
        def func(x, y):
            return (x, y)
        with pytest.raises(TypeError):
            func(1, 42)

    def test_sin_validacion(self):
        @validar_tipos()
        def func(x):
            return x
        assert func("cualquier_cosa") == "cualquier_cosa"


# ── Sr 03: Data Drift ─────────────────────────────────────────────────────────
class TestSr03DataDrift:
    @pytest.fixture
    def dfs_sin_drift(self):
        np.random.seed(42)
        d = pd.DataFrame({"val": np.random.normal(30, 5, 100)})
        return d, d.copy()

    @pytest.fixture
    def dfs_con_drift(self):
        np.random.seed(42)
        df1 = pd.DataFrame({"val": np.random.normal(30, 5, 200)})
        df2 = pd.DataFrame({"val": np.random.normal(80, 5, 200)})
        return df1, df2

    def test_retorna_dataframe(self, dfs_sin_drift):
        df1, df2 = dfs_sin_drift
        result = detect_data_drift(df1, df2)
        assert isinstance(result, pd.DataFrame)

    def test_columnas_esperadas(self, dfs_sin_drift):
        df1, df2 = dfs_sin_drift
        result = detect_data_drift(df1, df2)
        assert "drift_detectado" in result.columns

    def test_sin_drift(self, dfs_sin_drift):
        df1, df2 = dfs_sin_drift
        result = detect_data_drift(df1, df2)
        assert not result["drift_detectado"].any()

    def test_con_drift(self, dfs_con_drift):
        df1, df2 = dfs_con_drift
        result = detect_data_drift(df1, df2)
        assert result["drift_detectado"].any()


# ── Sr 04: Combinations K ────────────────────────────────────────────────────
class TestSr04CombinationsK:
    def test_basico(self):
        result = combinations_k([1, 2, 3], 2)
        assert sorted([sorted(c) for c in result]) == [[1, 2], [1, 3], [2, 3]]

    def test_k_cero(self):
        assert combinations_k([1, 2, 3], 0) == [[]]

    def test_k_igual_n(self):
        assert combinations_k([1, 2, 3], 3) == [[1, 2, 3]]

    def test_lista_vacia(self):
        assert combinations_k([], 1) == []

    def test_k_mayor_que_n(self):
        assert combinations_k([1, 2, 3], 4) == []


# ── Sr 05: Memoize Unhashable ─────────────────────────────────────────────────
class TestSr05MemoizeUnhashable:
    def test_resultado_correcto(self):
        @memoize_unhashable
        def suma_lista(lst):
            return sum(lst)
        assert suma_lista([1, 2, 3]) == 6

    def test_usa_cache(self):
        call_count = [0]

        @memoize_unhashable
        def costosa(lst):
            call_count[0] += 1
            return sum(lst)

        costosa([1, 2, 3])
        costosa([1, 2, 3])
        assert call_count[0] == 1

    def test_clear_cache(self):
        @memoize_unhashable
        def func(lst):
            return sum(lst)
        func([1, 2])
        assert len(func.cache) == 1
        func.clear_cache()
        assert len(func.cache) == 0

    def test_dict_como_argumento(self):
        @memoize_unhashable
        def suma_valores(d):
            return sum(d.values())
        assert suma_valores({"a": 1, "b": 2}) == 3


# ── Sr 06: Fuzzy Merge ────────────────────────────────────────────────────────
class TestSr06FuzzyMerge:
    @pytest.fixture
    def dfs(self):
        df1 = pd.DataFrame({"name_a": ["Python Developer", "Data Engineer"], "id": [1, 2]})
        df2 = pd.DataFrame({"name_b": ["Python Dev", "Data Analyst"], "salary": [5000, 4500]})
        return df1, df2

    def test_retorna_dataframe(self, dfs):
        df1, df2 = dfs
        result = fuzzy_merge(df1, df2, "name_a", "name_b", threshold=70)
        assert isinstance(result, pd.DataFrame)

    def test_columna_fuzzy_score(self, dfs):
        df1, df2 = dfs
        result = fuzzy_merge(df1, df2, "name_a", "name_b", threshold=70)
        if len(result) > 0:
            assert "fuzzy_score" in result.columns

    def test_umbral_alto_sin_resultados(self, dfs):
        df1, df2 = dfs
        result = fuzzy_merge(df1, df2, "name_a", "name_b", threshold=100)
        assert len(result) == 0


# ── Sr 07: Curry ──────────────────────────────────────────────────────────────
class TestSr07Curry:
    def test_llamada_individual(self):
        @curry
        def suma(a, b, c):
            return a + b + c
        assert suma(1)(2)(3) == 6

    def test_llamada_parcial(self):
        @curry
        def suma(a, b, c):
            return a + b + c
        assert suma(1, 2)(3) == 6

    def test_llamada_completa(self):
        @curry
        def suma(a, b, c):
            return a + b + c
        assert suma(1, 2, 3) == 6

    def test_un_parametro(self):
        @curry
        def identidad(x):
            return x
        assert identidad(42) == 42


# ── Sr 08: Serialize Roundtrip ────────────────────────────────────────────────
class TestSr08SerializeRoundtrip:
    def test_tupla_preservada(self):
        obj = (1, 2, 3)
        assert serialize_roundtrip(obj) == (1, 2, 3)
        assert isinstance(serialize_roundtrip(obj), tuple)

    def test_set_preservado(self):
        obj = {1, 2, 3}
        result = serialize_roundtrip(obj)
        assert result == {1, 2, 3}
        assert isinstance(result, set)

    def test_estructura_anidada(self):
        obj = {"a": (1, 2), "b": {3, 4}}
        result = serialize_roundtrip(obj)
        assert isinstance(result["a"], tuple)
        assert isinstance(result["b"], set)

    def test_lista_preservada(self):
        obj = [1, [2, 3]]
        result = serialize_roundtrip(obj)
        assert result == [1, [2, 3]]
        assert isinstance(result, list)


# ── Sr 09: Inverted Index ─────────────────────────────────────────────────────
class TestSr09InvertedIndex:
    def test_basico(self):
        docs = ["Python es genial", "Java es popular", "Python y Java son lenguajes"]
        idx = build_inverted_index(docs)
        assert idx["python"] == {0, 2}
        assert idx["es"] == {0, 1}

    def test_lista_vacia(self):
        assert build_inverted_index([]) == {}

    def test_case_insensitive(self):
        idx = build_inverted_index(["HOLA MUNDO", "hola colombia"])
        assert 0 in idx["hola"]
        assert 1 in idx["hola"]

    def test_palabra_inexistente(self):
        idx = build_inverted_index(["hola mundo"])
        assert "ruby" not in idx


# ── Sr 10: Rolling Apply ──────────────────────────────────────────────────────
class TestSr10RollingApply:
    @pytest.fixture
    def df_nums(self):
        return pd.DataFrame({"val": [1, 2, 3, 4, 5]})

    def test_suma_ventana_3(self, df_nums):
        result = rolling_apply(df_nums, "val", 3, sum)
        col = "val_rolling_3"
        assert col in result.columns
        assert result[col].iloc[2] == 6
        assert result[col].iloc[4] == 12

    def test_nones_iniciales(self, df_nums):
        result = rolling_apply(df_nums, "val", 3, sum)
        assert result["val_rolling_3"].iloc[0] is None or pd.isna(result["val_rolling_3"].iloc[0])

    def test_no_modifica_original(self, df_nums):
        original_cols = list(df_nums.columns)
        rolling_apply(df_nums, "val", 2, max)
        assert list(df_nums.columns) == original_cols

    def test_ventana_2_max(self, df_nums):
        result = rolling_apply(df_nums, "val", 2, max)
        assert result["val_rolling_2"].iloc[1] == 2
        assert result["val_rolling_2"].iloc[4] == 5
