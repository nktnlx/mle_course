# mlops_wine_project

## General Description

This project aims to develop a machine learning service for predicting wine quality.  
The project includes data loading, model training, model evaluation, and API deployment using `FastAPI`.  
It uses `Airflow` for orchestrating model training, `DVC` for data version control and `ClearML` for tracking model retraining experiments.  

## Project Structure

```
mlops_wine_project/
├── dags/  
│   ├── config.py                # config with model training parameters  
│   └── dag.py                   # DAG for training and saving a new model version  
├── data/                   
│   └── winequality-red.csv.dvc  # a link to the Red Wine Quality dataset in DVC  
├── models/  
│   ├── models_evaluation.py     # tracking experiments in ClearML to select the best model   
│   ├── rf_model.pkl.dvc         # a link to the trained Random Forest Regressor model in DVC   
│   └── rf_model_metadata.json   # metadata of the trained model  
├── src/  
│   └── api/
│       └── app.py               # API application created with FastAPI  
├── tests/                  
│   └── test_api.py              # tests for the project's API endpoints  
├── .gitignore                   # Git ignore template  
├── .gitlab-ci.yml               # GitLab CI configuration file  
├── requirements.txt             # list of Python libraries required to run the project  
└── README.md                    # project description  
```

## Model selection experiment

### Problem statement

Our task is to determine wine quality (the `quality` attribute).
To solve it, two models were chosen:
- linear regression (`LinearRegression`)
- random forest (`RandomForestRegressor`).

For each model, a hyperparameter search was performed using `GridSearchCV`.  

### Linear regression model

Hyperparameter grid for Linear Regression:
```
lr_params = {
    'fit_intercept': [True, False],
    'positive': [True, False]
}
```
As a result, the best parameters for Linear Regression:
```
{'fit_intercept': True,
 'positive': False}
```
Quality metrics of the best Linear Regression model:
```
Best Linear model MSE: 0.3900
Best Linear model R^2 score: 0.4032
Best Linear model MAE: 0.5035
```

### Random forest model
Hyperparameter grid for Random Forest Regressor:
```
rf_params = {
    'n_estimators': [100, 200, 500],
    'criterion': ['squared_error'],
    'max_depth': [None, 10],
    'min_samples_split': [2, 5],
    'max_features': [1, 'sqrt'],
    'random_state': [42],
}
```
As a result, the best parameters for Random Forest Regressor:
```
{'criterion': 'squared_error',
 'max_depth': None,
 'max_features': 'sqrt',
 'min_samples_split': 2, 
 'n_estimators': 500,
 'random_state': 42}
```
Quality metrics of the best Linear Regression model:
```
Best Random Forest model MSE: 0.2925
Best Random Forest model R^2 score: 0.5525
Best Random Forest model MAE: 0.4144
```

### Comparison of the results of the two models

```markdown
| Metric     | Linear Model | Random Forest Model |
|------------|--------------|---------------------|
| MSE        | 0.3900       | 0.2925              |
| R^2 Score  | 0.4032       | 0.5525              |
| MAE        | 0.5035       | 0.4144              |
```

Across all of the considered model quality metrics, we see an advantage for the Random Forest Model.
We will continue to use it in our project.

### ClearML report

A more detailed report on training and selecting the best model can be found here:
[ClearML report](https://app.clear.ml/projects/be12ead5a0644d1da2cc0f90822453fa/experiments/786048c75e234b1db9c7c629cce174ee/output/execution)

The report on the latest regular run and training of the best model via Airflow can be found here:
[ClearML report](https://app.clear.ml/projects/be12ead5a0644d1da2cc0f90822453fa/experiments/14857092d92540839619e2ba235f3a52/output/execution)

---

## Working with the project

1. Clone the repository
2. Using `pip`, install the libraries from `requirements.txt`  
3. Initialize and configure `DVC`
4. Initialize and configure `Airflow`
5. Run the `dag.py` jobs via `Airflow`
6. The model and its metadata resulting from training will now be updated once a day
7. Start the `API` and use the `/predict` endpoint to get predictions of red wine quality.

## Conclusion

This project demonstrates a complete pipeline for the development, training, deployment, and testing of a machine learning model using `Python`, `Airflow`, `DVC`, `ClearML` and `FastAPI`. Thus, we have a solid foundation for deploying and using machine learning services.  
