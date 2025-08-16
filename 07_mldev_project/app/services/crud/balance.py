import uuid
from typing import List, Optional
from models.balance import Balance
from models.transaction import Transaction
from models.user import User
from services.crud.transaction import create_transaction
from sqlmodel import Session, select


def get_balance_by_user_id(user_id: int, session: Session) -> Optional[Balance]:
    query = select(Balance).where(Balance.user_id == user_id)
    result = session.exec(query).first()
    return result


def get_all_balance(session: Session) -> List[Balance]:
    query = select(Balance)
    result = session.exec(query).all()
    return result


def update_balance(
    session: Session,
    user: User,
    amount: float,
    spend: bool = False,
    target_user_id: Optional[int] = None,
) -> Balance:
    task_id = str(uuid.uuid4())
    if spend:
        balance = get_balance_by_user_id(user.user_id, session)
        balance.spend_balance(amount)
    else:
        if user.is_admin and target_user_id is not None:
            # Admin adding balance to another user's account
            target_balance = get_balance_by_user_id(target_user_id, session)
            target_balance.add_balance(amount)
            create_transaction(
                Transaction(
                    user_id=user.user_id,
                    is_admin=user.is_admin,
                    transaction_type='add_balance',
                    transaction_id=task_id,
                    amount=amount,
                ),
                session,
            )
            session.add(target_balance)
            session.commit()
            session.refresh(target_balance)
            return target_balance
        elif user.is_admin == False and target_user_id is not None:
            # not admin user trying to add balance to another account
            balance = get_balance_by_user_id(user.user_id, session)
            return balance
        else:
            # Regular user or admin adding balance to their own account
            balance = get_balance_by_user_id(user.user_id, session)
            balance.add_balance(amount)
            create_transaction(
                Transaction(
                    user_id=user.user_id,
                    is_admin=user.is_admin,
                    transaction_type='add_balance',
                    transaction_id=task_id,
                    amount=amount,
                ),
                session,
            )
        session.add(balance)
        session.commit()
        session.refresh(balance)
        return balance
