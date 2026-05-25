from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import papermill as pm

def execute_notebook(**context):
    pm.execute_notebook(
        input_path='/opt/airflow/notebooks/src/gendt/1_brz/brz_automobile.ipynb',
        output_path='/opt/airflow/notebooks/src/gendt/1_brz/brz_automobile_executed.ipynb',
    )

with DAG(
    '[GENDT] Automobile',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    pass

    '''
    run_notebook = PythonOperator(
        task_id='execute_notebook',
        python_callable=execute_notebook,
        provide_context=True
    )
    '''