"""Pipeline Silver - Calendário de Jogos (Limpeza e Transformação)"""

import pandas as pd
from pathlib import Path
from datetime import datetime

BRONZE_PATH = "data/bronze"
SILVER_PATH = "data/silver"

COLUMN_MAP = {
    "data": "DATA",
    "hora": "HORA",
    "jogo": "JOGO",
    "competicao": "CAMPEONATO",
}


def run(month: int = 4, year: int = 2026) -> None:
    """Executa o pipeline silver - limpa e transforma os dados bronze."""
    bronze_file = f"{BRONZE_PATH}/calendario_raw_{year}_{month:02d}.parquet"

    try:
        df = pd.read_parquet(bronze_file)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {bronze_file}")
        return

    if df.empty:
        print("Dados bronze vazios!")
        return

    df = df.copy()

    if "hora" in df.columns:
        df["hora"] = df["hora"].fillna("")

    df["jogo"] = df.apply(
        lambda r: (
            f"{r.get('time_casa', '')} x {r.get('time_fora', '')}"
            if r.get("time_casa") and r.get("time_fora")
            else ""
        ),
        axis=1,
    )

    df["status"] = df["JOGO"].apply(
        lambda x: "agendado" if not x or x == "" else "realizado"
    )

    df["updated_at"] = datetime.now().isoformat()

    cols_final = [
        "time",
        "DATA",
        "JOGO",
        "HORA",
        "TV",
        "status",
        "mes",
        "ano",
    ]
    existing = [c for c in cols_final if c in df.columns]
    df = df[existing]

    Path(SILVER_PATH).mkdir(parents=True, exist_ok=True)
    silver_file = f"{SILVER_PATH}/calendario_{year}_{month:02d}.parquet"
    df.to_parquet(silver_file, index=False)
    print(f"Salvo: {silver_file} ({len(df)} jogos)")


if __name__ == "__main__":
    run(month=4, year=2026)
