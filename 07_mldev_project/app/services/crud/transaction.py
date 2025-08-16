from typing import List
from models.transaction import Transaction
from sqlmodel import Session, select


def create_transaction(transaction: Transaction, session: Session) -> Transaction:
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def get_transactions_by_user_id(user_id: int, session: Session) -> List[Transaction]:
    query = select(Transaction).where(Transaction.user_id == user_id)
    result = session.exec(query).all()
    return result


def get_all_transactions(session: Session) -> List[Transaction]:
    query = select(Transaction)
    result = session.exec(query).all()
    return result


def get_transaction_by_transaction_id(transaction_id: str, session: Session) -> List[Transaction]:
    query = select(Transaction).where(Transaction.transaction_id == transaction_id)
    result = session.exec(query).all()
    return result
