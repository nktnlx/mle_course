from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_retrieve_item():
    item_id = 2
    test_value = "another_test_value"
    client.post(f"/store/{item_id}?item_value={test_value}")
    response = client.get(f"/retrieve/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "value": test_value}
