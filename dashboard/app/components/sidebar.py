from dash import dcc, html

from dashboard.app.services import DashboardService


def sidebar(times: list[str]) -> html.Div:
    return html.Div(
        id="sidebar",
        className="sidebar",
        children=[
            _logo(),
            _nav_menu(),
            _filters(times),
        ],
    )


def _logo() -> html.Div:
    return html.Div(
        className="sidebar-logo",
        children=[
            html.H1("🏆 Brasileirão"),
            html.P("Painel de Controle 2026"),
        ],
    )


def _nav_menu() -> html.Div:
    return html.Div(
        className="nav-menu",
        children=[
            html.Div("Painel de Controle", className="nav-title"),
            html.Div(
                id="nav-classificacao",
                className="nav-item",
                children=[html.Span("📋", className="nav-icon"), "Classificação"],
            ),
            html.Div(
                id="nav-elenco",
                className="nav-item",
                children=[html.Span("👔", className="nav-icon"), "Elenco"],
            ),
        ],
    )


def _filters(times: list[str]) -> html.Div:
    time_options = (
        [{"label": t, "value": t} for t in times]
        if times
        else [{"label": "Nenhum time disponível", "value": ""}]
    )

    return html.Div(
        className="filters-section",
        children=[
            html.Label("Página", className="filter-label"),
            dcc.Dropdown(
                id="page-selector",
                options=[
                    {"label": "🏠 Painel de Controle", "value": "dashboard"},
                    {"label": "📊 Classificação", "value": "classificacao"},
                    {"label": "👥 Elenco", "value": "elenco"},
                ],
                value="dashboard",
                clearable=False,
            ),
            html.Label("Time", className="filter-label"),
            dcc.Dropdown(
                id="team-selector",
                options=time_options,
                value="",
                clearable=True,
                placeholder="Selecione um time...",
            ),
            html.Label("Top 10", className="filter-label"),
            dcc.Dropdown(
                id="top10-selector",
                options=[
                    {"label": "Todos os Times", "value": "all"},
                    {"label": "🏆 Libertadores (1-6)", "value": "libertadores"},
                    {"label": "🌎 Sul-Americana (7-14)", "value": "sulamericana"},
                    {"label": "⚠️ Rebaixamento (17-20)", "value": "rebaixamento"},
                ],
                value="all",
                clearable=False,
            ),
        ],
    )


def _toggle_button() -> html.Div:
    return html.Div(
        className="sidebar-toggle-bottom",
        children=html.Button(id="sidebar-toggle-bottom", children="→", n_clicks=0),
    )
