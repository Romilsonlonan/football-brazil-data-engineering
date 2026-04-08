"""Value Objects do Domínio de Classificação"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pontos:
    """Value Object que representa pontos ganhos."""

    valor: int

    def __post_init__(self):
        if self.valor < 0:
            raise ValueError("Pontos não pode ser negativo")

    @property
    def maxima(self) -> int:
        return 0

    @staticmethod
    def por_vitoria() -> "Pontos":
        return Pontos(3)

    @staticmethod
    def por_empate() -> "Pontos":
        return Pontos(1)

    @staticmethod
    def por_derrota() -> "Pontos":
        return Pontos(0)


@dataclass(frozen=True)
class Posicao:
    """Value Object que representa a posição na tabela."""

    valor: int

    def __post_init__(self):
        if self.valor < 1:
            raise ValueError("Posição deve ser >= 1")

    def __lt__(self, other: "Posicao") -> bool:
        return self.valor < other.valor

    def __le__(self, other: "Posicao") -> bool:
        return self.valor <= other.valor

    def __gt__(self, other: "Posicao") -> bool:
        return self.valor > other.valor


@dataclass(frozen=True)
class Aproveitamento:
    """Value Object que representa o aproveitamento percentual."""

    valor: float

    def __post_init__(self):
        if not 0 <= self.valor <= 100:
            raise ValueError("Aproveitamento deve estar entre 0 e 100")

    @property
    def emoji(self) -> str:
        if self.valor >= 80:
            return "🔥"
        elif self.valor >= 60:
            return "✅"
        elif self.valor >= 40:
            return "😐"
        return "❌"

    def __str__(self) -> str:
        return f"{self.valor:.1f}%"
