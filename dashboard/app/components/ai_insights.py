from dash import html
from dashboard.app.theme import COLORS

def ai_insights_card(insight_text: str) -> html.Div:
    """
    Componente que exibe o insight gerado pela IA em um card elegante.
    """
    return html.Div(
        className="ai-insight-card",
        children=[
            html.Div(
                className="ai-insight-header",
                children=[
                    html.Span("🤖 AI Insights", className="ai-insight-title"),
                    html.Span("✨", className="ai-insight-icon"),
                ]
            ),
            html.Div(
                className="ai-insight-content",
                children=[
                    html.P(insight_text, className="ai-insight-text")
                ]
            )
        ]
    )
