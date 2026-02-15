from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_endpoints_sync():
    for url in ["/", "/health"]:
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["message"] == settings.app_description
        assert data["version"] == settings.app_version
