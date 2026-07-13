"""Bottom Sheet component for sidebar filters."""

from dash import dcc, html
from typing import List, Dict, Any


def bottom_sheet(
    id: str,
    label: str,
    options: List[Dict[str, Any]],
    value: Any = None,
    placeholder: str = "Selecione...",
    icon: str = "📋",
) -> html.Div:
    """Creates a bottom sheet filter component - opens within sidebar."""

    selected_label = placeholder
    for opt in options:
        if opt.get("value") == value:
            selected_label = opt.get("label", placeholder)
            break

    option_buttons = []
    for opt in options:
        is_selected = opt["value"] == value
        option_buttons.append(
            html.Button(
                className=f"bs-option {'bs-option-selected' if is_selected else ''}",
                children=opt["label"],
                id={"type": f"{id}-option", "index": str(opt["value"])},
                n_clicks=0,
            )
        )

    return html.Div(
        className="bottom-sheet-container",
        children=[
            html.Label(label, className="filter-label"),
            html.Button(
                id=f"{id}-trigger",
                className="bottom-sheet-trigger",
                n_clicks=0,
                children=[
                    html.Span(icon, className="bs-icon"),
                    html.Span(selected_label, className="bs-selected", id=f"{id}-selected-label"),
                    html.Span("▼", className="bs-arrow"),
                ],
            ),
            dcc.Store(id=f"{id}-store", data=value),
            dcc.Store(id=f"{id}-options", data=options),
            html.Div(
                id=f"{id}-content",
                className="bottom-sheet-content",
                style={"display": "none"},
                children=[
                    html.Div(
                        className="bs-panel",
                        children=[
                            html.Div(
                                className="bs-header",
                                children=[
                                    html.H3(label, className="bs-title"),
                                    html.Button(
                                        "✕",
                                        id=f"{id}-close",
                                        className="bs-close",
                                        n_clicks=0,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="bs-options",
                                children=option_buttons,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def bottom_sheet_team(
    id: str,
    label: str,
    times: List[str],
    value: str = "",
    placeholder: str = "Selecione um time...",
) -> html.Div:
    """Creates a bottom sheet for team selection with search - within sidebar."""

    options = [{"label": "Todos os Times", "value": "all"}] + [
        {"label": t, "value": t} for t in times
    ]

    selected_label = placeholder
    for opt in options:
        if opt.get("value") == value:
            selected_label = opt.get("label", placeholder)
            break

    option_buttons = []
    for opt in options:
        is_selected = opt["value"] == value
        option_buttons.append(
            html.Button(
                className=f"bs-option {'bs-option-selected' if is_selected else ''}",
                children=opt["label"],
                id={"type": f"{id}-option", "index": str(opt["value"])},
                n_clicks=0,
            )
        )

    return html.Div(
        className="bottom-sheet-container",
        children=[
            html.Label(label, className="filter-label"),
            html.Button(
                id=f"{id}-trigger",
                className="bottom-sheet-trigger",
                n_clicks=0,
                children=[
                    html.Span("⚽", className="bs-icon"),
                    html.Span(selected_label, className="bs-selected", id=f"{id}-selected-label"),
                    html.Span("▼", className="bs-arrow"),
                ],
            ),
            dcc.Store(id=f"{id}-store", data=value),
            dcc.Store(id=f"{id}-options", data=options),
            html.Div(
                id=f"{id}-content",
                className="bottom-sheet-content",
                style={"display": "none"},
                children=[
                    html.Div(
                        className="bs-panel bs-panel-search",
                        children=[
                            html.Div(
                                className="bs-header",
                                children=[
                                    html.H3(label, className="bs-title"),
                                    html.Button(
                                        "✕",
                                        id=f"{id}-close",
                                        className="bs-close",
                                        n_clicks=0,
                                    ),
                                ],
                            ),
                            dcc.Input(
                                id=f"{id}-search",
                                className="bs-search",
                                placeholder="🔍 Buscar time...",
                                type="text",
                                value="",
                            ),
                            html.Div(
                                id=f"{id}-options-container",
                                className="bs-options-scroll",
                                children=option_buttons,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
