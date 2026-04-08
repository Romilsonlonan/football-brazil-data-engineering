"""
DAG Gold - Carga de Elenco Goleiros para PostgreSQL/Superset
=============================================================
Pipeline de carga dos dados de elenco goleiros para PostgreSQL do Superset.

Tags: gold, carga, postgresql, superset, goleiros, elenco
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
    dag_id="gold_elenco_goleiros_carga",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 7 * * *",
    catchup=False,
    tags=["gold", "carga", "postgresql", "superset", "goleiros", "elenco"],
    default_args=default_args,
    description="Pipeline de carga dos dados de goleiros para PostgreSQL/Superset",
) as dag:

    @task(
        task_id="run_gold_carga_goleiros",
        retries=2,
    )
    def run_gold_carga_goleiros() -> dict:
        import sys
        import os

        project_root = os.environ.get("AIRFLOW_PROJECT_ROOT", "/opt/airflow")
        sys.path.insert(0, project_root)

        from src.pipelines.gold.carga_elenco_goleiros import run

        logger = logging.getLogger(__name__)
        logger.info("Iniciando pipeline Gold de carga de goleiros...")

        result = run()

        logger.info(f"✅ Pipeline Gold goleiros concluido: {result}")

        return result

    @task(
        task_id="verify_superset_data_goleiros",
    )
    def verify_superset_data_goleiros(result: dict) -> dict:
        from airflow.models import Variable

        logger = logging.getLogger(__name__)

        postgres_conn_id = Variable.get(
            "GOLD_POSTGRES_CONN_ID", default_var="postgres_default"
        )

        hook = PostgresHook(postgres_conn_id=postgres_conn_id)

        df_count = hook.get_pandas_df(
            "SELECT COUNT(*) as total FROM gold_elenco_goleiros"
        )
        count = df_count.iloc[0]["total"]

        logger.info(f"✅ Total de registros na tabela gold_elenco_goleiros: {count}")

        return {"rows_verified": int(count), "status": "VERIFIED"}

    result = run_gold_carga_goleiros()
    verify = verify_superset_data_goleiros(result)
