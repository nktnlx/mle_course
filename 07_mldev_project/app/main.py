from models.ml_model import MlModel
from models.ml_task import MlTask
from models.user import User
from services.crud.balance import (
    get_all_balance,
    get_balance_by_user_id,
    update_balance,
)
from services.crud.transaction import get_all_transactions
from services.crud.user import (
    create_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
)
from sqlmodel import Session, SQLModel, create_engine, select


if __name__ == "__main__":
    # Create an SQLite database engine
    engine = create_engine('sqlite:///database.db')

    # Create the table
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)

    # Create a session
    session = Session(engine)

    # Add a regular user
    regular_user = create_user(
        User(
            user_id=8888,
            user_name='kate',
            email='kate@mail.ru',
            password='ytrewq'),
        session,
    )

    # Add an admin user
    admin_user = create_user(
        User(
            user_id=9999,
            user_name='alex',
            email='alex@mail.ru',
            password='qwerty',
            is_admin=True,
        ),
        session,
    )

    # Adding and spending balance
    update_balance(session, user=regular_user, amount=11, spend=False)
    update_balance(
        session,
        user=regular_user,
        amount=4,
        spend=False,
        target_user_id=regular_user.user_id,
    )
    update_balance(
        session, user=regular_user, amount=4, spend=False, target_user_id=admin_user.user_id
    )
    update_balance(session, user=admin_user, amount=110, spend=False)
    update_balance(
        session, user=admin_user, amount=9, spend=False, target_user_id=regular_user.user_id
    )
    update_balance(
        session, user=admin_user, amount=100, spend=False, target_user_id=admin_user.user_id
    )

    # getting users by id, by email & getting balance by user_id
    print('-----getting users & balance with methods before spending-----')
    print(get_user_by_email(regular_user.email, session))
    print(get_balance_by_user_id(regular_user.user_id, session))
    print(get_user_by_id(admin_user.user_id, session))
    print(get_balance_by_user_id(admin_user.user_id, session))

    # initializing ML model and making predictions
    model = MlModel('catboost_model.cbm', 5.55)
    MlTask(regular_user, model, session).execute(['female', 26, '0', '3', 15.99])
    MlTask(admin_user, model, session).execute(['male', 36, '1', '1', 79.99])

    # getting transaction table
    print(f'\n-----printing TRANSACTION table-----')
    all_transactions = get_all_transactions(session)
    for transaction in all_transactions:
        print(transaction)

    # getting all users
    print('\n-----printing USER table-----')
    users = get_all_users(session)
    for user in users:
        print(user)

    # getting balance table
    print('\n-----printing BALANCE table-----')
    balances = get_all_balance(session)
    for balance in balances:
        print(balance)
