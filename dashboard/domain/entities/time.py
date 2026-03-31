"""Entidade Time - Domain Layer"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Time:
    """Entidade que representa um time de futebol."""
    id: str
    nome: str
    abreviacao: str | None = None
    estadio: str | None = None

    def __str__(self) -> str:
        return self.nome