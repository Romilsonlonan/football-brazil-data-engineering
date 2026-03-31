"""Interface de repositório - Domain Layer"""
from abc import ABC, abstractmethod

import pandas as pd

from dashboard.domain.entities.classificacao import ClassificacaoTime
from dashboard.domain.entities.jogador import Jogador


class ClassificacaoRepository(ABC):
    """Interface para repositório de classificação."""

    @abstractmethod
    def get_classificacao_completa(self) -> list[ClassificacaoTime]:
        """Retorna a classificação completa."""
        pass

    @abstractmethod
    def get_classificacao_dataframe(self) -> pd.DataFrame:
        """Retorna a classificação como DataFrame."""
        pass


class ElencoRepository(ABC):
    """Interface para repositório de elenco."""

    @abstractmethod
    def get_elenco_completo(self) -> list[Jogador]:
        """Retorna o elenco completo de todos os times."""
        pass

    @abstractmethod
    def get_elenco_por_time(self, nome_time: str) -> list[Jogador]:
        """Retorna o elenco de um time específico."""
        pass

    @abstractmethod
    def get_elenco_dataframe(self) -> pd.DataFrame:
        """Retorna o elenco como DataFrame."""
        pass