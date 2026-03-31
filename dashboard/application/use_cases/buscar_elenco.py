"""Use Case para buscar elenco - Application Layer"""
from typing import Protocol

import pandas as pd


class ElencoRepository(Protocol):
    """Protocolo para repositório de elenco."""

    def get_elenco_dataframe(self) -> pd.DataFrame:
        """Retorna o elenco como DataFrame."""
        ...


class BuscarElencoUseCase:
    """Use case para buscar dados de elenco."""

    def __init__(self, repository: ElencoRepository) -> None:
        self._repository = repository

    def execute(self) -> pd.DataFrame:
        """Executa o use case e retorna os dados do elenco."""
        return self._repository.get_elenco_dataframe()

    def get_elenco_por_time(self, nome_time: str) -> pd.DataFrame:
        """Retorna o elenco de um time específico."""
        df = self._repository.get_elenco_dataframe()
        return df[df["Time"].str.contains(nome_time, case=False)]

    def get_times(self) -> list[str]:
        """Retorna a lista de todos os times."""
        df = self._repository.get_elenco_dataframe()
        return sorted(df["Time"].unique().tolist())