import sys
from pathlib import Path
from typing import Any

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from dash import Dash, html

from dashboard.app.services import DashboardService
from dashboard.app.components.sidebar import sidebar
from dashboard.app.callbacks.navigation import register

_INDEX_STRING = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { max-width: 100vw; margin: 0; padding: 0; }

            /* ── Sidebar: scroll interno, sem clipar dropdowns ── */
            .sidebar {
                overflow: visible !important;
            }
            .sidebar-scroll {
                overflow-y: auto !important;
                overflow-x: hidden !important;
                height: 100vh !important;
                padding: 20px 16px !important;
                box-sizing: border-box !important;
            }
            .filters-section { overflow: visible !important; }
            .app-container { overflow: visible !important; }

            /* ── Dropdown: controle (campo fechado) ── */
            .dash-dropdown .Select-control,
            .Select .Select-control {
                background-color: #1c2128 !important;
                border: 1px solid #30363d !important;
                border-radius: 6px !important;
                min-height: 36px !important;
                cursor: pointer !important;
            }
            .dash-dropdown .Select-placeholder,
            .Select-placeholder {
                color: #8b949e !important;
            }
            .dash-dropdown .Select-value-label,
            .Select-value-label,
            .Select-value-text {
                color: #c9d1d9 !important;
            }
            .Select-input > input {
                color: #c9d1d9 !important;
                caret-color: #c9d1d9 !important;
            }

            /* ── Menu flutuante ── */
            .dash-dropdown .Select-menu-outer,
            .Select-menu-outer {
                background-color: #1c2128 !important;
                border: 1px solid #388bfd !important;
                border-radius: 6px !important;
                box-shadow: 0 8px 32px rgba(0,0,0,0.8) !important;
                z-index: 999999 !important;
                position: absolute !important;
                top: 100% !important;
                left: 0 !important;
                right: 0 !important;
                max-height: 260px !important;
                overflow-y: auto !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                clip: auto !important;
                clip-path: none !important;
            }
            .Select-menu { overflow-y: auto !important; }

            /* ── Itens do menu (react-select v1 e v2+) ── */
            .VirtualizedSelectOption,
            .Select-option {
                background-color: #1c2128 !important;
                color: #c9d1d9 !important;
                padding: 10px 12px !important;
                font-size: 13px !important;
                cursor: pointer !important;
            }
            .VirtualizedSelectFocusedOption,
            .Select-option.is-focused,
            .VirtualizedSelectOption:hover,
            .Select-option:hover {
                background-color: #21262d !important;
                color: #ffffff !important;
            }
            .VirtualizedSelectSelectedOption,
            .Select-option.is-selected {
                background-color: #1f6feb !important;
                color: #ffffff !important;
            }

            /* ── Seta ── */
            .Select-arrow {
                border-color: #8b949e transparent transparent !important;
            }

            /* ── FORÇA MÁXIMA DE VISIBILIDADE ── */
            .Select-menu-outer {
                background-color: #00ff00 !important;
                color: #ff0000 !important;
                border: 5px solid yellow !important;
                width: 300px !important;
                min-height: 100px !important;
                padding: 20px !important;
            }

            .Select-option, 
            .VirtualizedSelectOption,
            div[role="option"] {
                background-color: #00ff00 !important;
                color: #ff0000 !important;
                border: 1px solid red !important;
                padding: 15px !important;
                font-size: 20px !important;
                font-weight: bold !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


def create_app(flask_server: Any = None, **kwargs) -> Dash:
    if flask_server is None:
        kwargs["suppress_callback_exceptions"] = True

    app = Dash(
        __name__,
        server=flask_server if flask_server else True,
        **kwargs,
    )
    app.title = "Dashboard Brasileirão"
    app.index_string = _INDEX_STRING

    times = DashboardService.get_times()

    app.layout = html.Div(
        className="app-container",
        children=[
            sidebar(times),
            html.Div(id="sidebar-overlay", className="sidebar-overlay"),
            html.Button(
                id="sidebar-toggle-bottom",
                className="sidebar-toggle-float",
                children="←",
                n_clicks=0,
            ),
            html.Div(
                id="main-content",
                className="main-content",
                children=[
                    html.Div(
                        id="page-content",
                        children=html.Div(
                            className="loading",
                            children=html.H3("Carregando dados..."),
                        ),
                    )
                ],
            ),
        ],
    )

    register(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8051)
