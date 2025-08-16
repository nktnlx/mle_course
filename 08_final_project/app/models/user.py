from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = 'user'

    user_id: int = Field(unique=True, primary_key=True)
    user_name: str
    email: str = Field(unique=True)
    password: str

    def __str__(self) -> str:
        return (
            f'user_id: {self.user_id}, user_name: {self.user_name}, email: {self.email}'
        )
