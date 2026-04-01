from dash import html
from pandas import DataFrame

from dashboard.app.components.tables import roster_table, metric_card
from dashboard.app.services import DashboardService


def render(time: str) -> html.Div:
    if not time:
        return html.Div(
            className="loading",
            children=[html.H3("👈 Selecione um time na barra lateral para ver o elenco.")],
        )

    try:
        df = DashboardService.get_elenco_use_case().execute()
        df_time = df[df["Time"].str.contains(time, case=False, na=False)]

        posicoes = df_time["Posição"].value_counts()
        idades = df_time["Idade"].dropna()
        media_idade = float(idades.mean()) if len(idades) > 0 else 0
        nacionalidades = df_time["NAC"].nunique()

        return html.Div(children=[
            html.Div(className="page-header", children=[
                html.H1(f"👥 Elenco - {time}"),
                html.P(f"Total de jogadores: {len(df_time)}"),
            ]),
            html.Div(className="metrics-grid", children=[
                metric_card("🏟️", str(len(posicoes)), "Posições"),
                metric_card("🎂", f"{media_idade:.1f}", "Média de Idade"),
                metric_card("🌍", str(nacionalidades), "Nacionalidades"),
            ]),
            html.Div(className="table-card", children=[
                html.H3("📋 Jogadores", className="chart-title"),
                roster_table(df_time),
            ]),
        ])
    except Exception as e:
        return html.Div(
            className="loading",
            children=[html.H3(f"Erro ao carregar dados do elenco: {str(e)}")],
        )
