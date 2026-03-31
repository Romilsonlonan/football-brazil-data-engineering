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
from airflow.providers.postgres.hooks.postgres import PostgresHook


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
    description="Pipeline de carga dos dados de classificação para PostgreSQL/Superset",
) as dag:
    """
    Pipeline Gold para carga de dados de classificação.

    Fluxo:
        1. Lê os dados da camada Silver
        2. Carrega os dados no PostgreSQL (tabela gold_classificacao)
        3. O Superset então pode visualizar os dados atualizados

    Esta DAG pode ser executada manualmente ou em conjunto com a DAG Silver.
    """

    @task(task_id="run_gold_carga", retries=2)
    def run_gold_carga() -> dict:
        """Executa o pipeline Gold de carga de classificação."""
        import sys
        import os

        # Adicionar o caminho do projeto ao sys.path
        project_root = os.environ.get("AIRFLOW_PROJECT_ROOT", "/opt/airflow")
        sys.path.insert(0, project_root)

        # Importar o pipeline Gold
        from src.pipelines.gold.carga_classificacao import run

        logger = logging.getLogger(__name__)
        logger.info("Iniciando pipeline Gold de carga...")

        result = run()

        logger.info(f"✅ Pipeline Gold concluido: {result}")

        return result

    @task(task_id="verify_superset_data")
    def verify_superset_data(result: dict) -> dict:
        """Verifica se os dados foram corretamente inseridos no PostgreSQL.

        Usa PostgresHook do Airflow para:
        - Gerenciamento seguro de conexões (sem senhas no código)
        - Método get_pandas_df para consultas integradas com Pandas

        Args:
            result: Resultado da tarefa anterior (run_gold_carga)
            postgres_conn_id: ID da conexão do Airflow (padrão: 'postgres_default')

        Returns:
            dict com total de registros verificados e status
        """
        from airflow.models import Variable

        logger = logging.getLogger(__name__)

        # Obtém o ID da conexão via variável do Airflow ou usa o padrão
        postgres_conn_id = Variable.get(
            "GOLD_POSTGRES_CONN_ID", default_var="postgres_default"
        )

        # ============================================
        # USANDO POSTGRESHOOK (Boas práticas Airflow)
        # ============================================
        # O hook busca a conexão configurada na UI do Airflow
        # Segura a senha automaticamente (não exposta no código)
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)

        # Usando get_pandas_df - mais limpo e integrado
        # O Hook executa a query e já retorna um DataFrame
        df_count = hook.get_pandas_df(
            "SELECT COUNT(*) as total FROM gold_classificacao"
        )
        count = df_count.iloc[0]["total"]

        logger.info(f"✅ Total de registros na tabela gold_classificacao: {count}")

        # Verificando posições dos times (exemplo de query customizada)
        df_positions = hook.get_pandas_df(
            "SELECT posicao, time, pontos FROM gold_classificacao ORDER BY posicao LIMIT 5"
        )

        logger.info("📊 Top 5 times na classificação:")
        for _, row in df_positions.iterrows():
            logger.info(f"   {row['posicao']}º - {row['time']}: {row['pontos']} pontos")

        return {"rows_verified": int(count), "status": "VERIFIED"}

    # Executar pipeline Gold
    result = run_gold_carga()
    verify = verify_superset_data(result)
