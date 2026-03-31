"""Injeção de dependências."""

from src.api.presentation.controllers.classificacao_controller import (
    ClassificacaoController,
)
from src.api.presentation.routes.classificacao_routes import ClassificacaoRoutes


# Instâncias singleton (simples injeção de dependência)
_classificacao_controller: ClassificacaoController = None
_classificacao_routes: ClassificacaoRoutes = None


def get_classificacao_controller() -> ClassificacaoController:
    """Retorna o controller de classificação (singleton)."""
    global _classificacao_controller
    if _classificacao_controller is None:
        _classificacao_controller = ClassificacaoController()
    return _classificacao_controller


def get_classificacao_routes() -> ClassificacaoRoutes:
    """Retorna as rotas de classificação (singleton)."""
    global _classificacao_routes
    if _classificacao_routes is None:
        controller = get_classificacao_controller()
        _classificacao_routes = ClassificacaoRoutes(controller)
    return _classificacao_routes
