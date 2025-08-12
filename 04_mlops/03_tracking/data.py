from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

from config import config


def load_dataset() -> tuple[list]:
    dataset = load_digits(return_X_y=False)
    X = dataset.data
    y = dataset.target
    return X, y


def split_dataset(X, y) -> dict:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config["data"]["test_size"],
        random_state=config["random_state"],
    )
    data = {
        "x_train": X_train,
        "x_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }
    return data


def get_data() -> dict:
    return split_dataset(*load_dataset())
