import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from api import app
from database.database import get_session
from models.user import User
from auth.hash_password import HashPassword


# Create a test database (in-memory SQLite for isolation)
@pytest.fixture(name='test_engine')
def test_engine():
    engine = create_engine(
        'sqlite:///database.db',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


# Create a session for the test database
@pytest.fixture(name='session')
def session_fixture(test_engine):
    with Session(test_engine) as session:
        yield session


# Override FastAPI dependency to use the test database
def override_get_session(session):
    def _override_get_session():
        yield session
    return _override_get_session


# FastAPI test client
@pytest.fixture(name='client')
def client_fixture(session):
    app.dependency_overrides[get_session] = override_get_session(session)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Create a test user
@pytest.fixture(name='test_user')
def test_user_fixture(session):
    hash_password = HashPassword()
    user = User(
        user_name='testuser',
        email='testuser@example.com',
        password=hash_password.create_hash('testpassword'),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
