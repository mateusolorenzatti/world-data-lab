from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='test_dag_simples',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['test']
) as dag:
    
    task = BashOperator(
        task_id='print_date',
        bash_command='date'
    )

print("DAG CARREGADA COM SUCESSO!")
