"""Scraper para buscar dados de calendário da ESPN - Bronze Layer"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

TIME_ID_MAP = {
    "Athletico Paranaense": 3458,
    "Atlético Go": 3672,
    "Atlético Mineiro": 278,
    "Bahia": 268,
    "Botafogo": 274,
    "Bragantino": 3705,
    "Ceará": 292,
    "Corinthians": 276,
    "Coritiba": 315,
    "Cruzeiro": 282,
    "Cuiabá": 3721,
    "Flamengo": 288,
    "Fluminense": 343,
    "Fortaleza": 3562,
    "Goiás": 290,
    "Grêmio": 285,
    "Internacional": 287,
    "Juventude": 3483,
    "Mirassol": 4736,
    "Palmeiras": 275,
    "Santos": 277,
    "São Paulo": 280,
    "Sport": 303,
    "Vasco": 265,
    "Vitória": 2877,
}

TIME_LINK_MAP = {
    "Athletico Paranaense": "bra.atletico_paranaense",
    "Atlético Go": "bra.atletico_goianiense",
    "Atlético Mineiro": "bra.atletico_mineiro",
    "Bahia": "bra.bahia",
    "Botafogo": "bra.botafogo",
    "Bragantino": "bra.bragantino",
    "Ceará": "bra.ceara",
    "Corinthians": "bra.corinthians",
    "Coritiba": "bra.coritiba",
    "Cruzeiro": "bra.cruzeiro",
    "Cuiabá": "bra.cuiaba",
    "Flamengo": "bra.flamengo",
    "Fluminense": "bra.fluminense",
    "Fortaleza": "bra.fortaleza",
    "Goiás": "bra.goias",
    "Grêmio": "bra.gremio",
    "Internacional": "bra.internacional",
    "Juventude": "bra.juventude",
    "Mirassol": "bra.mirassol",
    "Palmeiras": "bra.palmeiras",
    "Santos": "bra.santos",
    "São Paulo": "bra.saopaulo",
    "Sport": "bra.sport",
    "Vasco": "bra.vasco",
    "Vitória": "bra.vitoria",
}


def fetch_games_from_espn(time_name: str, month: int, year: int = 2026) -> pd.DataFrame:
    """Busca jogos de um time específico via ESPN."""
    time_id = TIME_ID_MAP.get(time_name)
    time_link = TIME_LINK_MAP.get(time_name)

    if not time_id or not time_link:
        return pd.DataFrame()

    url = f"https://www.espn.com.br/futebol/time/calendario/_/id/{time_id}/{time_link}"

    games = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        game_cards = (
            soup.select(".ScheduleGameCard")
            or soup.select('[class*="GameCard"]')
            or soup.select("li.game-card")
        )

        for game in game_cards:
            try:
                date_elem = game.select_one(".Date, .date, [class*='date']")
                time_elem = game.select_one(".Time, .time, [class*='time']")
                home_team = game.select_one(".Home .TeamName, .home-team-name")
                away_team = game.select_one(".Away .TeamName, .away-team-name")
                score_elem = game.select_one(".Scoreboard, .score, [class*='score']")

                if not date_elem:
                    continue

                game_date = date_elem.get_text(strip=True)
                game_time = time_elem.get_text(strip=True) if time_elem else ""
                home = home_team.get_text(strip=True) if home_team else ""
                away = away_team.get_text(strip=True) if away_team else ""
                score = score_elem.get_text(strip=True) if score_elem else "x"

                games.append(
                    {
                        "time": time_name,
                        "data": game_date,
                        "hora": game_time,
                        "time_casa": home,
                        "time_fora": away,
                        "placar": score,
                        "mes": month,
                        "ano": year,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception:
                continue

    except Exception as e:
        print(f"Erro ao buscar {time_name}: {e}")
        return pd.DataFrame()

    return pd.DataFrame(games)


def fetch_all_games_for_month(month: int, year: int = 2026) -> pd.DataFrame:
    """Busca jogos de todos os times para um mês específico."""
    all_games = []

    for time_name in TIME_ID_MAP.keys():
        print(f"Buscando {time_name}...")
        games_df = fetch_games_from_espn(time_name, month, year)
        if not games_df.empty:
            all_games.append(games_df)

    if all_games:
        return pd.concat(all_games, ignore_index=True)
    return pd.DataFrame()


if __name__ == "__main__":
    print("Testando scraping...")

    df = fetch_games_from_espn("Flamengo", 4, 2026)
    print(df)
    print(f"Encontrados {len(df)} jogos")
