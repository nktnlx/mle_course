from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_session
from models.user import User
from services.crud import user as UserService
from services.crud import balance as BalanceService
from typing import Optional
from pydantic import BaseModel


balance_route = APIRouter(tags=['Balance'])

class UserLogin(BaseModel):
    email: str
    amount: float
    target_email: Optional[str] = None


def get_current_user(email: str, session=Depends(get_session)) -> User:
    user = UserService.get_user_by_email(email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found.'
        )
    return user


@balance_route.get('/balance')
async def get_balance(email: str, session=Depends(get_session)) -> dict:
    current_user = get_current_user(email, session)
    balance = BalanceService.get_balance_by_user_id(current_user.user_id, session)
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Balance not found for user.'
        )
    return {
        'user_id': current_user.user_id,
        'email': current_user.email,
        'balance': balance.amount
    }


@balance_route.post('/balance')
async def add_balance(data: UserLogin, session=Depends(get_session)) -> dict:
    email = data.email
    amount = data.amount
    target_email = data.target_email
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Adding amount must be positive.'
        )
    current_user = get_current_user(email, session)
    if target_email:
        if current_user.is_admin:
            target_user = get_current_user(target_email, session)
            updated_balance = BalanceService.update_balance(
                session=session,
                user=current_user,
                amount=amount,
                spend=False,
                target_user_id=target_user.user_id
            )
            return {
                'message': 'Balance updated successfully.',
                'user_id': target_user.user_id,
                'email': target_user.email,
                'new_balance': updated_balance.amount
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only admins can add balance to other users.'
            )

    updated_balance = BalanceService.update_balance(
        session=session,
        user=current_user,
        amount=amount,
        spend=False,
        target_user_id=None
    )
    return {
        'message': 'Balance updated successfully.',
        'user_id': current_user.user_id,
        'email': current_user.email,
        'new_balance': updated_balance.amount
    }
