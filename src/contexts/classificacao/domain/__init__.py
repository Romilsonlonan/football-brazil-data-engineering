"""Domínio de Classificação - DDD Complete

Este módulo contém a implementação completa do DDD para classificação:
- Value Objects: Pontos, Posicao, Aproveitamento
- Entities: Time, Classificacao, ResultadoJogo
- Domain Services: CalculadoraClassificacao, CalculadoraColocacao
- Adapters: ClassificacaoLegacy, TimeLegacy (compatibilidade)

Princípios aplicados:
- SRP: Cada classe tem uma responsabilidade
- OCP: Extensible via adapters
- DIP: Depende de abstrações (Entities/Services)
- Adapter Pattern: Compatibilidade com legados

Uso:
    from src.contexts.classificacao.domain import (
        Classificacao,
        CalculadoraClassificacao,
        CalculadoraColocacao,
        Pontos,
        Posicao,
        Aproveitamento,
        ClassificacaoLegacy,  # Para migrar Dashboard/API
    )
"""

from .value_objects import Pontos, Posicao, Aproveitamento
from .entities import Time, Classificacao, ResultadoJogo
from .services import (
    CalculadoraClassificacao,
    CalculadoraColocacao,
    CalculadoraConfrontosDiretos,
    Confronto,
)
from .adapters import ClassificacaoLegacy, TimeLegacy

__all__ = [
    # Value Objects
    "Pontos",
    "Posicao",
    "Aproveitamento",
    # Entities
    "Time",
    "Classificacao",
    "ResultadoJogo",
    # Domain Services
    "CalculadoraClassificacao",
    "CalculadoraColocacao",
    "CalculadoraConfrontosDiretos",
    "Confronto",
    # Adapters (para migração)
    "ClassificacaoLegacy",
    "TimeLegacy",
]
