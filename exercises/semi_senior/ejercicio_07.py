"""
RETO SEMI-SENIOR #07 — Listas + Funciones
Tema: Funciones de orden superior
"""

METADATA = {
    "id": "ss_07",
    "nivel_rol": "semi_senior",
    "tema": "funciones",
    "enunciado": "Escribe una función `pipeline(*functions)` que retorne una nueva función. Al llamarla con un valor, aplica las funciones dadas en orden pasando cada resultado a la siguiente. pipeline(f, g, h)(x) = h(g(f(x))).",
    "andamiaje_minimo": "Necesitas retornar una función que aplique las funciones en cadena, una tras otra.",
    "andamiaje_parcial": "La función interna recibe un `valor`. Usa un for para recorrer `functions` actualizando `valor = f(valor)` en cada iteración. Al final retorna `valor`.",
    "andamiaje_completo": "Define `def pipeline(*functions):` y dentro una closure: `def run(valor): [valor := f(valor) for f in functions]; return valor`. O más claro: un for loop que actualiza `valor`. Retorna `run`.",
}

# ── Ejemplos esperados ────────────────────────────────────────────────────────
# doble = lambda x: x * 2
# mas_uno = lambda x: x + 1
# al_str = lambda x: str(x)
# pipeline(doble, mas_uno, al_str)(3) → "7"   (3*2=6, 6+1=7, str(7)="7")
# pipeline()(5)                        → 5    (sin funciones, retorna el valor)


def solucion_referencia(*functions):
    """Solución de referencia (no modificar)."""
    def run(valor):
        for f in functions:
            valor = f(valor)
        return valor
    return run


def solucion_estudiante(*functions):
    """
    TU SOLUCIÓN AQUÍ.
    Retorna una función que aplica `functions` en cadena al valor dado.

    Args:
        *functions: funciones a encadenar (cada una recibe un argumento)

    Returns:
        Función que aplica el pipeline
    """
    pass
