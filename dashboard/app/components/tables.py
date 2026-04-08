from dash import html
from pandas import DataFrame


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

        rows.append(
            html.Tr(
                [
                    html.Td(html.Span(str(pos), className=f"posicao-badge {badge}")),
                    html.Td(row["time"]),
                    html.Td(str(int(row["jogos"]))),
                    html.Td(str(int(row["vitorias"]))),
                    html.Td(str(int(row["empates"]))),
                    html.Td(str(int(row["derrotas"]))),
                    html.Td(str(int(row["gols_pro"]))),
                    html.Td(str(int(row["gols_contra"]))),
                    html.Td(str(int(row["saldo_gols"]))),
                    html.Td(str(int(row["pontos"]))),
                ]
            )
        )

    return html.Table(
        className="data-table",
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th("Pos"),
                        html.Th("Time"),
                        html.Th("J"),
                        html.Th("V"),
                        html.Th("E"),
                        html.Th("D"),
                        html.Th("GP"),
                        html.Th("GC"),
                        html.Th("SG"),
                        html.Th("Pts"),
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
    headers = [html.Th(rename.get(c, c)) for c in cols]
    rows = [
        html.Tr([html.Td(str(row[rename.get(c, c)])) for c in cols])
        for _, row in df_view.iterrows()
    ]

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
