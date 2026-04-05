from typing import Optional
import pandas as pd
from pandas import DataFrame

from dashboard.application.use_cases.buscar_classificacao import (
    BuscarClassificacaoUseCase,
)
from dashboard.application.use_cases.buscar_elenco import BuscarElencoUseCase
from dashboard.infrastructure.repositories.parquet_repository import ParquetRepository
from dashboard.shared.config import get_data_path, get_bronze_data_path
import os


class DashboardService:
    _classificacao_use_case: Optional[BuscarClassificacaoUseCase] = None
    _elenco_use_case: Optional[BuscarElencoUseCase] = None
    _times_cache: Optional[list[str]] = None
    _classificacao_cache: Optional[DataFrame] = None
    _elenco_cache: Optional[DataFrame] = None
    _calendario_cache: dict = {}

    @classmethod
    def get_classificacao_use_case(cls) -> BuscarClassificacaoUseCase:
        if cls._classificacao_use_case is None:
            repo = ParquetRepository(get_data_path())
            cls._classificacao_use_case = BuscarClassificacaoUseCase(repo)
        return cls._classificacao_use_case

    @classmethod
    def get_elenco_use_case(cls) -> BuscarElencoUseCase:
        if cls._elenco_use_case is None:
            repo = ParquetRepository(get_bronze_data_path())
            cls._elenco_use_case = BuscarElencoUseCase(repo)
        return cls._elenco_use_case

    @classmethod
    def get_classificacao_df(cls) -> DataFrame:
        if cls._classificacao_cache is None:
            try:
                cls._classificacao_cache = cls.get_classificacao_use_case().execute()
            except Exception as e:
                print(f"[DashboardService] Erro ao carregar classificação: {e}")
                cls._classificacao_cache = DataFrame()
        return cls._classificacao_cache

    @classmethod
    def get_elenco_df(cls) -> DataFrame:
        """Retorna o DataFrame completo do elenco (para estatísticas do campeonato)."""
        if cls._elenco_cache is None:
            try:
                cls._elenco_cache = cls.get_elenco_use_case().execute()
            except Exception as e:
                print(f"[DashboardService] Erro ao carregar elenco: {e}")
                cls._elenco_cache = DataFrame()
        return cls._elenco_cache

    @classmethod
    def get_estatisticas_campeonato(cls, month: int = None) -> dict:
        """Retorna estatísticas agregadas do campeonato para os cards."""
        df = cls.get_elenco_df()
        if df.empty:
            return {
                "artilheiro": {"nome": "-", "gols": 0},
                "cartoes_amarelos": {"total": 0},
                "cartoes_vermelhos": {"total": 0},
                "melhor_goleiro": {"nome": "-", "defesas": 0},
            }

        df = df.copy()
        df["G"] = pd.to_numeric(df["G"], errors="coerce").fillna(0)
        df["CA"] = pd.to_numeric(df["CA"], errors="coerce").fillna(0)
        df["CV"] = pd.to_numeric(df["CV"], errors="coerce").fillna(0)
        df["D"] = pd.to_numeric(df["D"], errors="coerce").fillna(0)

        if month and "mes" in df.columns:
            df = df[df["mes"] <= month]

        artilheiro = df.loc[df["G"].idxmax()] if not df.empty else None
        total_ca = int(df["CA"].sum())
        total_cv = int(df["CV"].sum())
        goleiros = df[df["Posição"] == "Goleiro"]
        melhor_goleiro = (
            goleiros.loc[goleiros["D"].idxmax()] if not goleiros.empty else None
        )

        return {
            "artilheiro": {
                "nome": artilheiro["Nome"] if artilheiro is not None else "-",
                "time": artilheiro["Time"] if artilheiro is not None else "-",
                "gols": int(artilheiro["G"]) if artilheiro is not None else 0,
            },
            "cartoes_amarelos": {"total": total_ca},
            "cartoes_vermelhos": {"total": total_cv},
            "melhor_goleiro": {
                "nome": melhor_goleiro["Nome"] if melhor_goleiro is not None else "-",
                "time": melhor_goleiro["Time"] if melhor_goleiro is not None else "-",
                "defesas": int(melhor_goleiro["D"])
                if melhor_goleiro is not None
                else 0,
            },
        }

    @classmethod
    def get_top_cartoes_amarelos(cls, top: int = 4, month: int = None) -> DataFrame:
        """Retorna os jogadores com mais cartões amarelos."""
        df = cls.get_elenco_df()
        if df.empty:
            return DataFrame()
        df = df.copy()
        df["CA"] = pd.to_numeric(df["CA"], errors="coerce").fillna(0)
        if month and "mes" in df.columns:
            df = df[df["mes"] <= month]
        return df.nlargest(top, "CA")[["Nome", "Time", "CA"]]

    @classmethod
    def get_top_cartoes_vermelhos(cls, top: int = 4, month: int = None) -> DataFrame:
        """Retorna os jogadores com mais cartões vermelhos."""
        df = cls.get_elenco_df()
        if df.empty:
            return DataFrame()
        df = df.copy()
        df["CV"] = pd.to_numeric(df["CV"], errors="coerce").fillna(0)
        if month and "mes" in df.columns:
            df = df[df["mes"] <= month]
        return df.nlargest(top, "CV")[["Nome", "Time", "CV"]]

    @classmethod
    def get_top_artilheiros(cls, top: int = 5, month: int = None) -> DataFrame:
        """Retorna os maiores artilheiros do championship."""
        df = cls.get_elenco_df()
        if df.empty:
            return DataFrame()
        df = df.copy()
        df["G"] = pd.to_numeric(df["G"], errors="coerce").fillna(0)
        if month and "mes" in df.columns:
            df = df[df["mes"] <= month]
        return df.nlargest(top, "G")[["Nome", "Time", "G"]]

    @classmethod
    def get_times(cls) -> list[str]:
        if cls._times_cache is None:
            try:
                cls._times_cache = cls.get_elenco_use_case().get_times()
            except Exception as e:
                print(f"[DashboardService] Erro ao carregar times: {e}")
                cls._times_cache = []
        return cls._times_cache

    @classmethod
    def get_goalkeepers_by_team(cls, team: str, month: int = None) -> DataFrame:
        """Retorna os goleiros de um time específico (da camada gold).
        O elenco é estático por temporada, então o mês não afeta o resultado.
        """
        gold_path = get_data_path()
        file_path = os.path.join(gold_path, "elenco_goleiros.parquet")
        if not os.path.exists(file_path):
            return DataFrame()
        df = pd.read_parquet(file_path)
        if df.empty or not team:
            return df
        df_team = df[df["Time"].str.contains(team, case=False, na=False)]
        cols = [
            "Nome",
            "POS",
            "Idade",
            "Alt",
            "P",
            "NAC",
            "J",
            "SUB",
            "D",
            "GS",
            "A",
            "FC",
            "FS",
            "CA",
            "CV",
        ]
        goleiros = df_team[cols].copy()
        numeric_cols = [
            "Idade",
            "Alt",
            "J",
            "SUB",
            "D",
            "GS",
            "A",
            "FC",
            "FS",
            "CA",
            "CV",
        ]
        for col in numeric_cols:
            goleiros[col] = (
                pd.to_numeric(goleiros[col], errors="coerce").fillna(0).astype(int)
            )
        return goleiros

    @classmethod
    def get_field_players_by_team(cls, team: str, month: int = None) -> DataFrame:
        """Retorna os jogadores de campo de um time específico (da camada gold).
        O elenco é estático por temporada, então o mês não afeta o resultado.
        """
        gold_path = get_data_path()
        file_path = os.path.join(gold_path, "elenco_jogadores_campo.parquet")
        if not os.path.exists(file_path):
            return DataFrame()
        df = pd.read_parquet(file_path)
        if df.empty or not team:
            return df
        df_team = df[df["Time"].str.contains(team, case=False, na=False)]
        cols = [
            "Nome",
            "POS",
            "Idade",
            "Alt",
            "P",
            "NAC",
            "J",
            "SUB",
            "G",
            "A",
            "TC",
            "CG",
            "FC",
            "FS",
            "CA",
            "CV",
        ]
        jogadores = df_team[cols].copy()
        numeric_cols = [
            "Idade",
            "Alt",
            "J",
            "SUB",
            "G",
            "A",
            "TC",
            "CG",
            "FC",
            "FS",
            "CA",
            "CV",
        ]
        for col in numeric_cols:
            jogadores[col] = (
                pd.to_numeric(jogadores[col], errors="coerce").fillna(0).astype(int)
            )
        return jogadores

    @classmethod
    def get_calendario(cls, team: str, month: int, year: int = 2026) -> DataFrame:
        """Retorna os jogos de um time específico da camada gold."""
        gold_path = get_data_path()
        file_path = os.path.join(gold_path, f"calendario_{year}_{month:02d}.parquet")
        if not os.path.exists(file_path):
            return DataFrame()
        try:
            df = pd.read_parquet(file_path)
            if team:
                mask1 = df["time_normalizado"].str.contains(team, case=False, na=False)
                mask2 = df["time"].str.contains(team, case=False, na=False)
                df = df[mask1 | mask2]
            return df
        except Exception:
            return DataFrame()

    @classmethod
    def clear_cache(cls) -> None:
        cls._classificacao_cache = None
        cls._elenco_cache = None
        cls._calendario_cache = {}
