"""Adapters de compatibilidade com sistemas legados.

Este módulo fornece adaptadores para manter compatibilidade
com os sistemas existentes (API, Dashboard) enquanto
a migração para DDD acontece gradualmente.

PRINCÍPIO: Adapter Pattern (GoF)
- Traduz entity DDD ↔ formatos legados
- Permite migração gradual sem QUEBRAR sistemas
"""

from dataclasses import dataclass
from .entities import Classificacao as ClassificacaoEntity
from .value_objects import Posicao, Aproveitamento


@dataclass
class ClassificacaoLegacy:
    """Adapter para Compatibility com ClassificacaoTime (dashboard).

    Uso:
        from src.contexts.classificacao.domain.adapters import ClassificacaoLegacy
        legacy = ClassificacaoLegacy.from_entity(entity)
    """

    posicao: int
    time: str
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    goals_pro: int
    goals_contra: int
    saldo_gols: int
    pontos: int
    aproveitamento: float

    @classmethod
    def from_entity(
        cls,
        entity: ClassificacaoEntity,
        posicao: int,
        calc_aproveitamento: any = None,
    ) -> "ClassificacaoLegacy":
        """Cria adapter a partir de entity DDD."""
        apr = (
            calc_aperveitamento(entity)
            if calc_aproveitamento
            else (entity.pontos / (entity.jogos * 3) * 100 if entity.jogos > 0 else 0.0)
        )
        return cls(
            posicao=posicao,
            time=entity.time,
            jogos=entity.jogos,
            vitorias=entity.vitorias,
            empates=entity.empates,
            defeats=entity.derrotas,
            goals_pro=entity.goals_pro,
            goals_contra=entity.goals_contra,
            saldo_gols=entity.saldo_goals,
            pontos=entity.pontos,
            aproveitamento=round(apr, 2),
        )

    def to_legacy_dict(self) -> dict:
        """Retorna dicionário compatibility com sistema legado."""
        return {
            "Posição": self.posicao,
            "Time": self.time,
            "Jogos": self.jogos,
            "Vitorias": self.vitorias,
            "Empates": self.empates,
            "Derrotas": self.derrotas,
            "GolsPro": self.goals_pro,
            "GolsContra": self.goals_contra,
            "SaldoGols": self.saldo_gols,
            "Pontos": self.pontos,
        }


@dataclass
class TimeLegacy:
    """Adapter para compatibility com Time (API/Dashboard).

    Uso:
        from src.contexts.classificacao.domain.adapters import TimeLegacy
        legacy = TimeLegacy.from_entity(entity)
    """

    id: str
    nome: str
    abreviacao: str | None = None
    estadio: str | None = None

    @classmethod
    def from_entity(cls, entity: any) -> "TimeLegacy":
        """Cria adapter a partir de entity."""
        return cls(
            id=entity.id if hasattr(entity, "id") else entity.nome,
            nome=entity.nome,
            abreviacao=entity.abreviacao if hasattr(entity, "abreviacao") else None,
            estadio=entity.estadio if hasattr(entity, "estadio") else None,
        )
