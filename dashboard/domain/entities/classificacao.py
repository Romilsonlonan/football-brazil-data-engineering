"""Entidade Classificacao - Domain Layer"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificacaoTime:
    """Entidade que representa a classificação de um time."""
    posicao: int
    time: str
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gols_pro: int
    saldo_gols: int
    pontos: int

    @property
    def aproveitamento(self) -> float:
        """Calcula o aproveitamento percentual do time."""
        if self.jogos == 0:
            return 0.0
        return (self.pontos / (self.jogos * 3)) * 100

    @property
    def numero_resultados(self) -> int:
        """Retorna o total de jogos (vitórias + empates + derrotas)."""
        return self.jogos