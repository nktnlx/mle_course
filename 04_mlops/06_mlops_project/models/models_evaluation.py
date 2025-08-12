import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import clearml


# loading dataset
data = pd.read_csv('/Users/nikitin_a/PycharmProjects/mlops_wine_project/data/winequality-red.csv')
X = data.drop('quality', axis=1)
y = data['quality']

# splitting data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# scaling data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# hyperparameters for Linear Regression
lr_params = {
    'fit_intercept': [True, False],
    'positive': [True, False]
}

# hyperparameters for Random Forest Regressor
rf_params = {
    'n_estimators': [100, 200, 500],
    'criterion': ['squared_error'],
    'max_depth': [None, 10],
    'min_samples_split': [2, 5],
    'max_features': [1, 'sqrt'],
    'random_state': [42],
}

# starting clearml
task = clearml.Task.init(project_name='wine-quality-prediction', task_name='best-model-experiment')
logger = task.get_logger()

# logging hyperparameters
task.connect(lr_params, name='Linear Regression Parameters')
task.connect(rf_params, name='Random Forest Regressor Parameters')

# training Linear Regression model
lr_grid = GridSearchCV(LinearRegression(), lr_params, cv=5, scoring='neg_mean_squared_error')
lr_grid.fit(X_train_scaled, y_train)

# best LR parameters and model
best_lr_params = lr_grid.best_params_
best_lr_model = lr_grid.best_estimator_

# predicting and evaluating LR
y_pred_lr = best_lr_model.predict(X_test_scaled)
mse_lr = mean_squared_error(y_test, y_pred_lr)
r2_lr = r2_score(y_test, y_pred_lr)
mae_lr = mean_absolute_error(y_test, y_pred_lr)

# logging LR metrics and best parameters
task.connect(best_lr_params, name='Best Linear Regression Parameters')
logger.report_scalar(title='MSE', series='Linear Regression', value=mse_lr, iteration=0)
logger.report_scalar(title='R^2 Score', series='Linear Regression', value=r2_lr, iteration=0)
logger.report_scalar(title='MAE', series='Linear Regression', value=mae_lr, iteration=0)

print(f'Best Linear model MSE: {mse_lr:.4f}')
print(f'Best Linear model R^2 score: {r2_lr:.4f}')
print(f'Best Linear model MAE: {mae_lr:.4f}')

# training Random Forest Regressor Model
rf_grid = GridSearchCV(RandomForestRegressor(), rf_params, cv=5, scoring='neg_mean_squared_error')
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
logger.report_scalar(title='R^2 Score', series='Random Forest', value=r2_rf, iteration=0)
logger.report_scalar(title='MAE', series='Random Forest', value=mae_rf, iteration=0)

print(f'Best Random Forest model MSE: {mse_rf:.4f}')
print(f'Best Random Forest model R^2 score: {r2_rf:.4f}')
print(f'Best Random Forest model MAE: {mae_rf:.4f}')

# closing clearml task
task.close()
