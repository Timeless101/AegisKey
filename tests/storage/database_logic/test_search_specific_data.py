import pytest
import src.common.errors as errors
import sqlite3
from src.storage.database_logic import search_specific_data

@pytest.fixture
def db_path(tmp_path):
    db_path = tmp_path / "test.db"

    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()

        sql = "CREATE TABLE IF NOT EXISTS test_table (Id TEXT);"
        sql1 = "INSERT INTO test_table (Id) VALUES ('hello');"
        c.execute(sql)
        c.execute(sql1)
        connection.commit()

        c.close()
    return db_path

def test_search_function_happy_test(db_path):
    data = search_specific_data(
        table="test_table",
        column="Id",
        data_to_be_searched="hello",
        database_name=db_path
    )
    assert data == [('hello',)]

def test_search_function_wrong_table(db_path):
    with pytest.raises(errors.TableError):
        search_specific_data(
            table="test.db",
            column="test",
            data_to_be_searched="test_data",
            database_name=db_path
        )


def test_search_function_wrong_column(db_path):
    with pytest.raises(errors.TableError):
        search_specific_data(
            table="test-table",
            column="wrong_column",
            data_to_be_searched="test_data",
            database_name=db_path
        )


def test_search_function_wrong_data_to_be_searched(db_path):
        assert search_specific_data(
            table="test_table",
            column="Id",
            data_to_be_searched="Whut?",
            database_name=db_path
        ) is None