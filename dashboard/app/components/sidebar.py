from dash import dcc, html

from dashboard.app.services import DashboardService
from dashboard.app.components.bottom_sheet import bottom_sheet, bottom_sheet_team


def sidebar(times: list[str]) -> html.Div:
    return html.Div(
        id="sidebar",
        className="sidebar",
        children=[
            html.Div(
                className="sidebar-scroll",
                children=[
                    _logo(),
                    _filters(times),
                ],
            )
        ],
    )


def _logo() -> html.Div:
    return html.Div(
        className="sidebar-logo",
        children=[
            html.Div("🏆", className="sidebar-logo-icon"),
            html.H1("Brasileirão", className="sidebar-logo-title"),
            html.P("Campeonato Brasileiro 2026", className="sidebar-logo-subtitle"),
        ],
    )


def _filters(times: list[str]) -> html.Div:
    time_options = [{"label": "Todos os Times", "value": "all"}] + (
        [{"label": t, "value": t} for t in times] if times else []
    )
    if not times:
        time_options = [{"label": "Nenhum time disponível", "value": ""}]

    page_options = [
        {"label": "📊 Classificação", "value": "classificacao"},
        {"label": "👥 Elenco", "value": "elenco"},
    ]

    month_options = [
        {"label": "Todo o Campeonato", "value": 0},
        {"label": "Janeiro", "value": 1},
        {"label": "Fevereiro", "value": 2},
        {"label": "Março", "value": 3},
        {"label": "Abril", "value": 4},
        {"label": "Maio", "value": 5},
        {"label": "Junho", "value": 6},
        {"label": "Julho", "value": 7},
        {"label": "Agosto", "value": 8},
        {"label": "Setembro", "value": 9},
        {"label": "Outubro", "value": 10},
        {"label": "Novembro", "value": 11},
        {"label": "Dezembro", "value": 12},
    ]

    top10_options = [
        {"label": "Todos os Times", "value": "all"},
        {"label": "🏆 Libertadores (1-4)", "value": "libertadores"},
        {"label": "🌎 Sul-Americana (7-14)", "value": "sulamericana"},
        {"label": "⚠️ Rebaixamento (17-20)", "value": "rebaixamento"},
        {"label": "⬆️ Top 10 (Primeiros)", "value": "top10"},
        {"label": "⬇️ Bottom 10 (Últimos)", "value": "bottom10"},
    ]

    return html.Div(
        className="filters-section",
        children=[
            bottom_sheet(
                id="page-selector",
                label="Página",
                options=page_options,
                value="dashboard",
                placeholder="Selecione...",
                icon="📑"
            ),
            bottom_sheet(
                id="year-selector",
                label="Ano",
                options=[{"label": "2026", "value": 2026}],
                value=2026,
                placeholder="Selecione o ano...",
                icon="📅"
            ),
            bottom_sheet(
                id="month-selector",
                label="Mês",
                options=month_options,
                value=4,
                placeholder="Selecione...",
                icon="📅"
            ),
            bottom_sheet_team(
                id="team-selector",
                label="Time",
                times=times,
                value="",
                placeholder="Selecione um time...",
            ),
            bottom_sheet(
                id="top10-selector",
                label="Top 10",
                options=top10_options,
                value="all",
                placeholder="Selecione...",
                icon="📈"
            ),
            html.Div(
                id="sidebar-calendar",
                className="sidebar-calendar",
                children=[],
            ),
            html.Hr(
                className="sidebar-divider",
                style={
                    "margin": "36px 0",
                    "border": "none",
                    "borderTop": "2px solid #555",
                },
            ),
            html.Img(
                src="https://i.ibb.co/0yBYM9HS/bola.png",
                className="sidebar-calendar-ball",
                id="refresh-ball",
                n_clicks=0,
                style={
                    "width": "62px",
                    "height": "auto",
                    "display": "block",
                    "margin": "16px auto",
                    "objectFit": "contain",
                },
            ),
        ],
    )


def _toggle_button() -> html.Div:
    return html.Div(
        className="sidebar-toggle-bottom",
        children=html.Button(id="sidebar-toggle-bottom", children="→", n_clicks=0),
    )
