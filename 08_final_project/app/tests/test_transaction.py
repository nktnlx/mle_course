from fastapi import status


def test_get_transactions_success(client, test_user, session):
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
    client.post('/prediction', json=prediction_data)

    response = client.get(f'/transactions?email={test_user.email}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == test_user.email
    assert len(response.json()['transactions']) == 1


def test_get_transactions_no_transactions(client, admin_user):
    response = client.get(f'/transactions?email={admin_user.email}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'No transactions found for user' in response.json()['detail']
