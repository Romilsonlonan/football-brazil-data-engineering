import plotly.graph_objects as go
from pandas import DataFrame

from dashboard.app.theme import COLORS


def bar_chart(df: DataFrame, time: str = "Todos") -> go.Figure:
    if time == "Todos":
        top5 = df.head(5)
        fig = go.Figure()
        for col, name, color in [
            ("vitorias", "Vitórias", COLORS["success"]),
            ("empates", "Empates", COLORS["warning"]),
            ("derrotas", "Derrotas", COLORS["danger"]),
        ]:
            fig.add_trace(
                go.Bar(
                    y=top5["time"],
                    x=top5[col],
                    name=name,
                    marker_color=color,
                    orientation="h",
                    text=top5[col],
                    textposition="inside",
                )
            )
        fig.update_layout(
            title="📊 Top 5 - Desempenho por Tipo de Resultado",
            barmode="stack",
        )
    else:
        row = df[df["time"].str.contains(time, case=False)].iloc[0]
        fig = go.Figure(
            data=[
                go.Bar(
                    x=["Vitórias", "Empates", "Derrotas"],
                    y=[row["vitorias"], row["empates"], row["derrotas"]],
                    marker_color=[
                        COLORS["success"],
                        COLORS["warning"],
                        COLORS["danger"],
                    ],
                    text=[row["vitorias"], row["empates"], row["derrotas"]],
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(title=f"📊 {time} - Desempenho")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        font=dict(color=COLORS["text_primary"]),
        margin=dict(l=20, r=20, t=80, b=20),
    )
    return fig


def pie_chart(df: DataFrame, time: str = "Todos") -> go.Figure:
    if time == "Todos":
        values = [
            int(df["vitorias"].sum()),
            int(df["empates"].sum()),
            int(df["derrotas"].sum()),
        ]
    else:
        row = df[df["time"].str.contains(time, case=False)].iloc[0]
        values = [int(row["vitorias"]), int(row["empates"]), int(row["derrotas"])]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Vitórias", "Empates", "Derrotas"],
                values=values,
                marker_colors=[COLORS["success"], COLORS["warning"], COLORS["danger"]],
                hole=0.4,
                textinfo="label+percent",
                textposition="outside",
                hovertemplate="%{label}<br> %{value} jogos<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="🍩 Distribuição de Resultados",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=400,
        font=dict(color=COLORS["text_primary"]),
        margin=dict(l=20, r=20, t=80, b=20),
    )
    return fig


def g4_donut(df: DataFrame) -> go.Figure:
    g4 = df.head(4)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=g4["time"].tolist(),
                values=g4["pontos"].tolist(),
                hole=0.6,
                marker=dict(colors=["#3fb950", "#58a6ff", "#8957e5", "#d29922"]),
                textinfo="label+percent",
                textposition="outside",
                textfont=dict(color="white", size=12),
            )
        ]
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(color="white"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
    )
    return fig


def top10_bar(df: DataFrame, filtro: str = "all") -> tuple[go.Figure, str]:
    mapa = {
        "libertadores": (df.head(4), "🏆 Libertadores (1-4)"),
        "libertadores_pre": (df.head(6), "🏆 Libertadores + Pré (1-6)"),
        "sulamericana": (df.iloc[6:14], "🌎 Sul-Americana (7-14)"),
        "rebaixamento": (df.tail(4), "⚠️ Rebaixamento (17-20)"),
        "top10": (df.head(10), "⬆️ Top 10 - Primeiros Colocados"),
        "bottom10": (df.tail(10), "⬇️ Bottom 10 - Últimos Colocados"),
    }
    dados, titulo = mapa.get(filtro, (df.head(10), "📊 Top 10 - Pontuação"))

    fig = go.Figure(
        data=[
            go.Bar(
                x=dados["time"],
                y=dados["pontos"],
                marker=dict(
                    color=dados["pontos"], colorscale="Viridis", showscale=False
                ),
                text=[f"{i + 1}º" for i in range(len(dados))],
                textposition="outside",
                textfont=dict(color="white", size=12),
                hovertemplate="<b>%{x}</b><br>Pontos: %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        xaxis=dict(
            title="",
            tickfont=dict(color="white", size=10),
            gridcolor="rgba(255,255,255,0.1)",
        ),
        yaxis=dict(
            title=dict(text="Pontos", font=dict(color="white")),
            tickfont=dict(color="white"),
            gridcolor="rgba(255,255,255,0.1)",
            zerolinecolor="rgba(255,255,255,0.2)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=40, l=40, r=20),
        height=320,
        showlegend=False,
    )
    return fig, titulo
