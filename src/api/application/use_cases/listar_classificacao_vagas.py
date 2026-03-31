"""Use Case: Listar Classificação com Vagas.

Este Use Case é responsável por listar a classificação do Campeonato Brasileiro
com informações de vagas para competições internacionais (Libertadores e Sul-Americana)
e zonas de rebaixamento.

Responsabilidades:
- Listar classificação completa com vagas
- Filtrar times por zona (Libertadores, Sul-Americana, Rebaixamento)
- Obter times classificados para competições internacionais
- Obter times na zona de rebaixamento
- Retornar resumo completo da temporada

DTOs relacionados:
- ClassificacaoVagasDTO: src/api/application/dto/classificacao_vagas_dto.py

Arquivo de dados:
- data/gold/classificacao-vagas.parquet: Contém a classificação com colunas de vagas
"""

from typing import List, Optional

from src.api.domain.entities.classificacao import Classificacao
from src.api.application.dto.classificacao_dto import ClassificacaoDTO


class ListarClassificacaoVagasUseCase:
    """Use case para listar a classificação do Brasileirão com vagas.

    Este use case utiliza os dados do arquivo parquet com vagas que contém:
    - Classificação básica (posicao, time, jogos, vitorias, empates, derrotas, gp, gc, sg, pontos)
    - Colunas de vagas: zona, status_curto, aproveitamento
    """

    def __init__(self):
        """Inicializa o Use Case."""
        self._repository = None

    def set_repository(self, repository):
        """Define o repositório a ser usado.

        Args:
            repository: Instância do repositório ParquetClassificacaoRepository
        """
        self._repository = repository

    def _ensure_repository(self):
        """Garante que o repositório está disponível."""
        if self._repository is None:
            from src.api.infrastructure.repositories.parquet_repository import (
                ParquetClassificacaoRepository,
            )

            self._repository = ParquetClassificacaoRepository()

    def execute(self, temporada: Optional[str] = None) -> List[Classificacao]:
        """
        Executa a listagem da classificação com vagas.

        Args:
            temporada: Ano da temporada (ex: "2026")

        Returns:
            Lista de classificações com vagas
        """
        self._ensure_repository()
        return self._repository.get_all(temporada)

    def get_all(self, temporada: Optional[str] = None) -> List[Classificacao]:
        """
        Retorna toda a classificação com vagas.

        Args:
            temporada: Ano da temporada

        Returns:
            Lista de classificações com vagas
        """
        self._ensure_repository()
        return self._repository.get_all(temporada)

    def get_all_as_dto(self, temporada: Optional[str] = None) -> List[ClassificacaoDTO]:
        """
        Retorna toda a classificação com vagas como DTOs.

        Args:
            temporada: Ano da temporada

        Returns:
            Lista de DTOs de classificação com vagas
        """
        entities = self.get_all(temporada)
        return [ClassificacaoDTO.from_entity(e) for e in entities]

    def get_by_posicao(
        self, posicao: int, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """
        Retorna a classificação de uma posição específica.

        Args:
            posicao: Posição na tabela (1-20)
            temporada: Ano da temporada

        Returns:
            Classificação da posição ou None
        """
        if posicao < 1 or posicao > 20:
            raise ValueError("Posição deve estar entre 1 e 20")

        self._ensure_repository()
        return self._repository.get_by_posicao(posicao, temporada)

    def get_by_time(
        self, nome_time: str, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """
        Retorna a classificação de um time específico.

        Args:
            nome_time: Nome do time
            temporada: Ano da temporada

        Returns:
            Classificação do time ou None
        """
        self._ensure_repository()
        return self._repository.get_by_time(nome_time, temporada)

    def get_libertadores(self, temporada: Optional[str] = None) -> List[Classificacao]:
        """
        Retorna times classificados para a Copa Libertadores.

        Args:
            temporada: Ano da temporada

        Returns:
            Lista de times classificados para Libertadores
        """
        self._ensure_repository()
        return self._repository.get_times_liberadores(temporada)

    def get_libertadores_as_dto(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoDTO]:
        """
        Retorna times classificados para a Libertadores como DTOs.

        Args:
            temporada: Ano da temporada

        Returns:
            Lista de DTOs de times Libertadores
        """
        entities = self.get_libertadores(temporada)
        return [ClassificacaoDTO.from_entity(e) for e in entities]

    def get_sul_americana(self, temporada: Optional[str] = None) -> List[Classificacao]:
        """
         Retorna times classificados para a Copa Sul-Americana.

        Nota: O arquivo classificacao-vagas.parquet não tem método específico para
         Sul-Americana, então filtra times que não são Libertadores nem rebaixados.

         Args:
             temporada: Ano da temporada

         Returns:
             Lista de times classificados para Sul-Americana
        """
        self._ensure_repository()

        # Busca todos os times
        todos = self._repository.get_all(temporada)

        # Filtra times na zona de Sul-Americana
        sulamericana = [
            t
            for t in todos
            if t.zona_computada and "SUL-AMERICANA" in t.zona_computada.upper()
        ]

        return sulamericana

    def get_sul_americana_as_dto(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoDTO]:
        """
        Retorna times classificados para Sul-Americana como DTOs.

        Args:
            temporada: Ano da temporada

        Returns:
            Lista de DTOs de times Sul-Americana
        """
        entities = self.get_sul_americana(temporada)
        return [ClassificacaoDTO.from_entity(e) for e in entities]

    def get_rebaixados(self, temporada: Optional[str] = None) -> List[Classificacao]:
        """
        Retorna times na zona de rebaixamento.

        Args:
            temporada: Ano da temporada

        Returns:
            Lista de times rebaixados
        """
        self._ensure_repository()
        return self._repository.get_times_rebaixados(temporada)

    def get_rebaixados_as_dto(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoDTO]:
        """
        Retorna times rebaixados como DTOs.

        Args:
            temporada: Ano da temporada

        Returns:
            Lista de DTOs de times rebaixados
        """
        entities = self.get_rebaixados(temporada)
        return [ClassificacaoDTO.from_entity(e) for e in entities]

    def get_resumo_temporada(self, temporada: str = "2026") -> dict:
        """
        Retorna um resumo completo da temporada.

        Args:
            temporada: Ano da temporada

        Returns:
            Dicionário com resumo da temporada
        """
        self._ensure_repository()

        classificacao = self._repository.get_all(temporada)
        libertadores = self._repository.get_times_liberadores(temporada)
        rebaixados = self._repository.get_times_rebaixados(temporada)

        # Sul-Americana: times que não são Libertadores nem rebaixados
        sul_americana = [
            t
            for t in classificacao
            if t.zona_computada and "SUL-AMERICANA" in t.zona_computada.upper()
        ]

        return {
            "temporada": temporada,
            "total_times": len(classificacao),
            "libertadores": {
                "quantidade": len(libertadores),
                "times": [t.time.nome for t in libertadores],
            },
            "sul_americana": {
                "quantidade": len(sul_americana),
                "times": [t.time.nome for t in sul_americana],
            },
            "rebaixados": {
                "quantidade": len(rebaixados),
                "times": [t.time.nome for t in rebaixados],
            },
            "classificacao_completa": [
                {
                    "posicao": c.posicao,
                    "time": c.time.nome,
                    "pontos": c.pontos,
                    "zona": c.zona_computada,
                    "status": c.status_curto,
                }
                for c in classificacao
            ],
        }
