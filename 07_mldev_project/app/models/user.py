from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = 'user'

    user_id: int = Field(unique=True, primary_key=True)
    user_name: str
    email: str = Field(unique=True)
    password: str
    is_admin: bool = Field(default=False)
    balance: Optional['Balance'] = Relationship(back_populates='user')
    # transaction: List['Transaction'] = Relationship(back_populates='user')

    @property
    def balance_amount(self) -> float:
        return self.balance.amount if self.balance else 0.0

    def __str__(self) -> str:
        return (
            f'user_id: {self.user_id}, user_name: {self.user_name}, email: {self.email}, admin: {self.is_admin}, '
            f'balance: {self.balance_amount}'
        )  # , transaction: {self.transaction}')
