import datetime

from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor


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


# task 6
# @app.get('/user/{id}')
# def get_user(id: int):
#     conn = psycopg2.connect(
#         "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml",
#         cursor_factory=RealDictCursor
#     )
#     cursor = conn.cursor()
#     query = '''
#         SELECT
#           gender,
#           age,
#           city
#         FROM
#           "user"
#         WHERE
#           id = %s
#         LIMIT
#           1
#         '''
#     cursor.execute(query, (id,))
#
#     result = cursor.fetchone()
#     return result


# task 7
# @app.get('/user/{id}')
# def get_user(id: int):
#     conn = psycopg2.connect(
#         "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml",
#         cursor_factory=RealDictCursor
#     )
#     cursor = conn.cursor()
#     query = '''
#         SELECT
#           gender,
#           age,
#           city
#         FROM
#           "user"
#         WHERE
#           id = %s
#         LIMIT
#           1
#         '''
#     cursor.execute(query, (id,))
#
#     result = cursor.fetchone()
#
#     if not result:
#         raise HTTPException(404, 'user not found')
#     return result


#task 8
def get_db():
    conn = psycopg2.connect(
        "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml",
        cursor_factory=RealDictCursor
    )
    return conn


@app.get('/user/{id}')
def get_user(id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        query = '''
            SELECT
              gender,
              age,
              city
            FROM 
              "user"
            WHERE 
              id = %s
            LIMIT 
              1
            '''
        cursor.execute(query, (id,))
        result = cursor.fetchone()

    if not result:
        raise HTTPException(404, 'user not found')
    return result


# task 9
class PostResponse(BaseModel):
    id: int
    text: str
    topic: str

    class Config:
        orm_mode=True


@app.get('/post/{id}', response_model=PostResponse)
def get_post_info(id: int, db=Depends(get_db)) -> PostResponse:
    with db.cursor() as cursor:
        query = '''
            SELECT
              id,
              text,
              topic
            FROM 
              "post"
            WHERE 
              id = %s
            LIMIT 
              1
            '''
        cursor.execute(query, (id,))
        result = cursor.fetchone()

    if not result:
        raise HTTPException(404, 'post not found')
    return PostResponse(**result)
