"""Context: Classificação - Implementação DDD Completa

Este é o Bounded Context de Classificação do Campeonato Brasileiro.

Estrutura DDD:
├── domain/           # Entidades, Value Objects, Domain Services
│   ├── entities.py
│   ├── value_objects.py
│   └── services.py
├── application/     # Use Cases
│   └── use_cases.py
└── infrastructure/ # Repositories, Scrapers (futuro)
    └── repositories.py

Uso:
    from src.contexts.classificacao import (
        Classificacao,
        CalculadoraClassificacao,
        CalculadoraColocacao,
        GerarClassificacaoUseCase,
    )
"""

from .domain import (
    Classificacao,
    Time,
    ResultadoJogo,
    Pontos,
    Posicao,
    Aproveitamento,
    CalculadoraClassificacao,
    CalculadoraColocacao,
)
from .application import (
    ClassificacaoDTO,
    GerarClassificacaoUseCase,
    ConsultarClassificacaoUseCase,
)

__all__ = [
    # Domain
    "Classificacao",
    "Time",
    "ResultadoJogo",
    "Pontos",
    "Posicao",
    "Aproveitamento",
    "CalculadoraClassificacao",
    "CalculadoraColocacao",
    # Application
    "ClassificacaoDTO",
    "GerarClassificacaoUseCase",
    "ConsultarClassificacaoUseCase",
]
