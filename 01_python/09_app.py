import datetime

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

# task 1
# @app.get('/')
# def say_hello():
#     return 'hello, world'


# task 2
@app.get('/')
def sum_numbers(a: int, b: int) -> int:
    return a + b


# task 3
@app.get('/sum_date')
def sum_date(current_date: datetime.date, offset: int) -> datetime.date:
    return current_date + datetime.timedelta(offset)


# task 4
class User(BaseModel):
    name: str
    surname: str
    age: int
    registration_date: datetime.date


# task 5
@app.post('/user/validate')
def validate_user(user: User):
    return f'Will add user: {user.name} {user.surname} with age {user.age}'
