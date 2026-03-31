"""Use Case para buscar classificação - Application Layer"""
from typing import Protocol

import pandas as pd

from dashboard.domain.entities.classificacao import ClassificacaoTime


class ClassificacaoRepository(Protocol):
    """Protocolo para repositório de classificação."""

    def get_classificacao_dataframe(self) -> pd.DataFrame:
        """Retorna a classificação como DataFrame."""
        ...


class BuscarClassificacaoUseCase:
    """Use case para buscar dados de classificação."""

    def __init__(self, repository: ClassificacaoRepository) -> None:
        self._repository = repository

    def execute(self) -> pd.DataFrame:
        """Executa o use case e retorna os dados de classificação."""
        return self._repository.get_classificacao_dataframe()

    def get_classificacao_por_time(self, nome_time: str) -> pd.DataFrame:
        """Retorna os dados de um time específico."""
        df = self._repository.get_classificacao_dataframe()
        return df[df["time"].str.contains(nome_time, case=False)]

    def get_top_times(self, limit: int = 4) -> pd.DataFrame:
        """Retorna os primeiros times (G4)."""
        df = self._repository.get_classificacao_dataframe()
        return df.head(limit)

    def get_times_rebaixados(self, limit: int = 4) -> pd.DataFrame:
        """Retorna os times na zona de rebaixamento."""
        df = self._repository.get_classificacao_dataframe()
        return df.tail(limit)