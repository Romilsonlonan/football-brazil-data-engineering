from dash import html
from pandas import DataFrame

TEAM_LOGOS = {
    'Athletico Paranaense': 'https://i.ibb.co/0jyrYDMw/atletico-paranaense.png',
    'Atlético Mineiro': 'https://i.ibb.co/HDnnBCGD/atletico-mineiro.png',
    'Bahia': 'https://i.ibb.co/Kcfjs29b/bahia.png',
    'Botafogo': 'https://i.ibb.co/7dy85bd2/botafogo.png',
    'Chapecoense': 'https://i.ibb.co/zTX3m1vn/chapecoense.png',
    'Corinthians': 'https://i.ibb.co/x8dbrzg6/corinthians.png',
    'Coritiba': 'https://i.ibb.co/6Jbcngx4/curitiba.png',
    'Cruzeiro': 'https://i.ibb.co/xWvBTvN/cruzeiro.png',
    'Flamengo': 'https://i.ibb.co/v49J8BDK/flamengo.png',
    'Fluminense': 'https://i.ibb.co/XZn8TH2H/fluminense.png',
    'Grêmio': 'https://i.ibb.co/938zRfGJ/gremio.png',
    'Internacional': 'https://i.ibb.co/0VVkcMbz/internacional.png',
    'Mirassol': 'https://i.ibb.co/chQkxwxD/mirassol.png',
    'Palmeiras': 'https://i.ibb.co/PGBxM25J/palmeiras.png',
    'Red Bull Bragantino': 'https://i.ibb.co/4RjYk9vW/redbull-bragantino.png',
    'Remo': 'https://i.ibb.co/wrhH6ZVk/remo.png',
    'Santos': 'https://i.ibb.co/3YpQt7Jc/santos.png',
    'São Paulo': 'https://i.ibb.co/GQ9wn1k1/sao-paulo.png',
    'Vasco da Gama': 'https://i.ibb.co/RTj73f35/vasco.png',
    'Vitória': 'https://i.ibb.co/mrBCRy8f/vitoria.png',
}


def classification_table(df: DataFrame) -> html.Table:
    rows = []
    for _, row in df.iterrows():
        pos = int(row["posicao"])
        if pos <= 4:
            badge = "posicao-g4"
        elif pos >= 17:
            badge = "posicao-rebaixamento"
        else:
            badge = "posicao-normal"

        time_name = row["time"]
        logo_url = TEAM_LOGOS.get(time_name)
        
        time_cell = html.Td(time_name, className="text-left")
        if logo_url:
            time_cell = html.Td(
                [
                    html.Img(src=logo_url, style={"width": "24px", "height": "24px", "margin-right": "8px", "verticalAlign": "middle"}),
                    html.Span(time_name)
                ],
                className="text-left"
            )

        rows.append(
            html.Tr(
                [
                    html.Td(html.Span(str(pos), className=f"posicao-badge {badge}"), className="text-center"),
                    time_cell,
                    html.Td(str(int(row["jogos"])), className="text-center"),
                    html.Td(str(int(row["vitorias"])), className="text-center"),
                    html.Td(str(int(row["empates"])), className="text-center"),
                    html.Td(str(int(row["derrotas"])), className="text-center"),
                    html.Td(str(int(row["gols_pro"])), className="text-center"),
                    html.Td(str(int(row["gols_contra"])), className="text-center"),
                    html.Td(str(int(row["saldo_gols"])), className="text-center"),
                    html.Td(str(int(row["pontos"])), className="text-center", style={"fontWeight": "bold"}),
                ]
            )
        )

    return html.Table(
        className="data-table",
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th("Pos", className="text-center"),
                        html.Th("Time", className="text-left"),
                        html.Th("J", className="text-center"),
                        html.Th("V", className="text-center"),
                        html.Th("E", className="text-center"),
                        html.Th("D", className="text-center"),
                        html.Th("GP", className="text-center"),
                        html.Th("GC", className="text-center"),
                        html.Th("SG", className="text-center"),
                        html.Th("Pts", className="text-center"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
    )



def roster_table(df: DataFrame) -> html.Table:
    cols_wanted = ["Nome", "Time", "Posição", "Idade", "NAC"]
    rename = {"NAC": "Nacionalidade"}
    cols = [c for c in cols_wanted if c in df.columns]

    df_view = df[cols].rename(columns=rename)
    
    # Define alignment for each column
    # Nome: left, Time: left, Posição: left, Idade: center, Nacionalidade: left
    alignments = {
        "Nome": "text-left",
        "Time": "text-left",
        "Posição": "text-left",
        "Idade": "text-center",
        "Nacionalidade": "text-left"
    }

    headers = [
        html.Th(rename.get(c, c), className=alignments.get(c, "text-left")) 
        for c in cols
    ]
    
    rows = []
    for _, row in df_view.iterrows():
        row_cells = []
        for c in cols:
            val = str(row[rename.get(c, c)])
            row_cells.append(html.Td(val, className=alignments.get(c, "text-left")))
        rows.append(html.Tr(row_cells))

    return html.Table(
        className="data-table",
        children=[html.Thead(html.Tr(headers)), html.Tbody(rows)],
    )


def metric_card(
    icon,
    value: str,
    label: str,
    highlight: bool = False,
    icon_class: str = "",
    card_class: str = "",
) -> html.Div:
    cls = f"metric-card {'highlight' if highlight else ''} {card_class}".strip()
    icon_class_name = f"metric-icon {icon_class}".strip()
    icon_element = (
        html.Div(icon, className=icon_class_name)
        if isinstance(icon, str)
        else html.Div(icon, className=icon_class_name)
    )
    return html.Div(
        className=cls,
        children=[
            icon_element,
            html.Div(value, className="metric-value"),
            html.Div(label, className="metric-label"),
        ],
    )
