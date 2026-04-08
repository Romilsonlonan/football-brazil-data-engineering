"""Entidades do Domínio de Classificação"""

from dataclasses import dataclass

from .value_objects import Pontos, Posicao, Aproveitamento


@dataclass(frozen=True)
class Time:
    """Entidade que representa um time de futebol."""

    id: str
    nome: str
    abreviacao: str | None = None
    estadio: str | None = None


@dataclass(frozen=True)
class Classificacao:
    """Entidade que representa a classificação de um time no Campeonato Brasileiro.

    Esta é uma entity 'anêmica' - contém apenas dados.
    As regras de negócio estão no Domain Service.
    """

    time: str
    pontos: int
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    goals_pro: int
    goals_contra: int
    saldo_goals: int

    @property
    def pontos_por_vitoria(self) -> Pontos:
        return Pontos(self.pontos)

    @property
    def saldo(self) -> int:
        return self.saldo_goals

    def __post_init__(self):
        jogos_calc = self.vitorias + self.empates + self.derrotas
        if jogos_calc != self.jogos:
            raise ValueError(
                f"Jogos inconsistency: {self.jogos} != {self.vitorias + self.empates + self.derrotas}"
            )


@dataclass(frozen=True)
class ResultadoJogo:
    """Entidade que representa o resultado de um jogo."""

    time_casa: str
    time_fora: str
    placar_casa: int
    placar_fora: int
    mandante_venceu: bool = False
    visitante_venceu: bool = False
    empatou: bool = False

    def __post_init__(self):
        self.mandante_venceu = self.placar_casa > self.placar_fora
        self.visitante_venceu = self.placar_fora > self.placar_casa
        self.empatou = self.placar_casa == self.placar_fora
