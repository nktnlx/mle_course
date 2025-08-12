import json
from datetime import datetime

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def load_data():
    data = pd.read_csv(
        '/Users/nikitin_a/PycharmProjects/mlops_wine_project/data/winequality-red.csv'
    )
    print(f'Downloaded dataframe of the following shape: {data.shape}')
    return data


def train_model(data):
    import clearml
    import joblib
    from config import config
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import GridSearchCV, train_test_split
    from sklearn.preprocessing import StandardScaler

    # splitting data
    X = data.drop('quality', axis=1)
    y = data['quality']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config['data']['test_size'], random_state=config['random_state']
    )

    # scaling data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # hyperparameters for Random Forest Regressor
    rf_params = config['rf_params']

    # starting clearml
    task = clearml.Task.init(
        project_name='wine-quality-prediction', task_name='random-forest-model-prod'
    )
    logger = task.get_logger()

    # logging hyperparameters
    task.connect(rf_params, name='Random Forest Regressor Parameters')

    # training Random Forest Regressor Model
    rf_grid = GridSearchCV(
        RandomForestRegressor(), rf_params, cv=5, scoring='neg_mean_squared_error'
    )
    rf_grid.fit(X_train_scaled, y_train)

    # best RF parameters and model
    best_rf_params = rf_grid.best_params_
    best_rf_model = rf_grid.best_estimator_

    # predicting and evaluating RF
    y_pred_rf = best_rf_model.predict(X_test_scaled)
    mse_rf = mean_squared_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)
    mae_rf = mean_absolute_error(y_test, y_pred_rf)

    # logging RF metrics and best parameters
    task.connect(best_rf_params, name='Best Random Forest Regressor Parameters')
    logger.report_scalar(title='MSE', series='Random Forest', value=mse_rf, iteration=0)
    logger.report_scalar(
        title='R^2 Score', series='Random Forest', value=r2_rf, iteration=0
    )
    logger.report_scalar(title='MAE', series='Random Forest', value=mae_rf, iteration=0)

    print(f'Best Random Forest model MSE: {mse_rf:.4f}')
    print(f'Best Random Forest model R^2 score: {r2_rf:.4f}')
    print(f'Best Random Forest model MAE: {mae_rf:.4f}')

    # closing clearml task
    task.close()

    # dumping model
    model_path = (
        '/Users/nikitin_a/PycharmProjects/mlops_wine_project/models/rf_model.pkl'
    )
    joblib.dump(best_rf_model, model_path)
    print(f'Trained model dumped to: {model_path}')

    # dumping metadata
    metadata = {
        'model': 'RandomForestRegressor',
        'metrics': {'mse': mse_rf, 'r2_score': r2_rf, 'mae': mae_rf},
        'parameters': best_rf_params,
    }
    metadata_path = '/Users/nikitin_a/PycharmProjects/mlops_wine_project/models/rf_model_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    print(f'Trained model metadata dumped to: {metadata_path}')

    return model_path


def save_model(model_path):
    import os

    path_name = model_path[0:58]
    model_name = model_path[59:]

    os.system(f'cd {path_name} && dvc add {model_name} && dvc push')
    print('Model added to dvc.')

    os.system(f'cd {path_name} && dvc push')
    print('Model pushed to dvc.')

    return True


default_args = {
    'owner': 'anikitin8',
    'start_date': datetime(2025, 2, 1),
    'retries': 1,
}

dag = DAG(
    'load_train_save',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
)

dvc_pull_task = BashOperator(
    task_id='dvc_pull_data',
    bash_command='cd /Users/nikitin_a/PycharmProjects/mlops_wine_project/data && dvc pull',
    dag=dag,
)

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    op_kwargs={'data': load_data_task.output},
    dag=dag,
)

save_model_task = PythonOperator(
    task_id='save_model',
    python_callable=save_model,
    op_kwargs={'model_path': train_model_task.output},
    dag=dag,
)


dvc_pull_task >> load_data_task >> train_model_task >> save_model_task
