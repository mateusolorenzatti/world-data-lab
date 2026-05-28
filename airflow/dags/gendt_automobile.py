from airflow import DAG
# from airflow.providers.standard.operators.bash import BashOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

import sys, os
sys.path.append(os.path.join(os.getcwd(), "/opt/airflow/operators"))
from notebook_operator import NotebookOperator


with DAG(
    'GENDT_Automobile_Pipeline',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["gendt", "automobile", "pipeline"],
    description="Pipeline completo: Bronze → Silver → Gold"
) as dag:
    
    bronze_task = NotebookOperator(
        task_id='bronze_ingestion',
        notebook_path='gendt/1_brz/brz_automobile.ipynb' 
    )
    
    silver_task = NotebookOperator(
        task_id='silver_transformation',
        notebook_path='gendt/2_svr/svr_automobile.ipynb' 
    )
    
    gold_task_brand = NotebookOperator(
        task_id='gold_aggregation_brand',
        notebook_path='gendt/3_gld/gld_automobile_by_brand.ipynb' 
    )
    
    gold_task_country = NotebookOperator(
        task_id='gold_aggregation_country',
        notebook_path='gendt/3_gld/gld_automobile_by_country.ipynb' 
    )
    
    bronze_task >> silver_task >> [gold_task_brand, gold_task_country]