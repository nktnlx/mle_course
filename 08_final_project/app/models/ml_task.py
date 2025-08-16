from models.ml_model import MlModel
from models.transaction import Transaction
from models.user import User
from services.crud.transaction import create_transaction
from sqlmodel import Session


class MlTask:
    def __init__(self, user: User, ml_model: MlModel, session: Session):
        self._user = user
        self._ml_model = ml_model
        self._session = session

    def execute(self, data: list, task_id: str) -> str:
        prediction = self._ml_model.predict(data)
        create_transaction(
            Transaction(
                user_id=self._user.user_id,
                transaction_id=task_id,
                data=data,
                prediction_result=prediction,
            ),
            self._session,
        )
        return f'Chance of cardiovascular disease: {prediction:.2%}'
