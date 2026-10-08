import src.services.search as search

def test_search_total_result_happy_test(monkeypatch):
    def fake_search_for_search_view(to_search, database, userid, limit, offset):
        return [("items"), ("item"), ("item"), ("item")]

    monkeypatch.setattr(search, "search_for_search_view", fake_search_for_search_view)

    assert search.search_total_result(to_search="item", userid=1) == 4

def test_search_total_result_none(monkeypatch):
    def fake_search_for_search_view(to_search, database, userid, limit, offset):
        return None

    monkeypatch.setattr(search, "search_for_search_view", fake_search_for_search_view)

    assert search.search_total_result(to_search="item", userid=1) == 0