import src.storage.storage_logic as storage_logic
import src.common.errors as errors
import pytest


#test search with no result.
def test_data_row_search_no_results(monkeypatch):
    def fake_search_data(table_name: str, table_column: str, data_to_be_searched: str):
        return None
    
    monkeypatch.setattr(storage_logic, "search_data", fake_search_data)

    assert storage_logic.data_row_search(email="fake@fake.com", table_column="Email", table_name="login_information") is None

def test_data_row_search_table_error(monkeypatch):
    def fake_search_data(table_name: str, table_column: str, data_to_be_searched: str):
        raise errors.TableError()
    
    monkeypatch.setattr(storage_logic, "search_data", fake_search_data)

    with pytest.raises(errors.TableError):
        assert storage_logic.data_row_search(email="fake@fake.com", table_column="Email", table_name="login_information")


#test search with result.
def test_data_row_search_happy_test(monkeypatch):
    def fake_search_data(table_name: str, table_column: str, data_to_be_searched: str):
        return [(1, "fake@fake.com", b"fake_hash")]
    
    monkeypatch.setattr(storage_logic, "search_data", fake_search_data)

    assert storage_logic.data_row_search(email="fake@fake.com", table_column="Email", table_name="login_information") == (1, "fake@fake.com", b"fake_hash")