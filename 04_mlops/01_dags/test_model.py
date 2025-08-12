import joblib
import json

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report


def test(model_path: str, test_csv: str) -> str:
    model = joblib.load(model_path)

    test_df = pd.read_csv(test_csv)
    X_test = test_df.drop('target', axis=1)
    y_test = test_df['target']

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    metrics = {'accuracy': accuracy, 'report': report}
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics, f)

    return metrics


# if __name__ == '__main__':
#     test('model.pkl', 'dataset/iris_test.csv')
