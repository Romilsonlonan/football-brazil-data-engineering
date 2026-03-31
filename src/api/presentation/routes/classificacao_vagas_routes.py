"""Rotas para classificação com vagas.

Este arquivo contém as rotas para endpoints específicos de classificação
com vagas em competições internacionais (Libertadores e Sul-Americana).

Rotas disponíveis:
- GET /classificacao-vagas - Classificação completa com vagas
- GET /classificacao-vagas/libertadores - Times classificados para Libertadores
- GET /classificacao-vagas/sul-americana - Times classificados para Sul-Americana
- GET /classificacao-vagas/rebaixados - Times na zona de rebaixamento
- GET /classificacao-vagas/resumo - Resumo completo da temporada
- GET /classificacao-vagas/posicao/{posicao} - Busca por posição
- GET /classificacao-vagas/time/{nome_time} - Busca por time
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Request:
    """Request simples para as rotas."""

    query_params: dict = None

    def __post_init__(self):
        if self.query_params is None:
            self.query_params = {}


@dataclass
class Response:
    """Response simples para as rotas."""

    status_code: int
    body: dict

    def json(self):
        return self.body


class ClassificacaoVagasRoutes:
    """Rotas para classificação com vagas."""

    def __init__(self, controller):
        """Inicializa as rotas com o controller."""
        self._controller = controller

    def get_classificacao_completa(
        self, temporada: Optional[str] = "2026", usar_dto: bool = False
    ) -> Response:
        """
        GET /classificacao-vagas

        Retorna a classificação completa do Brasileirão com vagas.

        Query params:
            - temporada: Ano da temporada (padrão: 2026)
            - usar_dto: Se true, retorna DTOs serializáveis
        """
        result = self._controller.listar_classificacao_completa(temporada, usar_dto)
        return Response(status_code=200 if result["success"] else 400, body=result)

    def get_libertadores(
        self, temporada: Optional[str] = "2026", usar_dto: bool = False
    ) -> Response:
        """
        GET /classificacao-vagas/libertadores

        Retorna times classificados para a Copa Libertadores.

        Query params:
            - temporada: Ano da temporada (padrão: 2026)
            - usar_dto: Se true, retorna DTOs serializáveis
        """
        result = self._controller.listar_libertadores(temporada, usar_dto)
        return Response(status_code=200 if result["success"] else 400, body=result)

    def get_sul_americana(
        self, temporada: Optional[str] = "2026", usar_dto: bool = False
    ) -> Response:
        """
        GET /classificacao-vagas/sul-americana

        Retorna times classificados para a Copa Sul-Americana.

        Query params:
            - temporada: Ano da temporada (padrão: 2026)
            - usar_dto: Se true, retorna DTOs serializáveis
        """
        result = self._controller.listar_sul_americana(temporada, usar_dto)
        return Response(status_code=200 if result["success"] else 400, body=result)

    def get_rebaixados(
        self, temporada: Optional[str] = "2026", usar_dto: bool = False
    ) -> Response:
        """
        GET /classificacao-vagas/rebaixados

        Retorna times na zona de rebaixamento.

        Query params:
            - temporada: Ano da temporada (padrão: 2026)
            - usar_dto: Se true, retorna DTOs serializáveis
        """
        result = self._controller.listar_rebaixados(temporada, usar_dto)
        return Response(status_code=200 if result["success"] else 400, body=result)

    def get_resumo(self, temporada: str = "2026") -> Response:
        """
        GET /classificacao-vagas/resumo

        Retorna um resumo completo da temporada.

        Query params:
            - temporada: Ano da temporada (padrão: 2026)
        """
        result = self._controller.get_resumo_temporada(temporada)
        return Response(status_code=200 if result["success"] else 400, body=result)

    def get_posicao(self, posicao: int, temporada: str = "2026") -> Response:
        """
        GET /classificacao-vagas/posicao/{posicao}

        Retorna a classificação de uma posição específica.

        Path params:
            - posicao: Posição na tabela (1-20)

        Query params:
            - temporada: Ano da temporada (padrão: 2026)
        """
        result = self._controller.buscar_por_posicao(posicao, temporada)
        return Response(status_code=200 if result["success"] else 404, body=result)

    def get_time(self, nome_time: str, temporada: str = "2026") -> Response:
        """
        GET /classificacao-vagas/time/{nome_time}

        Retorna a classificação de um time específico.

        Path params:
            - nome_time: Nome do time

        Query params:
            - temporada: Ano da temporada (padrão: 2026)
        """
        result = self._controller.buscar_por_time(nome_time, temporada)
        return Response(status_code=200 if result["success"] else 404, body=result)
