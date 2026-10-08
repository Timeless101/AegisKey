import src.services.search as s
from src.storage.database_logic import search_for_search_view

def test_search_total_result_happy(monkeypatch):

    def fake_search(to_search, userid, database, limit, offset):
        return ("item", "item", "item", "item", "item", )

    monkeypatch.setattr(s, "search_for_search_view", fake_search)

    assert s.search_total_result(
        to_search="item",
        userid=1
    ) == 5

def test_search_total_result_none(monkeypatch):

    def fake_search(to_search, userid, database, limit, offset):
        return None

    monkeypatch.setattr(s, "search_for_search_view", fake_search)

    assert s.search_total_result(
        to_search="item",
        userid=1
    ) == 0