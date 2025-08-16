from fastapi import status
from services.crud.balance import update_balance


def test_get_balance_success(client, test_user, session):
    # Initialize balance for test user
    update_balance(session, test_user, amount=100.0, spend=False, target_user_id=None)
    response = client.get(f'/balance?email={test_user.email}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == test_user.email
    assert response.json()['balance'] == 100.0


def test_add_balance_success(client, test_user, session):
    balance_data = {
        'email': test_user.email,
        'amount': 50.0,
    }
    response = client.post('/balance', json=balance_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['new_balance'] == 50.0
    assert response.json()['email'] == test_user.email


def test_add_balance_negative_amount(client, test_user):
    balance_data = {
        'email': test_user.email,
        'amount': -10.0,
    }
    response = client.post('/balance', json=balance_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Adding amount must be positive' in response.json()['detail']


def test_spend_balance_success(client, test_user, session):
    # first we will add some credits to a user balance
    update_balance(session, test_user, amount=100.0, spend=False, target_user_id=None)
    initial_balance = test_user.balance.amount

    # now we will spend some credits
    amount_to_spend = 10
    update_balance(session, test_user, amount=amount_to_spend, spend=True, target_user_id=None)

    response = client.get(f'/balance?email={test_user.email}')
    balance_after_spending = response.json()['balance']
    assert balance_after_spending == initial_balance - amount_to_spend


def test_spend_balance_below_zero(client, test_user, session):
    initial_balance = test_user.balance.amount  # initial balance is zero by default

    # trying to spend some credits by making a prediction
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
    # getting a message of a not sufficient balance
    response = client.post('/prediction', json=prediction_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Not enough balance to make a prediction' in response.json()['detail']

    # checking that the balance remained the same
    balance_response = client.get(f'/balance?email={test_user.email}')
    balance_after_spending = balance_response.json()['balance']
    assert balance_after_spending == initial_balance  # nothing was spent because of zero credits on the initial balance


def test_admin_add_balance_to_other_user(client, admin_user, test_user, session):
    balance_data = {
        'email': admin_user.email,
        'amount': 30.0,
        'target_email': test_user.email,
    }
    response = client.post('/balance', json=balance_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['new_balance'] == 30.0
    assert response.json()['email'] == test_user.email


def test_non_admin_add_balance_to_other_user(client, test_user, admin_user, session):
    balance_data = {
        'email': test_user.email,
        'amount': 20.0,
        'target_email': admin_user.email,
    }
    response = client.post('/balance', json=balance_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'Only admins can add balance to other users' in response.json()['detail']
