"""Value Object Posicao."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ZonaClassificacao(str, Enum):
    """Zonas de classificação no Brasileirão."""

    LIBERTADORES_GRUPO = "LIBERTADORES_GRUPO"  # 1º-4º - fase de grupos
    LIBERTADORES_PRE = "LIBERTADORES_PRE"  # 5º - fase preliminar
    SUL_AMERICANA = "SUL-AMERICANA"  # 6º-11º
    SEM_REBAIXAMENTO = "SEM_REBAIXAMENTO"  # 12º-16º
    REBAIXAMENTO = "REBAIXAMENTO"  # 17º-20º


class TipoVaga(str, Enum):
    """Tipos de vaga para competições continentais."""

    LIBERTADORES_GRUPO = "LIBERTADORES_GRUPO"  # Fase de grupos
    LIBERTADORES_PRE = "LIBERTADORES_PRE"  # Fase preliminar
    SUL_AMERICANA = "SUL-AMERICANA"  # Copa Sul-Americana


@dataclass(frozen=True)
class Posicao:
    """Value Object que representa uma posição na tabela."""

    numero: int
    zona: Optional[ZonaClassificacao] = None

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.numero < 1 or self.numero > 20:
            raise ValueError("Posição deve estar entre 1 e 20")

        # Determina a zona automaticamente se não fornecida
        if self.zona is None:
            self.zona = self._determinar_zona()

    def _determinar_zona(self) -> ZonaClassificacao:
        """Determina a zona de classificação baseada na posição."""
        if self.numero <= 4:
            return ZonaClassificacao.LIBERTADORES_GRUPO
        elif self.numero == 5:
            return ZonaClassificacao.LIBERTADORES_PRE
        elif self.numero <= 11:
            return ZonaClassificacao.SUL_AMERICANA
        elif self.numero >= 17:
            return ZonaClassificacao.REBAIXAMENTO
        else:
            return ZonaClassificacao.SEM_REBAIXAMENTO

    @property
    def is_liberadores(self) -> bool:
        return self.numero <= 5

    @property
    def is_liberadores_grupo(self) -> bool:
        return self.numero <= 4

    @property
    def is_liberadores_pre(self) -> bool:
        return self.numero == 5

    @property
    def is_sul_americana(self) -> bool:
        return 6 <= self.numero <= 11

    @property
    def is_rebaixamento(self) -> bool:
        return self.numero >= 17

    @property
    def tipo_vaga(self) -> Optional[TipoVaga]:
        """Retorna o tipo de vaga para competições continentais."""
        if self.numero <= 4:
            return TipoVaga.LIBERTADORES_GRUPO
        elif self.numero == 5:
            return TipoVaga.LIBERTADORES_PRE
        elif 6 <= self.numero <= 11:
            return TipoVaga.SUL_AMERICANA
        return None

    def __str__(self) -> str:
        return f"{self.numero}º lugar"

    def __lt__(self, other: "Posicao") -> bool:
        return self.numero < other.numero

    def __le__(self, other: "Posicao") -> bool:
        return self.numero <= other.numero

    def __gt__(self, other: "Posicao") -> bool:
        return self.numero > other.numero

    def __ge__(self, other: "Posicao") -> bool:
        return self.numero >= other.numero
