import main as app_module


def test_degrees_calculation_person_movie_person_is_1(monkeypatch):
    class _Node:
        def __init__(self, labels, props):
            self.labels = set(labels)
            self._props = props

        def __getitem__(self, key):
            return self._props[key]

    class _Path:
        def __init__(self, nodes):
            self.nodes = nodes
            self.relationships = [object(), object()]

    class _FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def run(self, *_args, **_kwargs):
            class _Result:
                def single(self_inner):
                    start = _Node({"Person"}, {"name": "A", "nconst": "nmA"})
                    movie = _Node({"Movie"}, {"title": "M", "tconst": "ttM"})
                    end = _Node({"Person"}, {"name": "B", "nconst": "nmB"})
                    return {"path": _Path([start, movie, end])}

            return _Result()

    class _FakeDriver:
        def session(self):
            return _FakeSession()

        def close(self):
            return None

    monkeypatch.setattr(app_module, "get_db", lambda: _FakeDriver())

    res = app_module.shortest_path("nmA", "nmB")
    assert res.path_found is True
    assert res.degrees == 1
    assert res.hops == 2
    assert [s.type for s in res.steps] == ["person", "movie", "person"]


def test_hops_calculation_movie_person_is_1_and_degrees_none(monkeypatch):
    class _Node:
        def __init__(self, labels, props):
            self.labels = set(labels)
            self._props = props

        def __getitem__(self, key):
            return self._props[key]

    class _Path:
        def __init__(self, nodes):
            self.nodes = nodes
            self.relationships = [object()]

    class _FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def run(self, *_args, **_kwargs):
            class _Result:
                def single(self_inner):
                    movie = _Node({"Movie"}, {"title": "M", "tconst": "ttM"})
                    person = _Node({"Person"}, {"name": "A", "nconst": "nmA"})
                    return {"path": _Path([movie, person])}

            return _Result()

    class _FakeDriver:
        def session(self):
            return _FakeSession()

        def close(self):
            return None

    monkeypatch.setattr(app_module, "get_db", lambda: _FakeDriver())

    res = app_module.shortest_path("movie:ttM", "person:nmA")
    assert res.path_found is True
    assert res.degrees is None
    assert res.hops == 1
    assert [s.type for s in res.steps] == ["movie", "person"]
