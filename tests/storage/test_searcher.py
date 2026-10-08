from src.storage.database_logic import searcher
import sqlite3
import pytest
import src.common.errors as errors

@pytest.fixture
def db_path(tmp_path):
    db_path = tmp_path / "test.db"

    create_table = """
            CREATE TABLE vault_storage (
                cred_id,
                UserID,
                Service,
                Username,
                Password,
                Comment,
                CreationDate,
                EditedDate
            );
        """
    
    insert_data = """
        INSERT INTO vault_storage (cred_ID, UserID, Service, Username, Password, Comment, CreationDate, EditedDate)
        VALUES
            (1, 1, "test1", "test1.0.1", "test", "test", "test", "test1.0.1.1"), 
            (2, 2, "test2", "test2.0.1", "test", "test", "test", "test2.0.1.1"),
            (3, 2, "test2.1", "test2.1.1", "test", "test", "test", "test2.1.1.1"),
            (4, 3, "test3", "test3.0.1", "test", "test", "test", "test3.0.1.1"),
            (5, 3, "test3.1", "test3.1.1", "test", "test", "test", "test3.1.1.1"),
            (6, 3, "test3.2", "test3.2.2", "test", "test", "test", "test3.2.2.2");
    """
    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        c.execute(create_table)
        c.execute(insert_data)

        c.close()
    return db_path

def test_searcher_happy_test(db_path):

    assert searcher(
        table="vault_storage",
        columns=["cred_id", "UserID", "Service"],
        column=("UserID",),
        database_name=db_path,
        data_to_search=3
    ) == [(4, 3, "test3"), (5, 3, "test3.1"), (6, 3, "test3.2")]

    assert searcher(
            table="vault_storage",
            columns=["cred_id"],
            column=("UserID",),
            database_name=db_path,
            data_to_search=3
        ) == [(4,), (5,), (6,)]

def test_searcher_operation_error(db_path):
    with pytest.raises(errors.DatabaseError):
        assert searcher(
        table="vault_storage",
        columns=["cred_id" "UserID", "Service"],
        column=("UserID",),
        database_name=db_path,
        data_to_search=3
    )

def test_searcher_wrong_sql(db_path):
   with pytest.raises(errors.WrongSQLStatement):
        assert searcher(
        table="vault_storage; SELECT * FROM vault_storage",
        columns=["cred_id","UserID", "Service"],
        column=("UserID",),
        database_name=db_path,
        data_to_search=3
    )

def test_searcher_wrong_type_tuple(db_path):
    with pytest.raises(errors.WrongDataTypeTuple):
        assert searcher(
        table="vault_storage",
        columns=["cred_id","UserID", "Service"],
        column="UserID",
        database_name=db_path,
        data_to_search=3
    )

def test_searcher_wrong_type_list(db_path):
    with pytest.raises(errors.WrongDataTypeList):
        assert searcher(
        table="vault_storage",
        columns="cred_id",
        column=("UserID",),
        database_name=db_path,
        data_to_search=3
    )