from app.services.github_client import GitHubClient


def test_paginated_request_collects_every_page(monkeypatch):
    client = object.__new__(GitHubClient)
    calls = []

    def fake_get(path, params=None):
        calls.append((path, params))
        if params["page"] == 1:
            return [{"id": index} for index in range(100)]
        return [{"id": index} for index in range(100, 105)]

    monkeypatch.setattr(client, "_get", fake_get)

    items = client._get_paginated("/example")

    assert len(items) == 105
    assert [call[1]["page"] for call in calls] == [1, 2]
    assert all(call[1]["per_page"] == 100 for call in calls)


def test_paginated_request_stops_at_requested_limit(monkeypatch):
    client = object.__new__(GitHubClient)
    calls = []

    def fake_get(path, params=None):
        calls.append((path, params))
        return [{"id": index} for index in range(100)]

    monkeypatch.setattr(client, "_get", fake_get)

    items = client._get_paginated("/example", max_items=12)

    assert len(items) == 12
    assert len(calls) == 1
