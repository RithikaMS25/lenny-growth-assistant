
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "The Lenny Growth Assistant"
    assert response.json()["status"] == "running"


def test_liveness_endpoint():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_readiness_endpoint_reports_healthy_dependencies(monkeypatch):
    import app.main as main

    class Connection:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def execute(self, _query): return None

    class Response:
        status_code = 200
        def json(self): return {"models": [{"name": "qwen2.5:3b"}]}

    class Client:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def get(self, _url): return Response()

    class Engine:
        def connect(self): return Connection()

    monkeypatch.setattr(main, "engine", Engine())
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: Client())
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:3b")
    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"]["api"] == "ok"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["llm"] == "ok"


def test_readiness_returns_503_when_database_is_down(monkeypatch):
    import app.main as main

    class BrokenConnection:
        async def __aenter__(self): raise OSError("database offline")
        async def __aexit__(self, *args): return None

    class Response:
        status_code = 200
        def json(self): return {"models": [{"name": "qwen2.5:3b"}]}

    class Client:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def get(self, _url): return Response()

    class Engine:
        def connect(self): return BrokenConnection()

    monkeypatch.setattr(main, "engine", Engine())
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: Client())
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:3b")
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["checks"]["database"].startswith("error:")



def test_unknown_route_returns_404():
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
