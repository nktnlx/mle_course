from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

from weather import fetch_and_write


default_args = {
    'owner': 'anikitin8',
    'start_date': datetime(2025, 2, 1),
    'retries': 1,
}


dag = DAG(
    dag_id='weather_dag',
    description='A pipeline to load weather data and write it to a csv file.',
    schedule_interval=timedelta(minutes=1), 
    default_args=default_args, 
)


fetch_and_write_task = PythonOperator(
    task_id='fetch_and_write',
    python_callable=fetch_and_write,
    dag=dag,
)


fetch_and_write_task
