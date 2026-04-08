"""
DAG Gold - Carga Completa Unificada
====================================
Executa todas as cargas Gold em uma única DAG sequencialmente.
Cada carga tem sua própria task com verificação.

Tags: gold, carga, completo, postgresql, superset
"""

from datetime import datetime, timedelta
import logging
import os

from airflow import DAG
from airflow.decorators import task
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
    },
    {
        "nome": "elenco_goleiros",
        "tabela": "gold_elenco_goleiros",
        "pipeline": "src.pipelines.gold.carga_elenco_goleiros",
    },
    {
        "nome": "elenco_jogadores_campo",
        "tabela": "gold_elenco_jogadores_campo",
        "pipeline": "src.pipelines.gold.carga_elenco_jogadores_campo",
    },
    {
        "nome": "classificacao_vagas",
        "tabela": "gold_classificacao_vagas",
        "pipeline": "src.pipelines.gold.carga_classificacao_vagas",
    },
    {
        "nome": "calendario",
        "tabela": "gold_calendario",
        "pipeline": "src.pipelines.gold.calendario_gold",
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

    anterior = None

    for carga in CARGAS:
        nome = carga["nome"]
        tabela = carga["tabela"]
        pipeline = carga["pipeline"]

        @task(task_id=f"run_{nome}", retries=2)
        def run_carga(nome=nome, pipeline=pipeline):
            import sys

            sys.path.insert(0, project_root)

            logger = logging.getLogger(__name__)
            logger.info(f"🔄 Executando carga: {nome}")

            if nome == "calendario":
                from datetime import datetime as dt

                module = __import__(pipeline, fromlist=["run"])
                result = module.run(month=dt.now().month, year=dt.now().year)
            else:
                module = __import__(pipeline, fromlist=["run"])
                result = module.run()

            logger.info(f"✅ {nome}: {result}")
            return {"status": "success", "nome": nome, "result": result}

        @task(task_id=f"verify_{nome}")
        def verify_carga(nome=nome, tabela=tabela):
            hook = PostgresHook(postgres_conn_id=postgres_conn_id)
            df = hook.get_pandas_df(f"SELECT COUNT(*) as total FROM {tabela}")
            total = df.iloc[0]["total"]
            logger.info(f"✅ Verificação {nome}: {total} registros")
            return {"status": "verified", "tabela": tabela, "total": total}

        run_task = run_carga()
        verify_task = verify_carga(run_task)

        if anterior:
            anterior >> run_task
        anterior = verify_task
