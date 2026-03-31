"""Interfaces de repositório para classificação."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.api.domain.entities.classificacao import Classificacao


class IClassificacaoRepository(ABC):
    """Interface para o repositório de classificação."""

    @abstractmethod
    def get_all(self, temporada: Optional[str] = None) -> List[Classificacao]:
        """Retorna toda a classificação."""
        pass

    @abstractmethod
    def get_by_posicao(
        self, posicao: int, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """Retorna a classificação de um time pela posição."""
        pass

    @abstractmethod
    def get_by_time(
        self, nome_time: str, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """Retorna a classificação de um time pelo nome."""
        pass

    @abstractmethod
    def get_times_rebaixados(
        self, temporada: Optional[str] = None
    ) -> List[Classificacao]:
        """Retorna os times na zona de rebaixamento."""
        pass

    @abstractmethod
    def get_times_liberadores(
        self, temporada: Optional[str] = None
    ) -> List[Classificacao]:
        """Retorna os times na zona de Libertadores."""
        pass
