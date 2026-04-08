"""
DAG Gold - Calendário de Jogos para PostgreSQL/Superset
=======================================================
Pipeline de carga dos dados de calendário para PostgreSQL do Superset.

Tags: gold, carga, postgresql, superset, calendario
"""

from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook


default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="gold_calendario_carga",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 7 * * *",
    catchup=False,
    tags=["gold", "carga", "postgresql", "superset", "calendario"],
    default_args=default_args,
    description="Pipeline de carga dos dados de calendário para PostgreSQL/Superset",
) as dag:

    @task(
        task_id="run_gold_carga_calendario",
        retries=2,
    )
    def run_gold_carga_calendario() -> dict:
        import sys
        import os

        project_root = os.environ.get("AIRFLOW_PROJECT_ROOT", "/opt/airflow")
        sys.path.insert(0, project_root)

        from src.pipelines.gold.calendario_gold import run as run_calendario

        logger = logging.getLogger(__name__)
        logger.info("Iniciando pipeline Gold de carga de calendário...")

        from datetime import datetime as dt

        current_month = dt.now().month
        current_year = dt.now().year

        result = run_calendario(month=current_month, year=current_year)

        logger.info(f"✅ Pipeline Gold calendário concluído: {result}")

        return result

    @task(
        task_id="verify_superset_data_calendario",
    )
    def verify_superset_data_calendario(result: dict) -> dict:
        from airflow.models import Variable

        logger = logging.getLogger(__name__)

        postgres_conn_id = Variable.get(
            "GOLD_POSTGRES_CONN_ID", default_var="postgres_default"
        )

        hook = PostgresHook(postgres_conn_id=postgres_conn_id)

        df_count = hook.get_pandas_df("SELECT COUNT(*) as total FROM gold_calendario")
        count = df_count.iloc[0]["total"]

        logger.info(f"✅ Total de registros na tabela gold_calendario: {count}")

        return {"rows_verified": int(count), "status": "VERIFIED"}

    result = run_gold_carga_calendario()
    verify = verify_superset_data_calendario(result)
