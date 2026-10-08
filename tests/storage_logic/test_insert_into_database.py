import src.storage.storage_logic as storage_logic
import src.storage.database_logic as Database_logic
import src.common.errors as errors
import pytest

def test_insert_into_database_happy_test(monkeypatch):
    
    def fake_insert_data(self, table_name: str, column_name: list, data_insert: list):
        return True
    
    monkeypatch.setattr(Database_logic.Insert_data, "insert_data", fake_insert_data)

    assert storage_logic.insert_data(
        table_name="table_name",
        column_name=["list", "of", "items"],
        data=["data", "list", "of", "items"]
        ) is True

def test_insert_into_database_wrong_data_type(monkeypatch):
    
    def fake_insert_data(self, table_name: str, column_name: list, data_insert: list):
        raise errors.WrongDataTypeDict
    
    monkeypatch.setattr(Database_logic.Insert_data, "insert_data", fake_insert_data)

    with pytest.raises(errors.WrongDataTypeDict):
        assert storage_logic.insert_data(
                                        table_name="table_name",
                                        column_name=["list", "of", "items"],
                                        data=["data", "list", "of", "items"]
                                        )
        
def test_insert_into_database_datalength_error(monkeypatch):
    
    def fake_insert_data(self, table_name: str, column_name: list, data_insert: list):
        raise errors.DataLengthError
    
    monkeypatch.setattr(Database_logic.Insert_data, "insert_data", fake_insert_data)

    with pytest.raises(errors.DataLengthError):
        assert storage_logic.insert_data(
                                        table_name="table_name",
                                        column_name=["list", "of", "items"],
                                        data=["data", "list", "of", "items"]
                                        )
        
def test_insert_into_database_insert_error(monkeypatch):
    
    def fake_insert_data(self, table_name: str, column_name: list, data_insert: list):
        raise errors.InsertError
    
    monkeypatch.setattr(Database_logic.Insert_data, "insert_data", fake_insert_data)

    with pytest.raises(errors.InsertError):
        assert storage_logic.insert_data(
                                        table_name="table_name",
                                        column_name=["list", "of", "items"],
                                        data=["data", "list", "of", "items"]
                                        )