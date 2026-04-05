"""Pipeline para processar dados de calendário - Silver & Gold Layer"""

import pandas as pd
from datetime import datetime
from pathlib import Path

BRONZE_PATH = "data/bronze"
SILVER_PATH = "data/silver"
GOLD_PATH = "data/gold"

TIME_NAMES_CLEAN = {
    "Athletico Paranaense": "Athletico-PR",
    "Atlético Go": "Atlético-GO",
    "Atlético Mineiro": "Atlético-MG",
    "Bahia": "Bahia",
    "Botafogo": "Botafogo",
    "Bragantino": "Bragantino",
    "Ceará": "Ceará",
    "Corinthians": "Corinthians",
    "Coritiba": "Coritiba",
    "Cruzeiro": "Cruzeiro",
    "Cuiabá": "Cuiabá",
    "Flamengo": "Flamengo",
    "Fluminense": "Fluminense",
    "Fortaleza": "Fortaleza",
    "Goiás": "Goiás",
    "Grêmio": "Grêmio",
    "Internacional": "Internacional",
    "Juventude": "Juventude",
    "Mirassol": "Mirassol",
    "Palmeiras": "Palmeiras",
    "Santos": "Santos",
    "São Paulo": "São Paulo",
    "Sport": "Sport",
    "Vasco": "Vasco",
    "Vitória": "Vitória",
}


def process_silver(df: pd.DataFrame) -> pd.DataFrame:
    """Processa dados do bronze para silver - limpa e padroniza."""
    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    if "time" in df.columns:
        df["time_normalizado"] = df["time"].map(TIME_NAMES_CLEAN).fillna(df["time"])

    if "data" in df.columns:
        df["data_formatada"] = pd.to_datetime(df["data"], errors="coerce")

    if "hora" in df.columns:
        df["hora"] = df["hora"].fillna("")

    df["placar_casa"] = df["placar"].apply(
        lambda x: str(x).split("-")[0].strip() if x and "-" in str(x) else ""
    )
    df["placar_fora"] = df["placar"].apply(
        lambda x: str(x).split("-")[1].strip() if x and "-" in str(x) else ""
    )

    return df


def save_to_gold(df: pd.DataFrame, month: int, year: int = 2026) -> None:
    """Salva dados processados na camada gold."""
    if df.empty:
        return

    Path(GOLD_PATH).mkdir(parents=True, exist_ok=True)

    file_path = f"{GOLD_PATH}/calendario_{year}_{month:02d}.parquet"
    df.to_parquet(file_path, index=False)
    print(f"Salvo: {file_path}")


def load_from_gold(time: str, month: int, year: int = 2026) -> pd.DataFrame:
    """Carrega dados da camada gold."""
    file_path = f"{GOLD_PATH}/calendario_{year}_{month:02d}.parquet"

    try:
        df = pd.read_parquet(file_path)
        if time:
            df = df[df["time_normalizado"].str.contains(time, case=False)]
        return df
    except FileNotFoundError:
        return pd.DataFrame()


def run_pipeline(month: int = 4, year: int = 2026) -> None:
    """Executa o pipeline completo: bronze -> silver -> gold."""
    from dashboard.infrastructure.scrapers.espn_calendar import fetch_games_from_espn

    print(f"Iniciando pipeline para {month}/{year}...")

    all_games = []
    for time_name in TIME_NAMES_CLEAN.keys():
        print(f"Processando {time_name}...")
        df = fetch_games_from_espn(time_name, month, year)
        if not df.empty:
            all_games.append(df)

    if not all_games:
        print("Nenhum jogo encontrado!")
        return

    bronze_df = pd.concat(all_games, ignore_index=True)

    Path(BRONZE_PATH).mkdir(parents=True, exist_ok=True)
    bronze_file = f"{BRONZE_PATH}/calendario_raw_{year}_{month:02d}.parquet"
    bronze_df.to_parquet(bronze_file, index=False)
    print(f"Bronze salvo: {bronze_file}")

    silver_df = process_silver(bronze_df)
    Path(SILVER_PATH).mkdir(parents=True, exist_ok=True)
    silver_file = f"{SILVER_PATH}/calendario_{year}_{month:02d}.parquet"
    silver_df.to_parquet(silver_file, index=False)
    print(f"Silver salvo: {silver_file}")

    save_to_gold(silver_df, month, year)
    print("Pipeline concluído!")


if __name__ == "__main__":
    run_pipeline(month=4, year=2026)
