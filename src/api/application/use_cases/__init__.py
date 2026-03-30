"""Use Cases."""
from .listar_classificacao import ListarClassificacaoUseCase
from .listar_classificacao_vagas import ListarClassificacaoVagasUseCase
from .criar_classificacao import CriarClassificacaoUseCase
from .atualizar_classificacao import AtualizarClassificacaoUseCase

__all__ = [
    "ListarClassificacaoUseCase",
    "ListarClassificacaoVagasUseCase",
    "CriarClassificacaoUseCase", 
    "AtualizarClassificacaoUseCase"
]
