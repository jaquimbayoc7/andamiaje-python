"""
RETO SENIOR #01 — Diccionarios
Tema: Diccionarios y estructuras de datos avanzadas
"""

METADATA = {
    "id": "sr_01",
    "nivel_rol": "senior",
    "tema": "diccionarios",
    "enunciado": "Implementa una clase `LFUDict(capacity)` — un dict de tamaño fijo que expulsa el elemento Menos Frecuentemente Usado (LFU) cuando está lleno. Si dos elementos tienen la misma frecuencia, expulsa el menos recientemente usado. Métodos: get(key) → valor o -1; put(key, value).",
    "andamiaje_minimo": "Necesitas rastrear la frecuencia de acceso de cada clave y poder identificar rápidamente cuál es la de menor frecuencia.",
    "andamiaje_parcial": "Mantén tres estructuras: `data` (clave→valor), `freq` (clave→frecuencia), `freq_map` (frecuencia→OrderedDict de claves). Actualiza `min_freq` al insertar y al acceder.",
    "andamiaje_completo": "Usa `defaultdict(OrderedDict)` para `freq_map`. En `get`: actualiza frecuencia. En `put`: si lleno, expulsa `freq_map[min_freq].popitem(last=False)`. Al insertar nuevo, `min_freq = 1`. Al actualizar, mueve de `freq_map[f]` a `freq_map[f+1]`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# lfu = LFUDict(2)
# lfu.put(1, 1); lfu.put(2, 2)
# lfu.get(1) → 1          (freq de 1 ahora es 2)
# lfu.put(3, 3)            (expulsa 2, que tiene freq 1)
# lfu.get(2) → -1
# lfu.get(3) → 3


from collections import defaultdict, OrderedDict


def solucion_referencia(capacidad):
    """Retorna una instancia de LFUDict con la capacidad dada (no modificar)."""

    class LFUDict:
        def __init__(self, cap):
            self.cap = cap
            self.data = {}
            self.freq = {}
            self.freq_map = defaultdict(OrderedDict)
            self.min_freq = 0

        def _update_freq(self, key):
            f = self.freq[key]
            del self.freq_map[f][key]
            if not self.freq_map[f] and f == self.min_freq:
                self.min_freq += 1
            self.freq[key] = f + 1
            self.freq_map[f + 1][key] = True

        def get(self, key):
            if key not in self.data:
                return -1
            self._update_freq(key)
            return self.data[key]

        def put(self, key, value):
            if self.cap <= 0:
                return
            if key in self.data:
                self.data[key] = value
                self._update_freq(key)
            else:
                if len(self.data) >= self.cap:
                    evicted, _ = self.freq_map[self.min_freq].popitem(last=False)
                    del self.data[evicted]
                    del self.freq[evicted]
                self.data[key] = value
                self.freq[key] = 1
                self.freq_map[1][key] = True
                self.min_freq = 1

    return LFUDict(capacidad)


def solucion_estudiante(capacidad):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna una instancia de LFUDict con los métodos get(key) y put(key, value).

    Args:
        capacidad: tamaño máximo del cache

    Returns:
        Instancia de LFUDict
    """
    pass
