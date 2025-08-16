import datetime
from typing import Any, List, Optional
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class Transaction(SQLModel, table=True):
    __tablename__ = 'transaction'

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key='user.user_id')
    # user: Optional['User'] = Relationship(back_populates='transaction')
    is_admin: bool
    transaction_type: str
    transaction_id: Optional[str] = Field(default=None)
    amount: float
    data: List[Any] = Field(default=None, sa_column=Column(JSON))
    prediction_result: Optional[float] = Field(default=None)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return (
            f'ID: {self.id}, '
            f'User ID: {self.user_id}, '
            f'Is Admin: {self.is_admin}, '
            f'Type: {self.transaction_type}, '
            f'Transaction ID: {self.transaction_id}, '
            f'Amount: {self.amount}, '
            f'Data: {self.data}, '
            f'Prediction Result: {self.prediction_result}, '
            f'Timestamp: {self.timestamp}'
        )
