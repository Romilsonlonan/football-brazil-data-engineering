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
        df_filtered = df[df["time"].str.contains(time, case=False, na=False)]
        if df_filtered.empty:
            return go.Figure()
        row = df_filtered.iloc[0]
        # Convert numpy types to native Python
        vitorias = int(row["vitorias"])
        empates = int(row["empates"])
        derrotas = int(row["derrotas"])
        fig = go.Figure(
            data=[
                go.Bar(
                    x=["Vitórias", "Empates", "Derrotas"],
                    y=[vitorias, empates, derrotas],
                    marker_color=[
                        COLORS["success"],
                        COLORS["warning"],
                        COLORS["danger"],
                    ],
                    text=[vitorias, empates, derrotas],
                    textposition="outside",
                )
            ]
        )

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
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="white", size=11),
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


def create_zone_probability_chart(posicao: int, df: DataFrame) -> go.Figure:
    """Cria gráfico de rosca com probabilidade de zonas."""
    if posicao < 1 or posicao > 20:
        return go.Figure()
    jogos_disputados = df["jogos"].max() if "jogos" in df.columns else 10
    jogos_restantes = max(0, 38 - jogos_disputados)

    # Calcular pontos atuais e possíveis
    pontos_atuais = (
        df[df["time"].str.contains("Athletico Paranaense", case=False, na=False)][
            "pontos"
        ].iloc[0]
        if not df[
            df["time"].str.contains("Athletico Paranaense", case=False, na=False)
        ].empty
        else 0
    )
    pontos_maximos = pontos_atuais + (jogos_restantes * 3)

    # Porcentagem teórica baseada na posição
    total_times = len(df)
    pct = 100 / total_times

    zonas = {
        "G4": pct * 4 if posicao <= 4 else pct * (posicao - 4),
        "G6": pct * 6 if posicao <= 6 else pct * (posicao - 6),
        "G14": pct * 14 if posicao <= 14 else pct * (posicao - 14),
        "Z4": pct * 4 if posicao >= 17 else 0,
    }

    labels = []
    values = []
    colors = []
    percentages = []

    for zona, pct_zona in zonas.items():
        pct_val = max(0, pct_zona)
        values.append(pct_val)
        percentages.append(f"{pct_val:.0f}%")

        if zona == "G4":
            colors.append("#3fb950")
            labels.append(
                f"G4: {'✅ Garantido' if posicao <= 4 else f'{pct_val:.0f}%'}"
            )
        elif zona == "G6":
            colors.append("#58a6ff")
            labels.append(
                f"G6: {'✅ Garantido' if posicao <= 6 else f'{pct_val:.0f}%'}"
            )
        elif zona == "G14":
            colors.append("#8957e5")
            labels.append(
                f"G14: {'✅ Garantido' if posicao <= 14 else f'{pct_val:.0f}%'}"
            )
        elif zona == "Z4":
            colors.append("#f85149")
            labels.append(
                f"Z4: {'⚠️ Rebaixado' if posicao >= 17 else f'{pct_val:.0f}%'}"
            )
        else:
            colors.append("#6e7681")
            labels.append(f"{zona}: {pct_val:.0f}%")

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker=dict(colors=colors),
                textinfo="percent",
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
            y=-0.35,
            xanchor="center",
            x=0.5,
            font=dict(color="white", size=11),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=100, l=20, r=20),
        height=350,
    )
    return fig
