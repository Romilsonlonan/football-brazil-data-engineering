from dash import dcc, html
from pandas import DataFrame
import plotly.graph_objects as go

from dashboard.app.components.tables import metric_card
from dashboard.app.services import DashboardService


def render(time: str = None, month: int = None) -> html.Div:
    """Renderiza a página de elenco com estatísticas do Campeonato."""
    try:
        stats = DashboardService.get_estatisticas_campeonato(month)
        top_ca = DashboardService.get_top_cartoes_amarelos(4, month)
        top_cv = DashboardService.get_top_cartoes_vermelhos(4, month)
        top_artilheiros = DashboardService.get_top_artilheiros(5, month)

        goleiros = DataFrame()
        jogadores_campo = DataFrame()
        if time:
            goleiros = DashboardService.get_goalkeepers_by_team(time, month)
            jogadores_campo = DashboardService.get_field_players_by_team(time, month)

        return html.Div(
            children=[
                html.Div(
                    className="page-header",
                    children=[
                        html.H1("👥 Estatísticas do Campeonato"),
                        html.P("Dados completos do Brasileirão"),
                    ],
                ),
                # 4 cards principais
                html.Div(
                    className="metrics-grid",
                    children=[
                        metric_card(
                            "⚽",
                            f"{stats['artilheiro']['gols']}",
                            f"Artilheiro: {stats['artilheiro']['nome']}",
                            highlight=True,
                        ),
                        metric_card(
                            "🟨",
                            f"{stats['cartoes_amarelos']['total']}",
                            "Total Cartões Amarelos",
                            highlight=False,
                        ),
                        metric_card(
                            "🟥",
                            f"{stats['cartoes_vermelhos']['total']}",
                            "Total Cartões Vermelhos",
                            highlight=False,
                        ),
                        metric_card(
                            "🧤",
                            f"{stats['melhor_goleiro']['defesas']}",
                            f"Melhor Goleiro: {stats['melhor_goleiro']['nome']}",
                            highlight=True,
                        ),
                    ],
                ),
                # Gráficos de rosca (lado a lado)
                html.Div(
                    className="charts-grid",
                    children=[
                        html.Div(
                            className="chart-card",
                            children=[
                                html.Div(
                                    "🟨 Top 4 - Cartões Amarelos",
                                    className="chart-title",
                                ),
                                dcc.Graph(
                                    figure=_create_yellow_cards_donut(top_ca),
                                    config={"displayModeBar": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="chart-card",
                            children=[
                                html.Div(
                                    "🟥 Top 4 - Cartões Vermelhos",
                                    className="chart-title",
                                ),
                                dcc.Graph(
                                    figure=_create_red_cards_donut(top_cv),
                                    config={"displayModeBar": False},
                                ),
                            ],
                        ),
                    ],
                ),
                # Gráfico de barras - Top 5 Artilheiros
                html.Div(
                    className="chart-card",
                    style={"gridColumn": "span 2", "marginBottom": "20px"},
                    children=[
                        html.Div(
                            "⚽ Top 5 - Artilheiros do Campeonato",
                            className="chart-title",
                        ),
                        dcc.Graph(
                            figure=_create_scorers_bar_chart(top_artilheiros),
                            config={"displayModeBar": False},
                        ),
                    ],
                ),
                # Tabelas de elenco por time
                html.Div(
                    style={"display": "none" if time is None else "block"},
                    children=[
                        html.Div(
                            className="table-card",
                            children=[
                                html.Div(
                                    "🧤 Goleiros",
                                    className="chart-title",
                                ),
                                _create_table(goleiros),
                            ],
                        ),
                        html.Div(
                            className="table-card",
                            children=[
                                html.Div(
                                    "⚽ Jogadores em Campo",
                                    className="chart-title",
                                ),
                                _create_table(jogadores_campo),
                            ],
                        ),
                    ],
                ),
            ]
        )
    except Exception as e:
        return html.Div(
            className="loading",
            children=[html.H3(f"Erro ao carregar dados: {str(e)}")],
        )


def _create_table(df: DataFrame) -> html.Div:
    """Cria uma tabela HTML para o DataFrame."""
    if df.empty:
        return html.Div("Sem dados", className="table-empty")

    headers = df.columns.tolist()
    return html.Table(
        className="data-table",
        children=[
            html.Thead(html.Tr([html.Th(h) for h in headers])),
            html.Tbody(
                [
                    html.Tr([html.Td(str(row[col])) for col in headers])
                    for _, row in df.iterrows()
                ]
            ),
        ],
    )


def _create_yellow_cards_donut(df: DataFrame) -> go.Figure:
    """Cria gráfico de rosca para cartões amarelos."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados")
        return fig

    # Cores para os 4 primeiros
    colors = ["#f0c000", "#e6a800", "#d69f00", "#c79500"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=[f"{row['Nome']}\n({row['Time']})" for _, row in df.iterrows()],
                values=df["CA"].tolist(),
                hole=0.5,
                marker=dict(colors=colors),
                textinfo="label+value",
                textposition="outside",
                textfont=dict(color="white", size=10),
                hovertemplate="%{label}<br>Cartões: %{value}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
    )
    return fig


def _create_red_cards_donut(df: DataFrame) -> go.Figure:
    """Cria gráfico de rosca para cartões vermelhos."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados")
        return fig

    # Cores para os 4 primeiros
    colors = ["#f85149", "#da3633", "#b62324", "#8b1a1a"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=[f"{row['Nome']}\n({row['Time']})" for _, row in df.iterrows()],
                values=df["CV"].tolist(),
                hole=0.5,
                marker=dict(colors=colors),
                textinfo="label+value",
                textposition="outside",
                textfont=dict(color="white", size=10),
                hovertemplate="%{label}<br>Cartões: %{value}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
    )
    return fig


def _create_scorers_bar_chart(df: DataFrame) -> go.Figure:
    """Cria gráfico de barras para os top 5 artilheiros."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados")
        return fig

    # Cores para as posições
    colors = ["#3fb950", "#58a6ff", "#8957e5", "#d29922", "#8b949e"]

    fig = go.Figure(
        data=[
            go.Bar(
                x=[f"{row['Nome']} ({row['Time']})" for _, row in df.iterrows()],
                y=df["G"].tolist(),
                orientation="v",
                marker=dict(color=colors[: len(df)]),
                text=df["G"].tolist(),
                textposition="outside",
                textfont=dict(color="white", size=14),
                hovertemplate="<b>%{x}</b><br>Gols: %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        font=dict(color="white"),
        xaxis=dict(
            title="",
            tickfont=dict(color="white", size=11),
            tickangle=-45,
        ),
        yaxis=dict(
            title=dict(text="Gols", font=dict(color="white")),
            tickfont=dict(color="white"),
            gridcolor="rgba(255,255,255,0.1)",
        ),
        margin=dict(l=50, r=20, t=50, b=80),
        showlegend=False,
    )
    return fig
