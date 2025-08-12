from fastapi.testclient import TestClient
from src.api.app import app


client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_model_info():
    response = client.get('/model-info')
    assert response.status_code == 200
    assert 'model' in response.json()
    assert 'metrics' in response.json()
    assert 'parameters' in response.json()


def test_predict():
    data = {
        'fixed_acidity': 7.4,
        'volatile_acidity': 0.7,
        'citric_acid': 0.0,
        'residual_sugar': 1.9,
        'chlorides': 0.076,
        'free_sulfur_dioxide': 11.0,
        'total_sulfur_dioxide': 34.0,
        'density': 0.9978,
        'pH': 3.51,
        'sulphates': 0.56,
        'alcohol': 9.4,
    }
    response = client.post('/predict', json=data)
    assert response.status_code == 200
    assert 'predicted_quality' in response.json()
