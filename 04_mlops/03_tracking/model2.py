from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, roc_auc_score
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
    mlflow.log_param('max_depth', model.max_depth)
    mlflow.log_param('max_leaf_nodes', model.max_leaf_nodes)
    mlflow.log_param('criterion', model.criterion)
    
    # Log confusion matrix as heatmap
    cm_df = pd.DataFrame(cm, 
                        index=['Actual Class {}'.format(i) for i in range(len(np.unique(y_test)))],
                        columns=['Predicted Class {}'.format(i) for i in range(len(np.unique(y_test)))])
    plt.figure(figsize=(16,9))
    sns.heatmap(cm_df, annot=True, cmap='Blues')
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.title('Confusion Matrix')
    plt.savefig('confusion_matrix_tree.png')
    mlflow.log_artifact('confusion_matrix_tree.png')
    
    # Log model
    mlflow.sklearn.log_model(model, 'decision_tree_model')

    print(f'Accuracy: {accuracy:.4f}')
    print(f'F1 Score: {f1:.4f}')
    print(f'AUC-ROC: {auc_roc:.4f}')


if __name__ == '__main__':
    mlflow.set_tracking_uri('http://127.0.0.1:8085')
    experiment = mlflow.set_experiment('decision_tree')
    
    with mlflow.start_run():
        decision_tree_model = DecisionTreeClassifier(
            random_state=config['random_state'],
            max_depth=config['decision_tree']['max_depth'],
            max_leaf_nodes=config['decision_tree']['max_leaf_nodes'],
            criterion=config['decision_tree']['criterion']
        )
    
    data = get_data()
    train(decision_tree_model, data['x_train'], data['y_train'])
    test(decision_tree_model, data['x_test'], data['y_test'])
