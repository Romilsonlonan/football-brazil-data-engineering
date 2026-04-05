"""Pipeline Gold - Calendário de Jogos (Prontos para consumo)"""

import pandas as pd
from pathlib import Path
from datetime import datetime

SILVER_PATH = "data/silver"
GOLD_PATH = "data/gold"

TIME_NAME_MAP = {
    "Athletico-PR": "Athletico Paranaense",
    "Atlético-MG": "Atlético Mineiro",
    "Bahia": "Bahia",
    "Botafogo": "Botafogo",
    "Chapecoense": "Chapecoense",
    "Corinthians": "Corinthians",
    "Coritiba": "Coritiba",
    "Cruzeiro": "Cruzeiro",
    "Flamengo": "Flamengo",
    "Fluminense": "Fluminense",
    "Grêmio": "Grêmio",
    "Internacional": "Internacional",
    "Mirassol": "Mirassol",
    "Palmeiras": "Palmeiras",
    "Red Bull Bragantino": "Bragantino",
    "Remo": "Remo",
    "Santos": "Santos",
    "São Paulo": "São Paulo",
    "Vasco da Gama": "Vasco",
    "Vitória": "Vitória",
}


def run(month: int = 4, year: int = 2026) -> None:
    """Executa o pipeline gold - dados otimizados para o dashboard."""
    silver_file = f"{SILVER_PATH}/calendario_{year}_{month:02d}.parquet"

    try:
        df = pd.read_parquet(silver_file)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {silver_file}")
        return

    if df.empty:
        print("Dados silver vazios!")
        return

    df = df.copy()

    if "time" in df.columns:
        df["time_normalizado"] = df["time"].map(TIME_NAME_MAP).fillna(df["time"])

    cols_ordem = [
        "time",
        "time_normalizado",
        "DATA",
        "JOGO",
        "HORA",
        "status",
        "mes",
        "ano",
    ]

    cols_existentes = [c for c in cols_ordem if c in df.columns]
    df = df[cols_existentes]

    Path(GOLD_PATH).mkdir(parents=True, exist_ok=True)
    gold_file = f"{GOLD_PATH}/calendario_{year}_{month:02d}.parquet"
    df.to_parquet(gold_file, index=False)
    print(f"Salvo: {gold_file} ({len(df)} jogos)")


if __name__ == "__main__":
    run(month=4, year=2026)
