from models.ml_model import MlModel
from models.ml_task import MlTask
from models.user import User
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
    first_user = create_user(
        User(
            user_id=8888,
            user_name='kate',
            email='kate@mail.ru',
            password='ytrewq'),
        session,
    )

    # Add an admin user
    second_user = create_user(
        User(
            user_id=9999,
            user_name='alex',
            email='alex@mail.ru',
            password='qwerty',
        ),
        session,
    )


    # getting users by id, by email
    print('-----getting users & balance with methods before spending-----')
    print(get_user_by_email(first_user.email, session))
    print(get_user_by_id(second_user.user_id, session))

    # initializing ML model and making predictions
    model = MlModel('catboost_model.cbm')
    MlTask(first_user, model, session).execute([0, 0, 1, 'Age_25_to_29', 1, 1, 1, 2, 1, 57.7, 'Never smoked', 1.64, 1, 'Past_year', 11], '1')
    MlTask(second_user, model, session).execute([1, 0, 1, 'Age_80_or_older', 1, 1, 1, 2, 1, 77.7, 'Smokes_every_day', 1.84, 1, '5_or_more_years_ago', 11], '2')

    # getting transaction table
    print(f'\n-----printing TRANSACTION table-----')
    all_transactions = get_all_transactions(session)
    for transaction in all_transactions:
        print(transaction)
