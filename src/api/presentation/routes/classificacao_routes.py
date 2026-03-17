"""Rotas para classificação."""

from typing import Optional
from dataclasses import dataclass

# Estrutura de rota simples (sem FastAPI dependência)
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


class ClassificacaoRoutes:
    """Rotas para classificação."""
    
    def __init__(self, controller):
        self._controller = controller
    
    def get_classificacao(
        self, 
        temporada: Optional[str] = "2026",
        zona: Optional[str] = None
    ) -> Response:
        """
        GET /classificacao
        
        Retorna a classificação completa do Brasileirão.
        
        Query params:
            - temporada: Ano da temporada (padrão: 2026)
            - zona: Filtrar por zona (LIBRERTADORES, SUL-AMERICANA, REBAIXAMENTO)
        """
        result = self._controller.listar_classificacao(temporada, zona)
        return Response(
            status_code=200 if result["success"] else 400,
            body=result
        )
    
    def get_posicao(self, posicao: int, temporada: str = "2026") -> Response:
        """
        GET /classificacao/posicao/{posicao}
        
        Retorna a classificação de uma posição específica.
        """
        result = self._controller.buscar_por_posicao(posicao, temporada)
        return Response(
            status_code=200 if result["success"] else 404,
            body=result
        )
    
    def get_time(self, nome_time: str, temporada: str = "2026") -> Response:
        """
        GET /classificacao/time/{nome_time}
        
        Retorna a classificação de um time específico.
        """
        result = self._controller.buscar_por_time(nome_time, temporada)
        return Response(
            status_code=200 if result["success"] else 404,
            body=result
        )
    
    def get_vagas(self, temporada: str = "2026") -> Response:
        """
        GET /classificacao/vagas
        
        Retorna a configuração de vagas para a temporada.
        """
        result = self._controller.get_vagas(temporada)
        return Response(
            status_code=200,
            body=result
        )
