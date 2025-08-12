from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_item_store_and_retrieve_integration():
    # Сначала тестируем сохранение данных
    item_id = 100
    test_value = "integration_test"
    store_response = client.post(f"/store/{item_id}?item_value={test_value}")

    assert store_response.status_code == 200
    assert store_response.json() == {
        "item_id": item_id,
        "value": test_value
    }

    # Затем тестируем извлечение тех же данных
    retrieve_response = client.get(f"/retrieve/{item_id}")
    assert retrieve_response.status_code == 200
    assert retrieve_response.json() == {
        "item_id": item_id,
        "value": test_value
    }
