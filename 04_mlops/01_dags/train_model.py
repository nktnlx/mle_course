import joblib

import pandas as pd
from sklearn.linear_model import LogisticRegression


def train(train_csv: str) -> str:
    train_df = pd.read_csv(train_csv)
    X_train = train_df.drop('target', axis=1) 
    y_train = train_df['target']

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    joblib.dump(model, 'model.pkl')

    return 'model.pkl'


# if __name__ == '__main__':
#     train('dataset/iris_train.csv')
