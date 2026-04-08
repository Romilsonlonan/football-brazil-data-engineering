"""
DAG - Contexto DDD Classificação (Lógica de Negócio)
=====================================================
Orquestra a lógica de domínio DDD: Use Cases -> Domain Services -> Entities.

Fluxo:
    1. Lê dados da camada Gold
    2. Executa Use Cases (lógica de negócio)
    3. Aplica regras de domínio
    4. Salva resultado no PostgreSQL
    5. Verifica persistência

Tags: ddd, dominio, classificacao, use_cases, negocio
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
    dag_id="ddd_classificacao_use_cases",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 8 * * *",
    catchup=False,
    tags=["ddd", "dominio", "classificacao", "use_cases", "negocio"],
    default_args=default_args,
    description="Orquestra lógica de negócio DDD para classificação",
) as dag:

    @task(
        task_id="run_ddd_classificacao",
        retries=2,
    )
    def run_ddd_classificacao() -> dict:
        import sys
        import os

        project_root = os.environ.get("AIRFLOW_PROJECT_ROOT", "/opt/airflow")
        sys.path.insert(0, project_root)

        import pandas as pd

        from src.contexts.classificacao.application.use_cases import (
            GerarClassificacaoUseCase,
            ConsultarClassificacaoUseCase,
        )

        from src.configs import settings
        from sqlalchemy import create_engine

        engine = create_engine(settings.postgres_url)
        result_df.to_sql(
            "ddd_classificacao_resultado",
            engine,
            schema="public",
            if_exists="replace",
            index=False,
        )

        logger.info("✅ Resultados DDD salvos no PostgreSQL")

        return {
            "status": "success",
            "total_times": len(dtos),
            "posicao_flamengo": posicao,
            "top_4": top4,
        }

    @task(
        task_id="verify_ddd_resultado",
    )
    def verify_ddd_resultado(result: dict) -> dict:
        from airflow.models import Variable

        logger = logging.getLogger(__name__)

        postgres_conn_id = Variable.get(
            "GOLD_POSTGRES_CONN_ID", default_var="postgres_default"
        )

        hook = PostgresHook(postgres_conn_id=postgres_conn_id)

        df_count = hook.get_pandas_df(
            "SELECT COUNT(*) as total FROM ddd_classificacao_resultado"
        )
        count = df_count.iloc[0]["total"]

        logger.info(
            f"✅ Total de registros na tabela ddd_classificacao_resultado: {count}"
        )

        return {"rows_verified": int(count), "status": "VERIFIED"}

    result = run_ddd_classificacao()
    verify = verify_ddd_resultado(result)
