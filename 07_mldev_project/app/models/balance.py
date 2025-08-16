from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class Balance(SQLModel, table=True):
    __tablename__ = 'balance'

    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float = Field(default=0.0)
    user_id: Optional[int] = Field(default=None, foreign_key='user.user_id')
    user: Optional['User'] = Relationship(back_populates='balance')

    def add_balance(self, amount: float) -> float:
        if amount > 0:
            self.amount += amount
        return self.amount

    def spend_balance(self, amount: float) -> float:
        if amount <= self.amount:
            self.amount -= amount
        return self.amount

    def __str__(self) -> str:
        return f'id: {self.id}, user_id: {self.user_id}, balance: {self.amount}'
