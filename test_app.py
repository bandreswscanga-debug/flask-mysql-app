import json
from app import app


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "API funcionando correctamente"


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code in [200, 503]


def test_api_data_endpoint():
    client = app.test_client()
    response = client.get("/api/data")
    assert response.status_code in [200, 500]
