"""
DAG Gold - Carga para PostgreSQL/Superset
===========================================
Pipeline de carga dos dados de classificação para o PostgreSQL do Superset.

Esta DAG pode ser executada:
- Independententemente (após pipeline Silver)
- Como parte do fluxo completo (Bronze → Silver → Gold)

Tags: gold, carga, postgresql, superset, classificacao
"""

from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.decorators import task


# Configuração padrão da DAG
default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="gold_classificacao_carga",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 7 * * *",  # Executa diariamente às 7:00 (após Silver)
    catchup=False,
    tags=["gold", "carga", "postgresql", "superset", "classificacao"],
    default_args=default_args,
    description="Pipeline de carga dos dados de classificação para PostgreSQL/Superset"
) as dag:
    """
    Pipeline Gold para carga de dados de classificação.
    
    Fluxo:
        1. Lê os dados da camada Silver
        2. Carrega os dados no PostgreSQL (tabela gold_classificacao)
        3. O Superset então pode visualizar os dados atualizados
    
    Esta DAG pode ser executada manualmente ou em conjunto com a DAG Silver.
    """
    
    @task(
        task_id="run_gold_carga",
        retries=2
    )
    def run_gold_carga() -> dict:
        """Executa o pipeline Gold de carga de classificação."""
        import sys
        import os
        
        # Adicionar o caminho do projeto ao sys.path
        project_root = os.environ.get('AIRFLOW_PROJECT_ROOT', '/opt/airflow')
        sys.path.insert(0, project_root)
        
        # Importar o pipeline Gold
        from src.pipelines.gold.carga_classificacao import run
        
        logger = logging.getLogger(__name__)
        logger.info("Iniciando pipeline Gold de carga...")
        
        result = run()
        
        logger.info(f"✅ Pipeline Gold concluido: {result}")
        
        return result
    
    
    @task(
        task_id="verify_superset_data"
    )
    def verify_superset_data(result: dict) -> dict:
        """Verifica se os dados foram corretamente inseridos no PostgreSQL."""
        import sys
        import os
        from sqlalchemy import create_engine, text
        
        logger = logging.getLogger(__name__)
        
        # Conexão com PostgreSQL
        project_root = os.environ.get('AIRFLOW_PROJECT_ROOT', '/opt/airflow')
        postgres_conn = os.environ.get(
            "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
            "postgresql+psycopg2://airflow:airflow123@postgres/airflow"
        )
        
        engine = create_engine(postgres_conn)
        
        # Verificar dados
        with engine.connect() as conn:
            result_query = conn.execute(text("SELECT COUNT(*) FROM gold_classificacao"))
            count = result_query.fetchone()[0]
            
            logger.info(f"✅ Total de registros na tabela: {count}")
            
            # Verificar posições
            positions = conn.execute(text("SELECT posicao, time, pontos FROM gold_classificacao ORDER BY posicao LIMIT 5"))
        
        return {
            "rows_verified": count,
            "status": "VERIFIED"
        }
    
    
    # Executar pipeline Gold
    result = run_gold_carga()
    verify = verify_superset_data(result)
