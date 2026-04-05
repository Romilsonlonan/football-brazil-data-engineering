"""Pipeline Bronze - Calendário de Jogos (ESPN)"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path

BRONZE_PATH = "data/bronze"

TIME_ESPN_LINKS = {
    "Athletico-PR": "https://www.espn.com.br/futebol/time/calendario/_/id/3458",
    "Atlético-MG": "https://www.espn.com.br/futebol/time/calendario/_/id/7632",
    "Bahia": "https://www.espn.com.br/futebol/time/calendario/_/id/9967",
    "Botafogo": "https://www.espn.com.br/futebol/time/calendario/_/id/6086",
    "Chapecoense": "https://www.espn.com.br/futebol/time/calendario/_/id/9318",
    "Corinthians": "https://www.espn.com.br/futebol/time/calendario/_/id/874",
    "Coritiba": "https://www.espn.com.br/futebol/time/calendario/_/id/3456",
    "Cruzeiro": "https://www.espn.com.br/futebol/time/calendario/_/id/2022",
    "Flamengo": "https://www.espn.com.br/futebol/time/calendario/_/id/819",
    "Fluminense": "https://www.espn.com.br/futebol/time/calendario/_/id/3445",
    "Grêmio": "https://www.espn.com.br/futebol/time/calendario/_/id/6273",
    "Internacional": "https://www.espn.com.br/futebol/time/calendario/_/id/1936",
    "Mirassol": "https://www.espn.com.br/futebol/time/calendario/_/id/9169",
    "Palmeiras": "https://www.espn.com.br/futebol/time/calendario/_/id/2029",
    "Red Bull Bragantino": "https://www.espn.com.br/futebol/time/calendario/_/id/6079",
    "Remo": "https://www.espn.com.br/futebol/time/calendario/_/id/4936",
    "Santos": "https://www.espn.com.br/futebol/time/calendario/_/id/2674",
    "São Paulo": "https://www.espn.com.br/futebol/time/calendario/_/id/2026",
    "Vasco da Gama": "https://www.espn.com.br/futebol/time/calendario/_/id/3454",
    "Vitória": "https://www.espn.com.br/futebol/time/calendario/_/id/3457",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_team_games(
    time_name: str, url: str, month: int, year: int = 2026
) -> list[dict]:
    """Busca jogos de um time específico."""
    games = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.select_one("table")
        if not table:
            return games

        tbody = table.select_one("tbody")
        rows = tbody.select("tr") if tbody else table.select("tr")

        for row in rows:
            try:
                cols = row.select("td")

                if len(cols) < 3:
                    continue

                data = cols[0].get_text(strip=True)

                cells = [c.get_text(strip=True) for c in cols[1:]]

                time_casa = cells[0] if len(cells) > 0 else ""
                vs = cells[1] if len(cells) > 1 else ""
                time_fora = cells[2] if len(cells) > 2 else ""
                hora = cells[3] if len(cells) > 3 else ""
                competicao = cells[4] if len(cells) > 4 else ""
                tv = cells[5] if len(cells) > 5 else ""

                if not data or data == "DATA":
                    continue

                if vs and vs.lower() != "v":
                    time_fora = vs
                    vs = "v"

                games.append(
                    {
                        "time": time_name,
                        "DATA": data,
                        "JOGO": f"{time_casa} x {time_fora}"
                        if time_casa and time_fora
                        else "",
                        "HORA": hora,
                        "TV": tv,
                        "mes": month,
                        "ano": year,
                        "fonte": "ESPN",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception:
                continue

        if not games:
            print(f"  [AVISO] Nenhum jogo encontrado para {time_name}")

    except Exception as e:
        print(f"Erro ao buscar {time_name}: {e}")

    return games


def run(month: int = 4, year: int = 2026) -> None:
    """Executa o pipeline bronze."""
    print(f"Iniciando scraping para {month}/{year}...")

    all_games = []

    for time_name, url in TIME_ESPN_LINKS.items():
        print(f"Buscando {time_name}...")
        games = fetch_team_games(time_name, url, month, year)
        all_games.extend(games)

    if all_games:
        df = pd.DataFrame(all_games)
        Path(BRONZE_PATH).mkdir(parents=True, exist_ok=True)
        file_path = f"{BRONZE_PATH}/calendario_raw_{year}_{month:02d}.parquet"
        df.to_parquet(file_path, index=False)
        print(f"Salvo: {file_path} ({len(df)} jogos)")
    else:
        print("Nenhum jogo encontrado!")


if __name__ == "__main__":
    run(month=4, year=2026)
