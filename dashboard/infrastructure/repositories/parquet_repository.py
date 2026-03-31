"""Implementação do repositório de dados Parquet - Infrastructure Layer"""
from pathlib import Path
from typing import Any

import pandas as pd

from dashboard.domain.entities.classificacao import ClassificacaoTime
from dashboard.domain.entities.jogador import Jogador
from dashboard.domain.repositories.interfaces import (
    ClassificacaoRepository,
    ElencoRepository,
)


class ParquetRepository(ClassificacaoRepository, ElencoRepository):
    """Repositório para acessar dados de arquivos Parquet."""

    def __init__(self, data_path: str = "data/gold") -> None:
        self._data_path = Path(data_path)
        self._classificacao_path = self._data_path / "classificacao.parquet"
        self._elenco_path = self._data_path / "classificacao-vagas.parquet"
        self._bronze_elenco_path = Path("data/bronze/elenco.parquet")

    @staticmethod
    def _parse_idade(valor: Any) -> int | None:
        """Converte o valor da idade para inteiro."""
        if pd.isna(valor):
            return None
        try:
            return int(float(valor))
        except (ValueError, TypeError):
            return None

    def get_classificacao_completa(self) -> list[ClassificacaoTime]:
        """Retorna a classificação completa como entidades."""
        df = self.get_classificacao_dataframe()
        return [
            ClassificacaoTime(
                posicao=row["posicao"],
                time=row["time"],
                jogos=row["jogos"],
                vitorias=row["vitorias"],
                empates=row["empates"],
                derrotas=row["derrotas"],
                golees_pro=row["gols_pro"],
                saldo_gols=row["saldo_gols"],
                pontos=row["pontos"],
            )
            for row in df.to_dict("records")
        ]

    def get_classificacao_dataframe(self) -> pd.DataFrame:
        """Retorna a classificação como DataFrame."""
        if self._classificacao_path.exists():
            df = pd.read_parquet(self._classificacao_path)
        elif self._elenco_path.exists():
            df = pd.read_parquet(self._elenco_path)
            if "zona" in df.columns:
                df = df.drop(columns=["zona", "status_curto", "aproveitamento"])
        else:
            raise FileNotFoundError(
                f"Arquivo de classificação não encontrado em: {self._data_path}"
            )
        return df.sort_values("posicao").reset_index(drop=True)

    def get_elenco_completo(self) -> list[Jogador]:
        """Retorna o elenco completo como entidades."""
        df = self.get_elenco_dataframe()
        return [
            Jogador(
                nome=row["Nome"],
                time=row["Time"],
                posicao=row["Posição"],
                idade=self._parse_idade(row.get("Idade")),
                nacionalidade=row.get("NAC"),
            )
            for row in df.to_dict("records")
        ]

    def get_elenco_por_time(self, nome_time: str) -> list[Jogador]:
        """Retorna o elenco de um time específico."""
        df = self.get_elenco_dataframe()
        return [
            Jogador(
                nome=row["Nome"],
                time=row["Time"],
                posicao=row["Posição"],
                idade=self._parse_idade(row.get("Idade")),
                nacionalidade=row.get("NAC"),
            )
            for row in df[df["Time"].str.contains(nome_time, case=False)].to_dict(
                "records"
            )
        ]

    def get_elenco_dataframe(self) -> pd.DataFrame:
        """Retorna o elenco como DataFrame."""
        if not self._bronze_elenco_path.exists():
            raise FileNotFoundError(
                f"Arquivo de elenco não encontrado em: {self._bronze_elenco_path}"
            )
        return pd.read_parquet(self._bronze_elenco_path)