from airflow import DAG
# from airflow.providers.standard.operators.bash import BashOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

def fun_teste():
    print('Teste da DAG')

with DAG(
    'GENDT_Automobile_Pipeline',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["gendt", "automobile", "pipeline"],
    description="Pipeline completo: Bronze → Silver → Gold"
) as dag:
    
    bronze_task = BashOperator(
        task_id='bronze_ingestion',
        bash_command="""
        jupyter nbconvert --to notebook --execute \
        --output /opt/airflow/logs/bronze_automobile_{{ds}}.ipynb \
        /opt/airflow/notebooks/src/gendt/1_brz/brz_automobile.ipynb
        """
    )
    
    silver_task = BashOperator(
        task_id='silver_transformation',
        bash_command="""
        jupyter nbconvert --to notebook --execute \
        --output /opt/airflow/logs/silver_automobile_{{ds}}.ipynb \
        /opt/airflow/notebooks/src/gendt/2_slv/slv_automobile.ipynb
        """
    )
    
    gold_task_brand = BashOperator(
        task_id='gold_aggregation_brand',
        bash_command="""
        jupyter nbconvert --to notebook --execute \
        --output /opt/airflow/logs/gold_automobile_{{ds}}.ipynb \
        /opt/airflow/notebooks/src/gendt/3_gld/gld_automobile_by_brand.ipynb
        """
    )
    
    gold_task_country = BashOperator(
        task_id='gold_aggregation_country',
        bash_command="""
        jupyter nbconvert --to notebook --execute \
        --output /opt/airflow/logs/gold_automobile_{{ds}}.ipynb \
        /opt/airflow/notebooks/src/gendt/3_gld/gld_automobile_by_country.ipynb
        """
    )
    
    bronze_task >> silver_task >> [gold_task_brand, gold_task_country]