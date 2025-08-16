from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_session
from services.crud import transaction as TransactionService
from routes.balance import get_current_user


transaction_route = APIRouter(tags=['Transaction'])

@transaction_route.get('/transactions')
async def get_transactions(email: str, session=Depends(get_session)) -> dict:
    current_user = get_current_user(email, session)
    transactions = TransactionService.get_transactions_by_user_id(current_user.user_id, session)
    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No transactions found for user.'
        )
    return {
        'user_id': current_user.user_id,
        'email': current_user.email,
        'transactions': transactions
    }