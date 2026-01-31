from fastapi.testclient import TestClient
import main as app_module


def test_search_requires_min_length_2():
    client = TestClient(app_module.app)
    res = client.get("/search", params={"q": "a"})
    assert res.status_code == 422


def test_path_response_shape_when_no_path(monkeypatch):
    class _FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def run(self, *_args, **_kwargs):
            class _Result:
                def single(self):
                    return None

            return _Result()

    class _FakeDriver:
        def session(self):
            return _FakeSession()

        def close(self):
            return None

    monkeypatch.setattr(app_module, "get_db", lambda: _FakeDriver())

    client = TestClient(app_module.app)
    res = client.get("/path", params={"start_id": "nm1", "end_id": "nm2"})
    assert res.status_code == 200
    body = res.json()
    assert body["path_found"] is False
    assert body["degrees"] is None
    assert body["hops"] == 0
    assert body["steps"] == []
