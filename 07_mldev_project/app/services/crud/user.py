from typing import List, Optional
from models.balance import Balance
from models.user import User
from sqlmodel import Session, select


def create_user(user: User, session: Session) -> User:
    new_user = User(
        user_name=user.user_name,
        email=user.email,
        password=user.password,
        is_admin=user.is_admin,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    balance = Balance(user_id=new_user.user_id)
    session.add(balance)
    session.commit()
    session.refresh(balance)

    new_user.balance = balance
    return new_user


def get_user_by_id(user_id: int, session: Session) -> Optional[User]:
    query = select(User).where(User.user_id == user_id)
    result = session.exec(query).first()
    return result


def get_user_by_email(email: str, session: Session) -> Optional[User]:
    query = select(User).where(User.email == email)
    result = session.exec(query).first()
    return result


def get_all_users(session: Session) -> List[User]:
    query = select(User)
    result = session.exec(query).all()
    return result
