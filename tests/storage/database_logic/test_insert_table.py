import pytest
import sqlite3
import src.common.errors as errors
from src.storage.database_logic import insert_data

def test_insert_missing_table_raises_insert_error(tmp_path):
    db_path = tmp_path / "test.db"

    with pytest.raises(errors.InsertError):
        insert_data(
            table_name="missing_table",
            column_name=["Email", "Password"],
            data_insert=["test@example.com", "hash"],
            database_name=str(db_path)
        )

def test_insert_missing_table_raises_column_not_list(tmp_path):
    db_path = tmp_path / "test.db"
    create_table = "CREATE TABLE IF NOT EXISTS Test_Table (hello, ola)"

    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        c.execute(create_table)

    with pytest.raises(errors.WrongDataTypeList):
        insert_data(
            table_name="Test_Table",
            column_name="hello",
            data_insert=["hoi",],
            database_name=str(db_path)
        )

def test_insert_missing_table_raises_data_not_list(tmp_path):
    db_path = tmp_path / "test.db"
    create_table = "CREATE TABLE IF NOT EXISTS Test_Table (hello, ola)"

    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        c.execute(create_table)

    with pytest.raises(errors.WrongDataTypeList):
        insert_data(
            table_name="Test_Table",
            column_name=["hello",],
            data_insert="hoi",
            database_name=str(db_path)
        )

def test_insert_missing_table_raises_list_length_error(tmp_path):
    db_path = tmp_path / "test.db"
    create_table = "CREATE TABLE IF NOT EXISTS Test_Table (hello, ola)"

    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        c.execute(create_table)

    with pytest.raises(errors.DataLengthError):
        insert_data(
            table_name="Test_Table",
            column_name=["hello", "hello"],
            data_insert=["hoi",],
            database_name=str(db_path)
        )

def test_insert_insert_error(tmp_path):
    db_path = tmp_path / "test.db"
    create_table = "CREATE TABLE IF NOT EXISTS Test_Table (hello, ola)"

    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        c.execute(create_table)

    with pytest.raises(errors.InsertError):
        insert_data(
            table_name="e",
            column_name=["hello",],
            data_insert=["hoi",],
            database_name=str(db_path)
        )

def test_insert_happy_test(tmp_path):
    db_path = tmp_path / "test.db"
    create_table = "CREATE TABLE IF NOT EXISTS Test_Table (hello, ola)"

    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        c.execute(create_table)

    assert insert_data(
        table_name="Test_table",
        column_name=["hello", "ola"],
        data_insert=["hoi", "hoi"],
        database_name=str(db_path)
    )