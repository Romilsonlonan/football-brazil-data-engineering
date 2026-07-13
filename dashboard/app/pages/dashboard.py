from dash import dcc, html
from pandas import DataFrame

from dashboard.app.components.charts import bar_chart, pie_chart
from dashboard.app.components.tables import classification_table, metric_card
from dashboard.app.components.ai_insights import ai_insights_card


def render(df: DataFrame) -> html.Div:
    lider = df.iloc[0]["time"] if len(df) > 0 else "N/A"

    return html.Div(children=[
        html.Div(className="page-header", children=[
            html.H1("🏠 Painel de Controle"),
            html.P("Bem-vindo ao Dashboard do Brasileirão 2026!"),
        ]),
        html.Div(className="metrics-grid", children=[
            metric_card("🏆", lider, "Líder", highlight=True),
            metric_card("⭐", f"{int(df['pontos'].sum()):,}", "Total Pontos"),
            metric_card("🎯", str(int(df["vitorias"].sum())), "Total Vitórias"),
            metric_card("⚽", f"{int(df['gols_pro'].sum()):,}", "Gols Marcados"),
        ]),
        html.Div(id="ai-insight-container", className="ai-insight-container", children=[
            html.Div(className="loading", children=[
                html.P("🤖 Analisando dados para gerar insights...", style={"fontStyle": "italic", "color": "#8b949e"})
            ])
        ]),
        html.Div(className="charts-grid", children=[
            html.Div(className="chart-card", children=[
                html.Div("📈 Desempenho", className="chart-title"),
                dcc.Graph(figure=bar_chart(df, "Todos"), config={"displayModeBar": False}),
            ]),
            html.Div(className="chart-card", children=[
                html.Div("🍩 Resultados", className="chart-title"),
                dcc.Graph(figure=pie_chart(df, "Todos"), config={"displayModeBar": False}),
            ]),
        ]),
        html.Div(className="table-card", children=[
            html.H3("📋 Classificação Geral", className="chart-title"),
            classification_table(df),
        ]),
    ])
