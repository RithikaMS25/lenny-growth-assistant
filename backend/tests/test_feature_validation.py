from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ship30_rejects_too_short_topic():
    response = client.post("/api/chat/ship30", json={"topic": "short"})
    assert response.status_code == 422


def test_artifact_rejects_unsupported_format():
    response = client.post("/api/chat/artifact", json={"prompt": "Make a product framework", "artifact_type": "javascript"})
    assert response.status_code == 422
