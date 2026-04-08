from dash import dcc, html

from dashboard.app.services import DashboardService


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
            html.H1("🏆 Brasileirão"),
            html.P("Campeonato Brasileiro 2026"),
        ],
    )


# def _nav_menu() -> html.Div:
#    return html.Div(
#        className="nav-menu",
#        children=[
#            html.Div("Painel de Controle", className="nav-title"),
#            html.Div(
#                id="nav-classificacao",
#                className="nav-item",
#                children=[html.Span("📋", className="nav-icon"), "Classificação"],
#            ),
#            html.Div(
#                id="nav-elenco",
#                className="nav-item",
#                children=[html.Span("👔", className="nav-icon"), "Elenco"],
#            ),
#        ],
#    )


def _filters(times: list[str]) -> html.Div:
    time_options = [{"label": "Todos os Times", "value": "all"}] + (
        [{"label": t, "value": t} for t in times] if times else []
    )
    if not times:
        time_options = [{"label": "Nenhum time disponível", "value": ""}]

    return html.Div(
        className="filters-section",
        children=[
            html.Label("Página", className="filter-label"),
            dcc.Dropdown(
                id="page-selector",
                options=[
                    {"label": "📊 Classificação", "value": "classificacao"},
                    {"label": "👥 Elenco", "value": "elenco"},
                ],
                value="dashboard",
                clearable=False,
            ),
            html.Label("Mês", className="filter-label"),
            dcc.Dropdown(
                id="month-selector",
                options=[
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
                ],
                value=4,
                clearable=False,
            ),
            html.Label("Time", className="filter-label"),
            dcc.Dropdown(
                id="team-selector",
                options=time_options,
                value="",
                clearable=True,
                placeholder="Selecione um time...",
                searchable=True,
            ),
            html.Label("Top 10", className="filter-label"),
            dcc.Dropdown(
                id="top10-selector",
                options=[
                    {"label": "Todos os Times", "value": "all"},
                    {"label": "🏆 Libertadores (1-4)", "value": "libertadores"},
                    {"label": "🌎 Sul-Americana (7-14)", "value": "sulamericana"},
                    {"label": "⚠️ Rebaixamento (17-20)", "value": "rebaixamento"},
                    {"label": "⬆️ Top 10 (Primeiros)", "value": "top10"},
                    {"label": "⬇️ Bottom 10 (Últimos)", "value": "bottom10"},
                ],
                value="all",
                clearable=False,
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
