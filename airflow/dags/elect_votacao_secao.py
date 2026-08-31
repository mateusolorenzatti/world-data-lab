from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

import sys, os
sys.path.append(os.path.join(os.getcwd(), "/opt/airflow/operators"))
from notebook_operator import NotebookOperator


with DAG(
    'ELECT_VotacaoSecao_Pipeline',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["elect", "tse", "pipeline"],
    description="Pipeline Bronze: ingestão de resultados de votação por seção (TSE)"
) as dag:

    bronze_task = NotebookOperator(
        task_id='bronze_ingestion',
        notebook_path='elect/1_brz/brz_elect_votacao_secao.ipynb'
    )
