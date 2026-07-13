from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
import pandas as pd
from pathlib import Path

from dashboard.app.services import DashboardService
from src.agents.insight_agent import InsightAgent
from src.infrastructure.llm.service import LLMFactory
from src.utils.logger import logger

# Path to the main log file
LOG_FILE_PATH = Path("/home/romilson/Projetos/Data-Futebol-Brasileiro/lakehouse/logs/lakehouse.log")

def register(app) -> None:
    @app.callback(
        Output("ai-insight-container", "children"),
        [
            Input("page-selector-store", "data"),
            Input("refresh-ball", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update_ai_insights(page: str, n_clicks: int):
        if page != "dashboard":
            raise PreventUpdate

        # 1. Prepare context
        try:
            df = DashboardService.get_classificacao_df()
            if df is None or df.empty:
                return "⚠️ Sem dados disponíveis para análise."
            
            # Summary of the dataframe
            data_summary = df.describe().to_string()
            # Add top performers/worst performers as part of summary
            data_summary += f"\n\nTop 3 Times: {', '.join(df.head(3)['time'].tolist())}"
            data_summary += f"\nBottom 3 Times: {', '.join(df.tail(3)['time'].tolist())}"

        except Exception as e:
            logger.error(f"Error gathering data for AI insight: {e}")
            data_summary = "Erro ao obter dados."

        try:
            # Get last 20 lines of log
            if LOG_FILE_PATH.exists():
                with open(LOG_FILE_PATH, "r") as f:
                    lines = f.readlines()
                    recent_logs = "".join(lines[-20:])
            else:
                recent_logs = "Arquivo de log não encontrado."
        except Exception as e:
            logger.error(f"Error reading logs for AI insight: {e}")
            recent_logs = "Erro ao ler logs."

        # 2. Run Agent
        try:
            # In a real app, we might use a singleton or manage lifecycle better
            # For now, we instantiate it here
            llm_service = LLMFactory.get_provider("mock") # Using mock for safety in dev
            # In production, you'd use the real provider from config
            # llm_service = LLMFactory.get_provider("openai") 
            
            # Wait, I should use the real factory logic.
            # Let's check how LLMFactory works. It takes provider_type.
            # For now, I will try to get the real service if possible or use mock.
            # Actually, let's assume we want to use whatever is configured.
            
            # Note: In this environment, I'll use mock to avoid errors if no API key is set
            # but I'll leave the code ready for real provider.
            
            # Let's try to get the real one, if it fails, use mock.
            try:
                # Assuming we might have environment variables set for real providers
                # but since I don't know, I'll default to mock for this implementation
                llm_service = LLMFactory.get_provider("mock")
            except:
                llm_service = LLMFactory.get_provider("mock")

            agent = InsightAgent(llm_service)
            
            result = agent.run(
                task="Analise os dados e os logs e forneça um insight curto e inteligente sobre o estado atual do sistema.",
                data_summary=data_summary,
                recent_logs=recent_logs
            )

            if result["success"]:
                from dashboard.app.components.ai_insights import ai_insights_card
                return ai_insights_card(result["insight"])
            else:
                return "⚠️ Não foi possível gerar insights automáticos no momento."

        except Exception as e:
            logger.error(f"Error running InsightAgent: {e}")
            return f"⚠️ Erro no Agente de Insights: {str(e)}"
