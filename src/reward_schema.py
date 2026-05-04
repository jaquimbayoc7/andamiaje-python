"""
src/reward_schema.py
Esquema del Reward Model para RLHF.
Define estructuras de datos para preferencias, rúbricas y ejercicios con andamiaje.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class RubricaPedagogica:
    """Rúbrica de evaluación pedagógica (escala 1-5 por dimensión)."""

    claridad: int = 3
    progresion: int = 3
    correccion: int = 3
    motivacion: int = 3
    autonomia: int = 3
    eficiencia_algoritmica: int = 3

    DIMENSIONES = [
        "claridad", "progresion", "correccion",
        "motivacion", "autonomia", "eficiencia_algoritmica",
    ]

    def score_total(self) -> float:
        """Score normalizado 0.0–1.0 sobre las 6 dimensiones."""
        total = sum(
            getattr(self, dim) for dim in self.DIMENSIONES
        )
        return round(total / (len(self.DIMENSIONES) * 5), 4)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "RubricaPedagogica":
        campos_validos = {
            k: int(v) for k, v in d.items()
            if k in cls.DIMENSIONES
        }
        return cls(**campos_validos)


@dataclass
class ComparacionAB:
    """Registro de una comparación A/B para entrenamiento del reward model."""

    ejercicio_id: str
    nivel: str
    tema: str
    perfil_id: str
    respuesta_a: str
    respuesta_b: str
    preferencia: str                               # "A" o "B"
    reward_score_a: float
    reward_score_b: float
    rubrica: RubricaPedagogica = field(default_factory=RubricaPedagogica)
    justificacion: str = ""
    fuente: str = "claude_haiku"                  # "claude_haiku" | "manual"

    def to_jsonl_line(self) -> str:
        """Serializa a línea JSONL para el reward model."""
        d = asdict(self)
        d["rubrica_score_total"] = self.rubrica.score_total()
        return json.dumps(d, ensure_ascii=False)

    @classmethod
    def from_ab_resultado(
        cls,
        resultado: dict,
        ejercicio_id: str,
        tema: str,
    ) -> "ComparacionAB":
        """Construye desde el output de ab_generator.generar_par_ab()."""
        return cls(
            ejercicio_id=ejercicio_id,
            nivel=resultado.get("nivel", "junior"),
            tema=tema,
            perfil_id=resultado.get("perfil_id", ""),
            respuesta_a=resultado.get("respuesta_a", ""),
            respuesta_b=resultado.get("respuesta_b", ""),
            preferencia=resultado.get("preferencia", "A"),
            reward_score_a=float(resultado.get("reward_score_a", 0.5)),
            reward_score_b=float(resultado.get("reward_score_b", 0.5)),
            rubrica=RubricaPedagogica.from_dict(resultado.get("rubrica", {})),
            justificacion=resultado.get("justificacion", ""),
        )


@dataclass
class EjercicioConAndamiaje:
    """Ejercicio con sus tres niveles de andamiaje generados en español."""

    id: str
    nivel_rol: str           # junior | semi_senior | senior
    tema: str
    enunciado_en: str        # Enunciado original en inglés
    solucion_ref: str        # Código Python de referencia
    andamiaje_minimo: str    # Pista mínima en español
    andamiaje_parcial: str   # Pista parcial en español
    andamiaje_completo: str  # Guía completa en español
    tests_esperados: list = field(default_factory=list)

    def to_sft_jsonl(self) -> list:
        """
        Genera 3 líneas JSONL para SFT (una por nivel de andamiaje).
        Formato instruction-following listo para entrenamiento.
        """
        lineas = []
        for nivel_and, hint in [
            ("mínimo", self.andamiaje_minimo),
            ("parcial", self.andamiaje_parcial),
            ("completo", self.andamiaje_completo),
        ]:
            registro = {
                "id": f"{self.id}_{nivel_and}",
                "nivel_rol": self.nivel_rol,
                "tema": self.tema,
                "nivel_andamiaje": nivel_and,
                "instruction": self.enunciado_en,
                "input": (
                    f"Perfil del candidato: {self.nivel_rol}. "
                    f"Nivel de andamiaje requerido: {nivel_and}."
                ),
                "output": hint,
                "solucion_referencia": self.solucion_ref,
            }
            lineas.append(json.dumps(registro, ensure_ascii=False))
        return lineas
