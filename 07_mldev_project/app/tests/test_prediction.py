from fastapi import status
from services.crud.balance import update_balance
from services.crud.transaction import get_transactions_by_user_id
import time


def test_make_prediction_success(client, test_user, session):
    # Add balance to user
    update_balance(session, test_user, amount=100.0, spend=False, target_user_id=None)

    prediction_data = {
        'email': test_user.email,
        'data': {
            'sex': 'male',
            'age': 12,
            'is_alone': '1',
            'pclass': '3',
            'fare': 11.0,
        },
        'model_name': 'catboost',
    }

    response = client.post('/prediction', json=prediction_data)
    assert response.status_code == status.HTTP_200_OK
    assert 'ML task was queued for execution' in response.json()['message']
    assert response.json()['email'] == test_user.email

    time.sleep(3)
    transactions = get_transactions_by_user_id(test_user.user_id, session)
    for trans in transactions:
        if trans.transaction_type == 'prediction':
            assert round(trans.prediction_result, 2) == 0.49


def test_make_prediction_insufficient_balance(client, test_user):
    prediction_data = {
        'email': test_user.email,
        'data': {
            'sex': 'male',
            'age': 30,
            'is_alone': '1',
            'pclass': '1',
            'fare': 50.0,
        },
        'model_name': 'catboost',
    }
    response = client.post('/prediction', json=prediction_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Not enough balance to make a prediction' in response.json()['detail']
