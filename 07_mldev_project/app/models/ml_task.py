from models.ml_model import MlModel
from models.transaction import Transaction
from models.user import User
from services.crud.balance import update_balance
from services.crud.transaction import create_transaction
from sqlmodel import Session


class MlTask:
    def __init__(self, user: User, ml_model: MlModel, session: Session):
        self._user = user
        self._ml_model = ml_model
        self._session = session

    def execute(self, data: list, task_id: str) -> str:
        prediction = self._ml_model.predict(data)
        update_balance(
            self._session,
            user=self._user,
            amount=self._ml_model.prediction_cost,
            spend=True,
        )
        create_transaction(
            Transaction(
                user_id=self._user.user_id,
                is_admin=self._user.is_admin,
                transaction_type='prediction',
                transaction_id=task_id,
                amount=self._ml_model.prediction_cost,
                data=data,
                prediction_result=prediction,
            ),
            self._session,
        )
        return f'Chance of survival: {prediction:.2%}'
