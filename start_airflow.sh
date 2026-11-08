#!/bin/bash
cd ~/airflow-dbt-lab
source venv-airflow/bin/activate
export AIRFLOW_HOME=~/airflow-dbt-lab/airflow_home
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow standalone
