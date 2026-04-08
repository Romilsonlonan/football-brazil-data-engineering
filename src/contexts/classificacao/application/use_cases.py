"""Use Cases para Classificação

Os Use Cases orquestram o domínio, chamar Domain Services
e coordenam a infraestrutura.
"""

import pandas as pd
from dataclasses import dataclass

from ..domain import (
    Classificacao,
    CalculadoraClassificacao,
    CalculadoraColocacao,
    Aproveitamento,
)


@dataclass
class ClassificacaoDTO:
    """DTO para transferência de dados."""

    time: str
    posicao: int
    pontos: int
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    goals_pro: int
    goals_contra: int
    saldo_goals: int
    aproveitamento: float


class GerarClassificacaoUseCase:
    """Use Case que gera a classificação completa.

    Fluxo:
    1. Recebe dados da camada Gold (DataFrame)
    2. Converte para Entities
    3. Aplica regras de domínio
    4. Retorna DTOs processados
    """

    def __init__(self):
        self._calculadora = CalculadoraClassificacao()
        self._colocacao = CalculadoraColocacao()

    def execute(self, df: pd.DataFrame) -> list[ClassificacaoDTO]:
        """Executa o use case."""
        # Converter DataFrame para Entities
        entities = self._df_para_entities(df)

        # Adicionar ao calculador de colocação
        for entity in entities:
            self._colocacao.adicionar(entity)

        # Gerar DTOs com regras aplicadas
        return self._gerar_dtos(entities)

    def _df_para_entities(self, df: pd.DataFrame) -> list[Classificacao]:
        """Converte DataFrame para Entities."""
        entities = []
        for _, row in df.iterrows():
            entities.append(
                Classificacao(
                    time=str(row.get("time", "")),
                    pontos=int(row.get("pontos", 0)),
                    jogos=int(row.get("jogos", 0)),
                    vitorias=int(row.get("vitorias", 0)),
                    empates=int(row.get("empates", 0)),
                    derrotas=int(row.get("derrotas", 0)),
                    goals_pro=int(row.get("gols_pro", 0)),
                    goals_contra=int(row.get("gols_contra", 0)),
                    saldo_goals=int(row.get("saldo_gols", 0)),
                )
            )
        return entities

    def _gerar_dtos(self, entities: list[Classificacao]) -> list[ClassificacaoDTO]:
        """Gera DTOs com regras de domínio aplicadas."""
        dtos = []
        ordenadas = self._colocacao.ordenar()

        for i, entity in enumerate(ordenadas, start=1):
            # Aplicar regra de domínio
            aproveitamento = self._calculadora.calcular_aproveitamento(entity)

            dto = ClassificacaoDTO(
                time=entity.time,
                posicao=i,
                pontos=entity.pontos,
                jogos=entity.jogos,
                vitorias=entity.vitorias,
                empates=entity.empates,
                derrota=entity.derrotas,
                goals_pro=entity.goals_pro,
                goals_contra=entity.goals_contra,
                saldo_goals=entity.saldo_goals,
                aproveitamento=aproveitamento.valor,
            )
            dtos.append(dto)

        return dtos


class ConsultarClassificacaoUseCase:
    """Use Case para consultar classificação."""

    def __init__(self):
        self._calculadora = CalculadoraClassificacao()
        self._colocacao = CalculadoraColocacao()

    def posicao_time(self, df: pd.DataFrame, time: str) -> int | None:
        """Retorna a posição de um time."""
        entities = self._df_para_entities(df)
        for e in entities:
            self._colocacao.adicionar(e)

        posicao = self._colocacao.posicao(time)
        return posicao.valor if posicao else None

    def top_4(self, df: pd.DataFrame) -> list[str]:
        """Retorna os 4 primeiros times."""
        entities = self._df_para_entities(df)
        for e in entities:
            self._colocacao.adicionar(e)

        return [c.time for c in self._colocacao.top_4()]

    def _df_para_entities(self, df: pd.DataFrame) -> list[Classificacao]:
        entities = []
        for _, row in df.iterrows():
            entities.append(
                Classificacao(
                    time=str(row.get("time", "")),
                    pontos=int(row.get("pontos", 0)),
                    jogos=int(row.get("jogos", 0)),
                    vitorias=int(row.get("vitorias", 0)),
                    empates=int(row.get("empates", 0)),
                    derrotas=int(row.get("derrotas", 0)),
                    goals_pro=int(row.get("gols_pro", 0)),
                    goals_contra=int(row.get("gols_contra", 0)),
                    saldo_goals=int(row.get("saldo_gols", 0)),
                )
            )
        return entities
