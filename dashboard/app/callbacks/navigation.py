from dash import Dash, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dashboard.app.services import DashboardService
from dashboard.app.pages import dashboard, classificacao, elenco, calendario

def register(app: Dash) -> None:
    from dash import callback_context

    # ============================================================
    # Callback: Reset filters and refresh data
    # ============================================================
    @app.callback(
        [
            Output("page-selector-store", "data", allow_duplicate=True),
            Output("year-selector-store", "data", allow_duplicate=True),
            Output("month-selector-store", "data", allow_duplicate=True),
            Output("team-selector-store", "data", allow_duplicate=True),
            Output("top10-selector-store", "data", allow_duplicate=True),
            Output("page-selector-selected-label", "children", allow_duplicate=True),
            Output("year-selector-selected-label", "children", allow_duplicate=True),
            Output("month-selector-selected-label", "children", allow_duplicate=True),
            Output("team-selector-selected-label", "children", allow_duplicate=True),
            Output("top10-selector-selected-label", "children", allow_duplicate=True),
            Output("refresh-ball", "className", allow_duplicate=True),
        ],
        Input("refresh-ball", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_and_refresh(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        DashboardService.clear_cache()

        # Reset values
        new_page = "dashboard"
        new_year = 2026
        new_month = 4
        new_team = ""
        new_top10 = "all"
        
        new_page_label = "Dashboard"
        new_year_label = "2026"
        new_month_label = "Abril"
        new_team_label = "Selecione um time..."
        new_top10_label = "Todos os Times"
        
        return (
            new_page,
            new_year,
            new_month,
            new_team,
            new_top10,
            new_page_label,
            new_year_label,
            new_month_label,
            new_team_label,
            new_top10_label,
            "sidebar-calendar-ball" # Removed spin
        )

    # ============================================================
    # Callback: Controlar filtro de Time baseado na página
    # ============================================================
    @app.callback(
        [
            Output("team-selector", "style"),
            Output("top10-selector", "style"),
            Output("month-selector", "style"),
        ],
        Input("page-selector", "value"),
    )
    def update_filters_visibility(page: str) -> tuple[dict, dict, dict]:
        """Esconde filtros específicos conforme a página"""
        hidden = {"display": "none"}
        visible = {"display": "block"}

        if page == "classificacao":
            return visible, visible, visible
        elif page == "elenco":
            return visible, hidden, visible
        else:
            return visible, visible, hidden

    # ============================================================
    # Callback: Controlar botões de zona na bike image
    # ============================================================
    @app.callback(
        [
            Output("zone-t10", "className"),
            Output("zone-b10", "className"),
            Output("zone-g4", "className"),
            Output("zone-g6", "className"),
            Output("zone-g12", "className"),
            Output("zone-z4", "className"),
            Output("top10-selector-store", "data", allow_duplicate=True),
        ],
        [
            Input("zone-t10", "n_clicks"),
            Input("zone-b10", "n_clicks"),
            Input("zone-g4", "n_clicks"),
            Input("zone-g6", "n_clicks"),
            Input("zone-g12", "n_clicks"),
            Input("zone-z4", "n_clicks"),
        ],
        [State("top10-selector-store", "data")],
        prevent_initial_call=True,
    )
    def update_zone_buttons(t10, b10, g4, g6, g12, z4, current_filter):
        ctx = callback_context
        if not ctx.triggered:
            return "", "", "", "", "", "", current_filter

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Mapear botão para filtro
        zone_map = {
            "zone-t10": "top10",  # Top 10 (primeiros 10 da tabela)
            "zone-b10": "bottom10",  # Bottom 10 (últimos 10 da tabela)
            "zone-g4": "libertadores",  # Libertadores Fase de Grupos
            "zone-g6": "libertadores_pre",  # Libertadores Pré
            "zone-g12": "sulamericana",  # Sul-Americana
            "zone-z4": "rebaixamento",  # Rebaixamento
        }

        selected_zone = zone_map.get(button_id)
        if not selected_zone:
            return "", "", "", "", "", "", current_filter

        # Se já está selecionado, desmarca
        if current_filter == selected_zone:
            return "", "", "", "", "", "", "all"

        # Atualiza botão selecionado
        btn_classes = {
            "top10": "zone-btn-active",
            "bottom10": "zone-btn-active",
            "libertadores": "zone-btn-active",
            "libertadores_pre": "zone-btn-active",
            "sulamericana": "zone-btn-active",
            "rebaixamento": "zone-btn-active",
        }

        return (
            btn_classes.get(selected_zone, ""),
            btn_classes.get(selected_zone, ""),
            btn_classes.get(selected_zone, ""),
            btn_classes.get(selected_zone, ""),
            btn_classes.get(selected_zone, ""),
            btn_classes.get(selected_zone, ""),
            selected_zone,
        )

    # ============================================================
    # Callback: Controle de Sidebar
    # ============================================================
    @app.callback(
        [
            Output("sidebar", "className"),
            Output("sidebar-toggle-bottom", "children"),
            Output("sidebar-toggle-bottom", "className"),
            Output("main-content", "className"),
            Output("sidebar-overlay", "className"),
        ],
        [
            Input("sidebar-toggle-bottom", "n_clicks"),
            Input("sidebar-overlay", "n_clicks"),
        ],
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

    # ============================================================
    # Callback: Atualizar Calendário na Sidebar
    # ============================================================
    @app.callback(
        Output("sidebar-calendar", "children"),
        [
            Input("team-selector-store", "data"),
            Input("month-selector-store", "data"),
            Input("year-selector-store", "data"),
        ],
    )
    def update_sidebar_calendar(team: str, month: int, year: int) -> html.Div:
        from dashboard.app.pages import calendario

        team = team if team and team.strip() else None
        if not team:
            return html.Div(className="calendar-empty", children=[])
        return calendario.render_sidebar(team, month, year)

    # ============================================================
    # Callback: Atualizar Conteúdo da Página
    # ============================================================
    @app.callback(
        Output("page-content", "children"),
        [
            Input("page-selector-store", "data"),
            Input("team-selector-store", "data"),
            Input("top10-selector-store", "data"),
            Input("year-selector-store", "data"),
            Input("month-selector-store", "data"),
        ],
    )
    def update_page(page: str, team: str, top10_filter: str, year: int, month: int) -> html.Div:
        team = team if team and team.strip() else None
        top10_filter = top10_filter or "all"

        try:
            df = DashboardService.get_classificacao_df()
            if df is None or df.empty:
                raise ValueError("Dados de classificação indisponíveis.")
        except Exception as e:
            return html.Div(
                className="loading",
                children=[
                    html.H3("⚠️ Erro ao carregar dados"),
                    html.P(str(e)),
                ],
            )

        try:
            if page == "dashboard":
                return dashboard.render(df)
            if page == "classificacao":
                return classificacao.render(df, team, top10_filter)
            if page == "elenco":
                return elenco.render(team, month, year)

            return html.Div()
        except Exception as e:
            import traceback

            return html.Div(
                className="loading",
                children=[
                    html.H3("⚠️ Erro ao renderizar página"),
                    html.Pre(traceback.format_exc()),
                ],
            )
