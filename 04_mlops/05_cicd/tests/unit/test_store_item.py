from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_store_item():
    item_id = 1
    test_value = "test_value"
    response = client.post(f"/store/{item_id}?item_value={test_value}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "value": test_value}
