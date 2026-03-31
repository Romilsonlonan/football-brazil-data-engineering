"""Entidade Jogador - Domain Layer"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Jogador:
    """Entidade que representa um jogador de futebol."""
    nome: str
    time: str
    posicao: str
    idade: int | None
    nacionalidade: str | None

    def __str__(self) -> str:
        return f"{self.nome} ({self.posicao})"