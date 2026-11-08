import os
from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

BASE = os.path.expanduser("~/airflow-dbt-lab")
DBT = f"cd {BASE}/dbt_lab && {BASE}/venv-dbt/bin/dbt"

with DAG(
    dag_id="pipeline_dbt",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
):
    ingest = BashOperator(
        task_id="ingest",
        bash_command=f"{BASE}/venv-dbt/bin/python {BASE}/scripts/ingest.py",
    )
    freshness = BashOperator(
        task_id="source_freshness",
        bash_command=f"{DBT} source freshness --profiles-dir .",
    )
    build = BashOperator(
        task_id="dbt_build",
        bash_command=f"{DBT} build --profiles-dir .",
    )

    ingest >> freshness >> build
