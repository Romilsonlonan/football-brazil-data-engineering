from dash import Dash, html
from dash.dependencies import Input, Output, State

from dashboard.app.services import DashboardService
from dashboard.app.pages import dashboard, classificacao, elenco


def register(app: Dash) -> None:
    @app.callback(
        [
            Output("sidebar", "className"),
            Output("sidebar-toggle-bottom", "children"),
            Output("sidebar-toggle-bottom", "className"),
            Output("main-content", "className"),
            Output("sidebar-overlay", "className"),
        ],
        [Input("sidebar-toggle-bottom", "n_clicks"),
         Input("sidebar-overlay", "n_clicks")],
    )
    def toggle_sidebar(n_toggle, n_overlay):
        total = (n_toggle or 0) + (n_overlay or 0)
        if total % 2 != 0:
            return (
                "sidebar collapsed",
                "→",
                "sidebar-toggle-float open",
                "main-content expanded",
                "sidebar-overlay",
            )
        return (
            "sidebar",
            "←",
            "sidebar-toggle-float",
            "main-content",
            "sidebar-overlay visible",
        )

    @app.callback(
        Output("page-content", "children"),
        [
            Input("page-selector", "value"),
            Input("team-selector", "value"),
            Input("top10-selector", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_page(page: str, team: str, top10_filter: str) -> html.Div:
        team = team if team and team.strip() else None
        top10_filter = top10_filter or "all"

        try:
            df = DashboardService.get_classificacao_df()
            if df is None or df.empty:
                raise ValueError("Dados de classificação indisponíveis.")
        except Exception as e:
            return html.Div(className="loading", children=[
                html.H3("⚠️ Erro ao carregar dados"),
                html.P(str(e)),
            ])

        if page == "dashboard":
            return dashboard.render(df)
        if page == "classificacao":
            return classificacao.render(df, team, top10_filter)
        if page == "elenco":
            return elenco.render(team)

        return html.Div()
