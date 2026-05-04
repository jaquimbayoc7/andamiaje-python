"""
tests/test_junior.py
Tests pytest para los 10 ejercicios Junior (fundamentos Python).
Se prueban las soluciones de referencia — siempre deben pasar.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exercises.junior.ejercicio_01 import solucion_referencia as swap
from exercises.junior.ejercicio_02 import solucion_referencia as remove_duplicates
from exercises.junior.ejercicio_03 import solucion_referencia as second_largest
from exercises.junior.ejercicio_04 import solucion_referencia as unpack_nested
from exercises.junior.ejercicio_05 import solucion_referencia as count_in_nested
from exercises.junior.ejercicio_06 import solucion_referencia as invert_dict
from exercises.junior.ejercicio_07 import solucion_referencia as merge_sum
from exercises.junior.ejercicio_08 import solucion_referencia as words_only_in_a
from exercises.junior.ejercicio_09 import solucion_referencia as sum_numerics
from exercises.junior.ejercicio_10 import solucion_referencia as flatten_one_level


# ── Jr 01: Swap ───────────────────────────────────────────────────────────────
class TestJr01Swap:
    def test_enteros(self):
        assert swap(1, 2) == (2, 1)

    def test_strings(self):
        assert swap("hola", "mundo") == ("mundo", "hola")

    def test_mismo_valor(self):
        assert swap(5, 5) == (5, 5)

    def test_listas(self):
        assert swap([1, 2], [3, 4]) == ([3, 4], [1, 2])

    def test_tipos_mixtos(self):
        assert swap(1, "x") == ("x", 1)


# ── Jr 02: Remove Duplicates ──────────────────────────────────────────────────
class TestJr02RemoveDuplicates:
    def test_basico(self):
        assert remove_duplicates([1, 2, 2, 3, 1]) == [1, 2, 3]

    def test_strings(self):
        assert remove_duplicates(["a", "b", "a"]) == ["a", "b"]

    def test_lista_vacia(self):
        assert remove_duplicates([]) == []

    def test_todos_iguales(self):
        assert remove_duplicates([5, 5, 5]) == [5]

    def test_orden_preservado(self):
        assert remove_duplicates([3, 1, 2, 1, 3]) == [3, 1, 2]


# ── Jr 03: Second Largest ─────────────────────────────────────────────────────
class TestJr03SecondLargest:
    def test_basico(self):
        assert second_largest([3, 1, 4, 1, 5, 9]) == 5

    def test_todos_iguales(self):
        assert second_largest([1, 1]) is None

    def test_un_elemento(self):
        assert second_largest([5]) is None

    def test_negativos(self):
        assert second_largest([-1, -3, -2]) == -2

    def test_dos_distintos(self):
        assert second_largest([10, 20]) == 10


# ── Jr 04: Unpack Nested ──────────────────────────────────────────────────────
class TestJr04UnpackNested:
    def test_enteros(self):
        assert unpack_nested(((1, 2), (3, 4))) == (1, 2, 3, 4)

    def test_strings(self):
        assert unpack_nested((("a", "b"), ("c", "d"))) == ("a", "b", "c", "d")

    def test_mixto(self):
        result = unpack_nested(((True, 0), (None, 1)))
        assert result == (True, 0, None, 1)


# ── Jr 05: Count in Nested ────────────────────────────────────────────────────
class TestJr05CountInNested:
    def test_multiples_ocurrencias(self):
        assert count_in_nested(((1, 2, 1), (3, 1)), 1) == 3

    def test_sin_ocurrencias(self):
        assert count_in_nested(((1, 2), (3, 4)), 5) == 0

    def test_strings(self):
        assert count_in_nested((("a", "a"), ("a",)), "a") == 3

    def test_vacio(self):
        assert count_in_nested((), 1) == 0


# ── Jr 06: Invert Dict ────────────────────────────────────────────────────────
class TestJr06InvertDict:
    def test_sin_duplicados(self):
        assert invert_dict({"a": 1, "b": 2}) == {1: ["a"], 2: ["b"]}

    def test_con_duplicados(self):
        result = invert_dict({"a": 1, "b": 1})
        assert set(result[1]) == {"a", "b"}

    def test_vacio(self):
        assert invert_dict({}) == {}

    def test_string_valor(self):
        assert invert_dict({"x": "y"}) == {"y": ["x"]}


# ── Jr 07: Merge Sum ──────────────────────────────────────────────────────────
class TestJr07MergeSum:
    def test_basico(self):
        assert merge_sum({"a": 1, "b": 2}, {"b": 3, "c": 4}) == {"a": 1, "b": 5, "c": 4}

    def test_d1_vacio(self):
        assert merge_sum({}, {"x": 10}) == {"x": 10}

    def test_d2_vacio(self):
        assert merge_sum({"k": 5}, {}) == {"k": 5}

    def test_suma_a_cero(self):
        assert merge_sum({"a": 1}, {"a": -1}) == {"a": 0}


# ── Jr 08: Words Only In A ────────────────────────────────────────────────────
class TestJr08WordsOnlyInA:
    def test_basico(self):
        assert words_only_in_a("hello world foo", "world bar") == {"hello", "foo"}

    def test_sin_diferencia(self):
        assert words_only_in_a("a b c", "a b c") == set()

    def test_case_insensitive(self):
        result = words_only_in_a("Python is great", "Java is ok")
        assert result == {"python", "great"}

    def test_texto_a_vacio(self):
        assert words_only_in_a("", "hello") == set()


# ── Jr 09: Sum Numerics ───────────────────────────────────────────────────────
class TestJr09SumNumerics:
    def test_solo_enteros(self):
        assert sum_numerics(1, 2, 3) == 6

    def test_mixto(self):
        assert sum_numerics(1, "hello", 2.5, None) == 3.5

    def test_sin_args(self):
        assert sum_numerics() == 0

    def test_excluye_bool(self):
        assert sum_numerics(True, 1, 2) == 3

    def test_sin_numericos(self):
        assert sum_numerics("a", "b") == 0


# ── Jr 10: Flatten One Level ──────────────────────────────────────────────────
class TestJr10FlattenOneLevel:
    def test_basico(self):
        assert flatten_one_level([[1, 2], [3, 4]]) == [1, 2, 3, 4]

    def test_un_nivel_solamente(self):
        assert flatten_one_level([[1, 2], [3, [4]]]) == [1, 2, 3, [4]]

    def test_mixto(self):
        assert flatten_one_level([1, [2, 3], 4]) == [1, 2, 3, 4]

    def test_vacio(self):
        assert flatten_one_level([]) == []

    def test_sublista_vacia(self):
        assert flatten_one_level([[]]) == []
