"""Entidade Classificacao Base.

Esta entidade contém apenas os campos básicos de classificação (stats).
Usada por pipelines que não precisam de informações de vagas/zonas.
"""

from dataclasses import dataclass
from typing import Optional

from .time import Time


@dataclass
class ClassificacaoBase:
    """Entidade que representa a classificação básica de um time no Brasileirão."""

    posicao: int
    time: Time
    jogos: int = 0
    vitorias: int = 0
    empates: int = 0
    defeats: int = 0
    gp: int = 0  # Gols Pró
    gc: int = 0  # Gols Contra
    sg: int = 0  # Saldo de Gols
    pontos: int = 0

    # Campos opcionais de metadata
    id: Optional[int] = None
    temporada: Optional[str] = None

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.posicao < 1 or self.posicao > 20:
            raise ValueError("Posição deve estar entre 1 e 20")

        if self.jogos < 0:
            raise ValueError("Número de jogos não pode ser negativo")

        # Recalcula pontos se não for fornecido
        if self.pontos == 0 and (self.vitorias > 0 or self.empates > 0):
            self.pontos = (self.vitorias * 3) + (self.empates * 1)

        # Recalcula saldo de gol se não for fornecido
        if self.sg == 0 and (self.gp > 0 or self.gc > 0):
            self.sg = self.gp - self.gc

    @property
    def aproveitamento(self) -> float:
        """Calcula o percentual de aproveitamento."""
        if self.jogos == 0:
            return 0.0
        return round((self.pontos / (self.jogos * 3)) * 100, 2)

    def get_status(self) -> str:
        """Retorna o status simples do time na competição."""
        if self.posicao <= 4:
            return "LIBERTADORES (G4)"
        elif self.posicao == 5:
            return "PRÉ-LIBERTADORES (G5)"
        elif self.posicao <= 6:
            return "LIBERTADORES (G6)"
        elif self.posicao <= 12:
            return "SUL-AMERICANA"
        elif self.posicao >= 17:
            return "REBAIXAMENTO"
        else:
            return "SEM_REBAIXAMENTO"

    def __str__(self) -> str:
        return f"{self.posicao}º - {self.time.nome_reduzido} ({self.pontos} pts)"
