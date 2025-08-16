from fastapi import status
from services.crud.balance import update_balance


def test_get_transactions_success(client, test_user, session):
    # Create a sample transaction
    update_balance(session, test_user, amount=100.0, spend=False, target_user_id=None)

    response = client.get(f'/transactions?email={test_user.email}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == test_user.email
    assert len(response.json()['transactions']) == 1
    assert response.json()['transactions'][0]['amount'] == 100.0


def test_get_transactions_no_transactions(client, admin_user):
    response = client.get(f'/transactions?email={admin_user.email}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'No transactions found for user' in response.json()['detail']
