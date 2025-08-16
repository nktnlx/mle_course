from fastapi import status
from services.crud.transaction import get_transactions_by_user_id
import time


def test_make_prediction_success(client, test_user, session):
    prediction_data = {
        'email': test_user.email,
        'data': {
            'HadAngina': 1,
            'ChestScan': 0,
            'GeneralHealth': 1,
            'AgeCategory': 'Age_25_to_29',
            'DifficultyWalking': 1,
            'RemovedTeeth': 1,
            'HadDiabetes': 1,
            'SleepHours: 7,'
            'IsMale': 1,
            'WeightInKilograms': 57.7,
            'SmokerStatus': 'Never smoked',
            'HeightInMeters': 1.64,
            'AlcoholDrinkers': 1,
            'LastCheckupTime': 'Past_year',
            'PhysicalHealthDays': 11
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
            assert round(trans.prediction_result, 2) == 0.71
