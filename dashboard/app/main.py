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
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
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

