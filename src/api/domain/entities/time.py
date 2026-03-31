"""Entidade Time."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Time:
    """Entidade que representa um time de futebol."""

    id: Optional[int] = None
    nome: str = ""
    nome_reduzido: Optional[str] = None
    estado: Optional[str] = None
    Estadio: Optional[str] = None

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.nome:
            raise ValueError("Nome do time é obrigatório")

        if not self.nome_reduzido:
            self.nome_reduzido = self._gerar_nome_reduzido()

    def _gerar_nome_reduzido(self) -> str:
        """Gera um nome reduzido baseado no nome completo."""
        # Mapeamento de nomes completos para reduzidos
        mapeamento = {
            "Atlético Mineiro": "Atlético-MG",
            "Atlético Paranaense": "Athletico-PR",
            "Botafogo": "Botafogo",
            "Corinthians": "Corinthians",
            "Cruzeiro": "Cruzeiro",
            "Flamengo": "Flamengo",
            "Fluminense": "Fluminense",
            "Grêmio": "Grêmio",
            "Internacional": "Internacional",
            "Palmeiras": "Palmeiras",
            "Santos": "Santos",
            "São Paulo": "São Paulo",
            "Vasco da Gama": "Vasco",
            "Red Bull Bragantino": "Bragantino",
            "Coritiba": "Coritiba",
            "Cuiabá": "Cuiabá",
            "América Mineiro": "América-MG",
            "Athletico Paranaense": "Athletico-PR",
            "Atlético Goianiense": "Atlético-GO",
            "Avaí": "Avaí",
            "Ceará": "Ceará",
            "Chapecoense": "Chapecoense",
            "Goiás": "Goiás",
            "Juventude": "Juventude",
            "Mirassol": "Mirassol",
            "Operário": "Operário",
            "Ponte Preta": "Ponte Preta",
            "Sport": "Sport",
            "Tubaráo": "Tubarão",
        }
        return mapeamento.get(self.nome, self.nome[:10].strip())

    def __str__(self) -> str:
        return self.nome_reduzido or self.nome
