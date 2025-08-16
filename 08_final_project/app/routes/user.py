from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_session
from models.user import User
from services.crud import user as UserService
from typing import List
from auth.hash_password import HashPassword


user_route = APIRouter(tags=['User'])
hash_password = HashPassword()

@user_route.post('/signup')
async def signup(data:User, session=Depends(get_session)):
    if UserService.get_user_by_email(data.email, session) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with this email already exists!!!')

    hashed_password = hash_password.create_hash(data.password)
    data.password = hashed_password
    UserService.create_user(data, session)

    return {'message': 'User successfully created!'}


@user_route.post('/signin')
async def signin(data: User, session=Depends(get_session)) -> dict:
    user = UserService.get_user_by_email(data.email, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist!')

    if not hash_password.verify_hash(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Wrong credentials passed!')

    return {'message': 'User signed in successfully.'}


@user_route.get('/users', response_model=List[User])
async def get_all_users(session=Depends(get_session)) -> list:
    return UserService.get_all_users(session)