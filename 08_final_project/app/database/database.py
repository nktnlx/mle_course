from sqlmodel import Session, SQLModel, create_engine, select
from services.crud.user import create_user
from models.user import User
from auth.hash_password import HashPassword
import os


# Get database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "ml_service")

# Create PostgreSQL connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
hash_password = HashPassword()

def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(bind=engine)

    session = Session(engine)

    # Check if users already exist
    first_user_exists = session.exec(select(User).where(User.email == 'kate@mail.ru')).first()
    if not first_user_exists:
        create_user(
            User(
                user_name='kate',
                email='kate@mail.ru',
                password=hash_password.create_hash('ytrewq')
            ),
            session,
        )

    second_user_exists = session.exec(select(User).where(User.email == 'alex@mail.ru')).first()
    if not second_user_exists:
        create_user(
            User(
                user_name='alex',
                email='alex@mail.ru',
                password=hash_password.create_hash('qwerty')
            ),
            session,
        )