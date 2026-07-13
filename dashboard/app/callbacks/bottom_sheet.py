"""Callbacks for Bottom Sheet filter interactions."""

from dash import Dash, ALL, html
from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
from typing import List, Dict, Any

def _get_label_from_options(new_value: Any, options: List[Dict[str, Any]], placeholder: str) -> str:
    """Helper to find the label for a given value in options."""
    for opt in options:
        if str(opt.get("value")) == str(new_value):
            return opt.get("label", placeholder)
    return placeholder


def register(app: Dash):
    """Register all bottom sheet callbacks."""
    @app.callback(
        [Output("page-selector-content", "style")],
        [
            Input("page-selector-trigger", "n_clicks"),
            Input("page-selector-close", "n_clicks"),
        ],
        [State("page-selector-content", "style")],
        prevent_initial_call=True,
    )
    def page_selector_toggle(n_trigger, n_close, current_style):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered[0]["prop_id"]

        if "trigger" in trigger and n_trigger:
            return [{"display": "block"}]

        if "close" in trigger and n_close:
            return [{"display": "none"}]

        return [no_update]

    # Page selector options - update store, label and close panel
    @app.callback(
        [
            Output("page-selector-store", "data", allow_duplicate=True),
            Output("page-selector-content", "style", allow_duplicate=True),
            Output("page-selector-selected-label", "children", allow_duplicate=True),
        ],
        [Input({"type": "page-selector-option", "index": ALL}, "n_clicks")],
        [
            State("page-selector-store", "data"),
            State("page-selector-options", "data"),
        ],
        prevent_initial_call=True,
    )
    def page_selector_options(selected_btn, current_value, options):
        if not callback_context.triggered:
            raise PreventUpdate

        prop_id = callback_context.triggered_id
        new_value = prop_id.get("index")
        
        # Find label
        new_label = _get_label_from_options(new_value, options, "Selecione...")

        return [new_value, {"display": "none"}, new_label]

    # Month selector - toggle panel
    @app.callback(
        [Output("month-selector-content", "style")],
        [
            Input("month-selector-trigger", "n_clicks"),
            Input("month-selector-close", "n_clicks"),
        ],
        [State("month-selector-content", "style")],
        prevent_initial_call=True,
    )
    def month_selector_toggle(n_trigger, n_close, current_style):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered[0]["prop_id"]

        if "trigger" in trigger and n_trigger:
            return [{"display": "block"}]

        if "close" in trigger and n_close:
            return [{"display": "none"}]

        return [no_update]

    # Month selector options - update store, label and close panel
    @app.callback(
        [
            Output("month-selector-store", "data", allow_duplicate=True),
            Output("month-selector-content", "style", allow_duplicate=True),
            Output("month-selector-selected-label", "children", allow_duplicate=True),
        ],
        [Input({"type": "month-selector-option", "index": ALL}, "n_clicks")],
        [
            State("month-selector-store", "data"),
            State("month-selector-options", "data"),
        ],
        prevent_initial_call=True,
    )
    def month_selector_options(selected_btn, current_value, options):
        if not callback_context.triggered:
            raise PreventUpdate

        prop_id = callback_context.triggered_id
        new_value = int(prop_id.get("index"))
        
        # Find label
        new_label = _get_label_from_options(new_value, options, "Selecione...")

        return [new_value, {"display": "none"}, new_label]

    # Team selector - toggle panel
    @app.callback(
        [Output("team-selector-content", "style")],
        [
            Input("team-selector-trigger", "n_clicks"),
            Input("team-selector-close", "n_clicks"),
        ],
        [State("team-selector-content", "style")],
        prevent_initial_call=True,
    )
    def team_selector_toggle(n_trigger, n_close, current_style):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered[0]["prop_id"]

        if "trigger" in trigger and n_trigger:
            return [{"display": "block"}]

        if "close" in trigger and n_close:
            return [{"display": "none"}]

        return [no_update]

    # Team selector options - update store and close panel
    @app.callback(
        [
            Output("team-selector-store", "data", allow_duplicate=True),
            Output("team-selector-content", "style", allow_duplicate=True),
            Output("team-selector-selected-label", "children", allow_duplicate=True),
        ],
        [Input({"type": "team-selector-option", "index": ALL}, "n_clicks")],
        [
            State("team-selector-store", "data"),
            State("team-selector-options", "data"),
        ],
        prevent_initial_call=True,
    )
    def team_selector_options(selected_btn, current_value, options):
        if not callback_context.triggered:
            raise PreventUpdate

        prop_id = callback_context.triggered_id
        new_value = prop_id.get("index")
        
        # Find label
        new_label = _get_label_from_options(new_value, options, "Selecione um time...")

        return [new_value, {"display": "none"}, new_label]

    # Top 10 selector - toggle panel
    @app.callback(
        [Output("top10-selector-content", "style")],
        [
            Input("top10-selector-trigger", "n_clicks"),
            Input("top10-selector-close", "n_clicks"),
        ],
        [State("top10-selector-content", "style")],
        prevent_initial_call=True,
    )
    def top10_selector_toggle(n_trigger, n_close, current_style):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered[0]["prop_id"]

        if "trigger" in trigger and n_trigger:
            return [{"display": "block"}]

        if "close" in trigger and n_close:
            return [{"display": "none"}]

        return [no_update]

    # Reset filters - refresh ball
    # (Moved to navigation.py to avoid duplicate output conflicts and ensure atomic reset/refresh)
