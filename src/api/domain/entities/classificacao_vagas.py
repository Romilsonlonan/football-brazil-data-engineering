"""Entidade Classificacao com Vagas.

Esta entidade contém campos de classificação + informações de vagas/zonas.
Usada pelo pipeline carga_classificacao_vagas.py.
"""

from dataclasses import dataclass
from typing import Optional

from .time import Time


@dataclass
class ClassificacaoVagas:
    """Entidade que representa a classificação de um time no Brasileirão com vagas."""

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

    # Campos de vagas/zona
    zona: str = ""  # Zona completa (ex: "LIBERTADORES (G4)")
    status_curto: str = ""  # Status curto (ex: "LIB", "SUL-AM")

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

        # Calcula zona automaticamente se não fornecida
        if not self.zona:
            self.zona = self._calcular_zona()

    def _calcular_zona(self) -> str:
        """Calcula a zona do time baseado na posição."""
        if self.posicao <= 4:
            return "LIBERTADORES (G4)"
        elif self.posicao == 5:
            return "PRÉ-LIBERTADORES (G5)"
        elif self.posicao == 6:
            return "LIBERTADORES (G6)"
        elif 7 <= self.posicao <= 12:
            return "SUL-AMERICANA"
        elif 13 <= self.posicao <= 16:
            return "SEM VAGA"
        elif 17 <= self.posicao <= 20:
            return "REBAIXAMENTO"
        else:
            return "INVÁLIDO"

    def _calcular_status_curto(self) -> str:
        """Calcula o status curto baseado na zona."""
        if "LIBERTADORES" in self.zona:
            return "LIB"
        elif "PRÉ-LIBERTADORES" in self.zona:
            return "PRE-LIB"
        elif "SUL-AMERICANA" in self.zona:
            return "SUL-AM"
        elif "REBAIXAMENTO" in self.zona:
            return "REBAIX"
        else:
            return "SEM_VAGA"

    @property
    def aproveitamento(self) -> float:
        """Calcula o percentual de aproveitamento."""
        if self.jogos == 0:
            return 0.0
        return round((self.pontos / (self.jogos * 3)) * 100, 2)

    def get_zona(self) -> str:
        """Retorna a zona do time."""
        return self.zona

    def get_status_curto(self) -> str:
        """Retorna o status curto do time."""
        if not self.status_curto:
            self.status_curto = self._calcular_status_curto()
        return self.status_curto

    def __str__(self) -> str:
        return f"{self.posicao}º - {self.time.nome_reduzido} ({self.pontos} pts) - {self.zona}"
