from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

from data import load_data, prepare_data
from train_model import train
from test_model import test


default_args = {
    'owner': 'anikitin8',
    'start_date': datetime(2025, 2, 1),
    'retries': 1,
}


dag = DAG(
    dag_id='iris_model_pipeline',
    description='A pipeline to load, prepare, train, and test the Iris dataset',
    schedule='@daily', 
    default_args=default_args, 
)


load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)


prepare_data_task = PythonOperator(
    task_id='prepare_data',
    python_callable=prepare_data,
    op_kwargs={'csv_path': 'dataset/iris.csv'},
    dag=dag,
)


train_task = PythonOperator(
    task_id='train_model',
    python_callable=train,
    op_kwargs={'train_csv': 'dataset/iris_train.csv'}, 
    dag=dag,
)


test_task = PythonOperator(
    task_id='test_model',
    python_callable=test,
    op_kwargs={
        'model_path': 'model.pkl',
        'test_csv': 'dataset/iris_test.csv',
    },
    dag=dag,
)


load_data_task >> prepare_data_task >> train_task >> test_task
