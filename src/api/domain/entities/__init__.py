"""Entidades do domínio."""
from .classificacao import Classificacao
from .time import Time
from .vagas import VagasConfig, ClassificacaoService

__all__ = ["Classificacao", "Time", "VagasConfig", "ClassificacaoService"]
