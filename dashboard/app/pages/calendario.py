from dash import dcc, html
import requests
from bs4 import BeautifulSoup

from dashboard.app.services import DashboardService

MONTH_NAMES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

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


def render(time: str, month: int) -> html.Div:
    """Renderiza a página de calendário."""
    time_id = TIME_ID_MAP.get(time)
    time_link = TIME_LINK_MAP.get(time)

    games = []
    error_msg = None

    if time_id and time_link:
        games, error_msg = _fetch_games(time_id, time_link, month)

    return html.Div(
        children=[
            html.Div(
                className="page-header",
                children=[
                    html.H1("📅 Calendário"),
                    html.P(f"Jogos do {time} - {MONTH_NAMES.get(month, '')}"),
                ],
            ),
            html.Div(
                className="table-card",
                children=[
                    html.Div(
                        f"📅 Jogos de {MONTH_NAMES.get(month, '')}",
                        className="chart-title",
                    ),
                    _create_games_table(games, time, month),
                ],
            ),
            html.Div(
                className="info-box",
                children=[
                    html.P("📌 Dados organizados via ESPN Brasil"),
                    html.A(
                        f"Ver no site da ESPN",
                        href=f"https://www.espn.com.br/futebol/calendario/_/id/{time_id}/{time_link}",
                        target="_blank",
                        className="external-link",
                    ),
                ],
            )
            if time_id
            else None,
        ]
    )


def render_sidebar(time: str, month: int) -> html.Div:
    """Renderiza o calendário compactado para o sidebar."""
    from dashboard.app.services import DashboardService

    games_df = DashboardService.get_calendario(time, month, 2026)

    if not games_df.empty:
        games = games_df.to_dict("records")
    else:
        time_id = TIME_ID_MAP.get(time)
        time_link = TIME_LINK_MAP.get(time)
        games = []
        if time_id and time_link:
            games_list, _ = _fetch_games(time_id, time_link, month)
            games = games_list

    month_name = MONTH_NAMES.get(month, "")

    return html.Div(
        className="sidebar-calendar-content",
        children=[
            html.Div(
                className="sidebar-calendar-title",
                children=["Calendário de Jogos"],
            ),
            html.Div(
                className="calendar-header",
                children=[
                    html.Span("⚽", className="calendar-icon"),
                    html.Span(
                        f"{'Todos os Times' if time == 'all' else time} - {month_name}"
                    ),
                ],
            ),
            html.Div(
                className="calendar-title",
                children=[
                    html.Span(f"📅 Jogos de {month_name}"),
                ],
            ),
            _create_games_table(games, time, month),
            html.Div(
                className="calendar-empty",
                children=[
                    html.P(f"Nenhum jogo encontrado para {time} em {month_name}"),
                    html.P("💡 Os jogos serão atualizados em breve"),
                ],
            )
            if not games
            else None,
        ],
    )


def _fetch_games(time_id: int, time_link: str, month: int):
    """Busca os jogos do time no mês especificado via ESPN."""
    url = f"https://www.espn.com.br/futebol/time/calendario/_/id/{time_id}/{time_link}"

    games = []
    error_msg = None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        game_elements = soup.select(".ScheduleGameCard")

        for game in game_elements[:10]:
            try:
                date_elem = game.select_one(".Date div")
                time_elem = game.select_one(".Time div")
                home_team = game.select_one(".Home .TeamName")
                away_team = game.select_one(".Away .TeamName")
                score_elem = game.select_one(".Scoreboard")

                game_date = date_elem.text.strip() if date_elem else ""
                game_time = time_elem.text.strip() if time_elem else ""
                home = home_team.text.strip() if home_team else ""
                away = away_team.text.strip() if away_team else ""
                score = score_elem.text.strip() if score_elem else "-"

                games.append(
                    {
                        "data": game_date,
                        "hora": game_time,
                        "casa": home,
                        "fora": away,
                        "placar": score,
                    }
                )
            except Exception:
                continue

    except Exception as e:
        error_msg = str(e)
        games = []

    return games, error_msg


def _create_games_table(games, time: str, month: int) -> html.Div:
    """Cria a tabela de jogos."""
    if not games:
        return html.Div(
            className="empty-state",
            children=[
                html.P(
                    f"Nenhum jogo encontrado para {time} em {MONTH_NAMES.get(month, '')}"
                ),
                html.P("💡 Os jogos serão atualizados em breve"),
            ],
        )

    headers = ["DATA", "JOGO", "HORA"]
    return html.Table(
        className="data-table calendar-table",
        children=[
            html.Thead(html.Tr([html.Th(h) for h in headers])),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(str(row.get("DATA", ""))),
                            html.Td(str(row.get("JOGO", ""))),
                            html.Td(str(row.get("HORA", ""))),
                        ]
                    )
                    for row in games
                ]
            ),
        ],
    )
