import os

import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def load_data() -> str:
    iris = load_iris()
    
    df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    df['target'] = iris.target  # Add the target column
    
    os.makedirs('dataset', exist_ok=True)
    
    csv_path = 'dataset/iris.csv'
    df.to_csv(csv_path, index=False)
    
    return csv_path


def prepare_data(csv_path: str) -> list[str]:
    df = pd.read_csv(csv_path)
    
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    train_path = 'dataset/iris_train.csv'
    test_path = 'dataset/iris_test.csv'
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    return [train_path, test_path]


# if __name__ == '__main__':
#     load_data()
#     prepare_data('dataset/iris.csv')
