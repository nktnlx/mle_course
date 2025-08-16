import datetime
from abc import abstractmethod


class Balance:
    def __init__(self, initial_balance: float = 0.0):
        self._amount = initial_balance

    @property
    def balance(self):
        return self._amount

    def add_balance(self, amount: float) -> float:
        if amount > 0:
            self._amount += amount
        return self._amount

    def spend_balance(self, amount: float) -> float:
        if amount <= self._amount:
            self._amount -= amount
        return self._amount


class User:
    def __init__(self, user_id: int, user_name: str, email: str, password: str, balance: Balance = None):
        self._user_id = user_id
        self._user_name = user_name
        self._email = email
        self._password = password
        self._balance = balance if balance else Balance()

    @property
    def user_id(self):
        return self._user_id

    @property
    def user_name(self):
        return self._user_name

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @property
    def balance(self):
        return self._balance.balance

    @abstractmethod
    def is_admin(self) -> bool:
        pass


class RegularUser(User):
    @property
    def is_admin(self) -> bool:
        return False

    def add_balance(self, amount: float) -> float:
        Transaction(self._user_id, self.is_admin, 'add_balance', amount)
        return self._balance.add_balance(amount)


class Admin(User):
    @property
    def is_admin(self) -> bool:
        return True

    def add_balance(self, amount: float, target_user: RegularUser=None) -> float:
        if not target_user:
            Transaction(self._user_id, self.is_admin, 'add_balance', amount)
            return self._balance.add_balance(amount)
        Transaction(self._user_id, self.is_admin, 'add_balance', amount)
        return target_user._balance.add_balance(amount)


class MlModel:
    def __init__(self, model_path: str, prediction_cost: float):
        self._model = self._load_model(model_path)
        self._prediction_cost = prediction_cost
        self._input_features = ['sex', 'age', 'is_alone', 'pclass', 'fare']

    @property
    def prediction_cost(self):
        return self._prediction_cost

    @property
    def input_features(self):
        return self._input_features

    def _load_model(self, model_path: str):
        from catboost import CatBoostClassifier
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(model_path)
        return loaded_model

    def predict(self, data: list) -> float:
        result = self._model.predict_proba(data)
        probability_to_survive = result[1:][0]
        return probability_to_survive


class MlTask:
    def __init__(self, user: User, ml_model: MlModel):
        self._user = user
        self._ml_model = ml_model

    def execute(self, data: list) -> float:
        if self._user.balance < self._ml_model.prediction_cost:
            print('Insufficient balance to perform prediction')
        prediction = self._ml_model.predict(data)
        self._user._balance.spend_balance(self._ml_model.prediction_cost)
        Transaction(self._user._user_id, self._user.is_admin, 'prediction',
                    -self._ml_model.prediction_cost, data, prediction)
        return prediction


class Transaction:
    transaction_history = []
    transactions_id_counter = 0

    @staticmethod
    def generate_transaction_id():
        Transaction.transactions_id_counter += 1
        return Transaction.transactions_id_counter

    def __init__(self, user_id: int, is_admin: bool, transaction_type: str,
                 amount: float, data: list = None, prediction_result: float = None):
        self._transaction_id = Transaction.generate_transaction_id()
        self._user_id = user_id
        self._is_admin = is_admin
        self._transaction_type = transaction_type
        self._amount = amount
        self._data = data
        self._prediction_result = prediction_result
        self._timestamp = datetime.datetime.now()
        Transaction.transaction_history.append(self)

    def __str__(self):
        return (f'Transaction ID: {self._transaction_id}, '
                f'User ID: {self._user_id}, '
                f'Is Admin: {self._is_admin}, '
                f'Type: {self._transaction_type}, '
                f'Amount: {self._amount}, '
                f'Data: {self._data}, '
                f'Prediction Result: {self._prediction_result}, '
                f'Timestamp: {self._timestamp}')

    @classmethod
    def get_transaction_history(cls):
        return cls.transaction_history


if __name__ == '__main__':
    # creating users
    user1 = Admin(9999, 'alex', 'alex@mail.ru', 'qwerty')
    user2 = RegularUser(8888, 'kate', 'kate@mail.ru', 'ytrewq')

    # adding balance to users
    user1.add_balance(100)
    user2.add_balance(10)
    user1.add_balance(5, user2)

    # initializing ML model and making predictions
    model = MlModel('app/catboost_model.cbm', 5.55)
    MlTask(user1, model).execute(['male', 36, '1', '1', 79.99])
    MlTask(user2, model).execute(['female', 26, '0', '3', 15.99])

    # showing transactions history
    history = Transaction.get_transaction_history()
    for transaction in history:
        print(transaction)

    # printing users remaining balance
    print(f'User: {user1.user_name} has {user1.balance} credits remaining.')
    print(f'User: {user2.user_name} has {user2.balance} credits remaining.')
