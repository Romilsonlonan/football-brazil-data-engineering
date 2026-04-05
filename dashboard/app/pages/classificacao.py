from dash import dcc, html
from pandas import DataFrame

from dashboard.app.components.charts import bar_chart, pie_chart, g4_donut, top10_bar
from dashboard.app.components.tables import classification_table, metric_card


_ZONE_BUTTONS = [
    {"label": "T10", "title": "Zona Superior",              "color": "#58a6ff", "id": "zone-t10"},
    {"label": "B10", "title": "Zona Inferior",              "color": "#8b949e", "id": "zone-b10"},
    {"label": "G4",  "title": "Libertadores - fase de grupos", "color": "#3fb950", "id": "zone-g4"},
    {"label": "G6",  "title": "Libertadores - incluindo pré",  "color": "#2ea043", "id": "zone-g6"},
    {"label": "G12", "title": "Sul-Americana",              "color": "#d29922", "id": "zone-g12"},
    {"label": "Z4",  "title": "Rebaixamento",               "color": "#f85149", "id": "zone-z4"},
]


def _zone_buttons() -> html.Div:
    buttons = [
        html.Button(
            btn["label"],
            title=btn["title"],
            id=btn["id"],
            n_clicks=0,
            style={
                "backgroundColor": btn["color"],
                "width": "52px",
                "height": "52px",
                "borderRadius": "50%",
                "border": "none",
                "color": "#ffffff",
                "fontSize": "12px",
                "fontWeight": "700",
                "cursor": "pointer",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "boxShadow": "0 3px 10px rgba(0,0,0,0.4)",
                "flexShrink": "0",
            },
        )
        for btn in _ZONE_BUTTONS
    ]
    return html.Div(
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "10px",
            "marginTop": "16px",
            "justifyContent": "center",
            "width": "100%",
        },
        children=buttons,
    )


def render(df: DataFrame, time: str = None, top10_filter: str = "all") -> html.Div:
    if time:
        return _render_time(df, time)
    return _render_geral(df, top10_filter)


def _render_time(df: DataFrame, time: str) -> html.Div:
    row = df[df["time"].str.contains(time, case=False)].iloc[0]
    df_time = df[df["time"].str.contains(time, case=False)]

    return html.Div(children=[
        html.Div(className="page-header", children=[
            html.H1(f"📊 {time}"),
            html.P("Estatísticas detalhadas do time"),
        ]),
        html.Div(className="metrics-grid", children=[
            metric_card("📍", f"#{int(row['posicao'])}", "Posição", highlight=True),
            metric_card("⭐", str(int(row["pontos"])), "Pontos"),
            metric_card("🏆", str(int(row["vitorias"])), "Vitórias"),
            metric_card("⚽", str(int(row["saldo_gols"])), "Saldo de Gols"),
        ]),
        html.Div(className="charts-grid", children=[
            html.Div(className="chart-card", children=[
                html.Div("📈 Desempenho", className="chart-title"),
                dcc.Graph(figure=bar_chart(df, time), config={"displayModeBar": False}),
            ]),
            html.Div(className="chart-card", children=[
                html.Div("🍩 Resultados", className="chart-title"),
                dcc.Graph(figure=pie_chart(df, time), config={"displayModeBar": False}),
            ]),
        ]),
        html.Div(className="table-card", children=[
            html.H3("📋 Estatísticas Detalhadas", className="chart-title"),
            classification_table(df_time),
        ]),
    ])


def _render_geral(df: DataFrame, top10_filter: str) -> html.Div:
    fig_top10, titulo_top10 = top10_bar(df, top10_filter)

    return html.Div(children=[
        html.Div(className="page-header", children=[
            html.H1("📊 Classificação"),
            html.P("Tabela completa do Brasileirão"),
        ]),
        html.Div(className="metrics-grid", children=[
            metric_card("🏆", df.iloc[0]["time"], "Líder", highlight=True),
            metric_card("⭐", f"{int(df['pontos'].sum()):,}", "Total Pontos"),
            metric_card("🎯", str(int(df["vitorias"].sum())), "Total Vitórias"),
            metric_card("⚽", f"{int(df['gols_pro'].sum()):,}", "Gols Marcados"),
        ]),
        html.Div(className="charts-grid", children=[
            html.Div(className="chart-card", children=[
                html.Div("🍩 G4 - Top 4 Brasileirão", className="chart-title"),
                dcc.Graph(figure=g4_donut(df), config={"displayModeBar": False}),
            ]),
            html.Div(className="chart-card", style={"display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "space-between"}, children=[
                html.Img(
                    src="https://i.ibb.co/yn8j92yK/bicicleta.png",
                    style={"width": "100%", "height": "220px", "objectFit": "contain", "borderRadius": "12px"},
                    id="bike-image",
                ),
                _zone_buttons(),
            ]),
        ]),
        html.Div(className="chart-card", style={"gridColumn": "span 2", "marginBottom": "30px"}, children=[
            html.Div(titulo_top10, className="chart-title"),
            dcc.Graph(figure=fig_top10, config={"displayModeBar": False}),
        ]),
        html.Div(className="table-card", children=[
            html.H3("📋 Classificação Geral", className="chart-title"),
            classification_table(df),
        ]),
    ])
