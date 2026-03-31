"""Entidades do domínio."""

from .classificacao import Classificacao
from .classificacao_base import ClassificacaoBase
from .classificacao_vagas import ClassificacaoVagas
from .time import Time
from .vagas import VagasConfig, ClassificacaoService

__all__ = [
    "Classificacao",
    "ClassificacaoBase",
    "ClassificacaoVagas",
    "Time",
    "VagasConfig",
    "ClassificacaoService",
]
