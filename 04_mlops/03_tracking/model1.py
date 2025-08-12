from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import label_binarize

import mlflow
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import config
from data import get_data


def train(model, x_train, y_train) -> None:
    model.fit(x_train, y_train)


def test(model, x_test, y_test) -> None:
    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    cm = confusion_matrix(y_test, y_pred)
    y_test_binarized = label_binarize(y_test, classes=np.unique(y_test))
    auc_roc = roc_auc_score(y_test_binarized, y_proba, average='weighted')
    
    # Log metrics 
    mlflow.log_metric('accuracy', accuracy)
    mlflow.log_metric('f1_score', f1)
    mlflow.log_metric('auc_roc', auc_roc)

    # Lof parameters
    mlflow.log_param('regularization', model.penalty)
    mlflow.log_param('max_iter', model.max_iter)
    mlflow.log_param('multi_class', model.multi_class)
    
    # Log confusion matrix as heatmap
    cm_df = pd.DataFrame(cm, 
                        index=['Actual Class {}'.format(i) for i in range(len(np.unique(y_test)))],
                        columns=['Predicted Class {}'.format(i) for i in range(len(np.unique(y_test)))])
    plt.figure(figsize=(16,9))
    sns.heatmap(cm_df, annot=True, cmap='Blues')
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.title('Confusion Matrix')
    plt.savefig('confusion_matrix.png')
    mlflow.log_artifact('confusion_matrix.png')

    # Log coefficients and intercept
    coefficients = pd.DataFrame({
        'Feature': [f'Feature_{i}' for i in range(len(model.coef_[0]))],
        'Coefficient': model.coef_[0]
    })
    coefficients = coefficients._append(
        {'Feature': 'Intercept', 'Coefficient': model.intercept_[0]}, 
        ignore_index=True
    )
    coefficients.to_csv('coefficients.csv', index=False)
    mlflow.log_artifact('coefficients.csv')

    # Log model
    mlflow.sklearn.log_model(model, 'logistic_regression_model')
    
    print(f'Accuracy: {accuracy:.4f}')
    print(f'F1 Score: {f1:.4f}')
    print(f'AUC-ROC: {auc_roc:.4f}')


if __name__ == '__main__':
    mlflow.set_tracking_uri('http://127.0.0.1:8085')
    experiment = mlflow.set_experiment('logistic_regression')
    
    with mlflow.start_run():
        logistic_regression_model = LogisticRegression(
            max_iter=config['logistic_regression']['max_iter'],
            penalty=config['logistic_regression']['penalty'],
            multi_class=config['logistic_regression']['multi_class']
        )
    
    data = get_data()
    train(logistic_regression_model, data['x_train'], data['y_train'])
    test(logistic_regression_model, data['x_test'], data['y_test'])
