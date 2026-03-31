"""Use Case: Listar Classificação."""

from typing import List, Optional

from src.api.domain.entities.classificacao import Classificacao
from src.api.domain.repositories.interface import IClassificacaoRepository


class ListarClassificacaoUseCase:
    """Use case para listar a classificação do Brasileirão."""

    def __init__(self, repository: IClassificacaoRepository):
        self._repository = repository

    def execute(
        self, temporada: Optional[str] = None, zona: Optional[str] = None
    ) -> List[Classificacao]:
        """
        Executa a listagem da classificação.

        Args:
            temporada: Ano da temporada (ex: "2026")
            zona: Filtrar por zona (LIBRERTADORES, SUL-AMERICANA, REBAIXAMENTO)

        Returns:
            Lista de classificações
        """
        if zona:
            return self._filtrar_por_zona(zona, temporada)

        return self._repository.get_all(temporada)

    def _filtrar_por_zona(
        self, zona: str, temporada: Optional[str] = None
    ) -> List[Classificacao]:
        """Filtra a classificação por zona."""
        zona_upper = zona.upper()

        if "LIBERTADORES" in zona_upper:
            return self._repository.get_times_liberadores(temporada)
        elif "REBAIXAMENTO" in zona_upper:
            return self._repository.get_times_rebaixados(temporada)

        return self._repository.get_all(temporada)

    def get_by_posicao(
        self, posicao: int, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """Retorna a classificação de uma posição específica."""
        if posicao < 1 or posicao > 20:
            raise ValueError("Posição deve estar entre 1 e 20")

        return self._repository.get_by_posicao(posicao, temporada)

    def get_by_time(
        self, nome_time: str, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """Retorna a classificação de um time específico."""
        return self._repository.get_by_time(nome_time, temporada)
