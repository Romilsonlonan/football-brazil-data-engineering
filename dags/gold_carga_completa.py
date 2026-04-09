"""
DAG Gold - Carga Completa Unificada
====================================
Executa todas as cargas Gold em uma única DAG com TaskGroups para organização visual.
Cada carga tem sua própria task, permitindo visualização granular no Airflow.

Tags: gold, carga, completo, postgresql, superset
"""

from datetime import datetime, timedelta
import logging
import os

from airflow import DAG
from airflow.decorators import task
from airflow.models import TaskGroup
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable


default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

logger = logging.getLogger(__name__)

CARGAS = [
    {
        "nome": "classificacao",
        "tabela": "gold_classificacao",
        "pipeline": "src.pipelines.gold.carga_classificacao",
        "funcao": "run",
    },
    {
        "nome": "elenco_goleiros",
        "tabela": "gold_elenco_goleiros",
        "pipeline": "src.pipelines.gold.carga_elenco_goleiros",
        "funcao": "run",
    },
    {
        "nome": "elenco_jogadores_campo",
        "tabela": "gold_elenco_jogadores_campo",
        "pipeline": "src.pipelines.gold.carga_elenco_jogadores_campo",
        "funcao": "run",
    },
    {
        "nome": "classificacao_vagas",
        "tabela": "gold_classificacao_vagas",
        "pipeline": "src.pipelines.gold.carga_classificacao_vagas",
        "funcao": "run",
    },
    {
        "nome": "calendario",
        "tabela": "gold_calendario",
        "pipeline": "src.pipelines.gold.calendario_gold",
        "funcao": "run",
        "kwargs": {"month": "current_month", "year": "current_year"},
    },
    {
        "nome": "ddd_classificacao",
        "tabela": "ddd_classificacao_resultado",
        "pipeline": "src.contexts.classificacao.application.use_cases",
        "funcao": "ddd_run",
    },
]


def get_project_root():
    return os.environ.get("AIRFLOW_PROJECT_ROOT", "/opt/airflow")


with DAG(
    dag_id="gold_carga_completa",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 7 * * *",
    catchup=False,
    tags=["gold", "carga", "completo", "postgresql", "superset"],
    default_args=default_args,
    description="Pipeline completo de carga Gold - todas as tabelas",
) as dag:
    project_root = get_project_root()

    postgres_conn_id = Variable.get(
        "GOLD_POSTGRES_CONN_ID", default_var="postgres_default"
    )

    tasks_anteriores = None
    task_groups = []

    for carga in CARGAS:
        nome = carga["nome"]
        tabela = carga["tabela"]
        pipeline = carga["pipeline"]
        funcao = carga.get("funcao", "run")
        kwargs = carga.get("kwargs", {})

        with TaskGroup(f"{nome}_group"):

            @task(task_id=f"run_{nome}", retries=2)
            def run_carga(nome=nome, pipeline=pipeline, funcao=funcao, kwargs=kwargs):
                import sys

                sys.path.insert(0, project_root)

                logger = logging.getLogger(__name__)
                logger.info(f"🔄 Executando carga: {nome}")

                try:
                    if kwargs:
                        from datetime import datetime as dt

                        if "current_month" in kwargs.values():
                            kwargs = {"month": dt.now().month, "year": dt.now().year}
                        module = __import__(pipeline, fromlist=[funcao])
                        result = getattr(module, funcao)(**kwargs)
                    elif nome == "ddd_classificacao":
                        import pandas as pd
                        from src.contexts.classificacao.application.use_cases import (
                            GerarClassificacaoUseCase,
                        )

                        gold_path = f"{project_root}/data/gold/classificacao.parquet"
                        df = pd.read_parquet(gold_path)
                        gerar_uc = GerarClassificacaoUseCase()
                        dtos = gerar_uc.execute(df)
                        result = {"status": "success", "total": len(dtos)}
                    else:
                        module = __import__(pipeline, fromlist=[funcao])
                        result = getattr(module, funcao)()

                    logger.info(f"✅ {nome}: {result}")
                    return {"status": "success", "nome": nome, "result": result}
                except Exception as e:
                    logger.error(f"❌ Erro na carga {nome}: {str(e)}")
                    raise

            @task(task_id=f"verify_{nome}")
            def verify_carga(result, tabela=tabela, nome=nome):
                hook = PostgresHook(postgres_conn_id=postgres_conn_id)
                df = hook.get_pandas_df(f"SELECT COUNT(*) as total FROM {tabela}")
                total = df.iloc[0]["total"]
                logger.info(f"✅ Verificação {nome}: {total} registros")
                return {"status": "verified", "tabela": tabela, "total": total}

            task_run = run_carga()
            task_verify = verify_carga(task_run)
            task_groups.append(f"{nome}_group")

            if tasks_anteriores:
                tasks_anteriores >> task_run
            tasks_anteriores = task_verify

    logger.info(f"✅ DAG configurada com {len(CARGAS)} grupos de tarefas")
