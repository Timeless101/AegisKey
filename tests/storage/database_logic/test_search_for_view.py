import src.storage.database_logic as database_logic
import sqlite3
import pytest

@pytest.fixture
def database(tmp_path):
    db = tmp_path / "test.db"

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

    insert_data = '''
        INSERT INTO vault_storage (cred_ID, UserID, Service, Username, Password, Comment, CreationDate, EditedDate)
        VALUES
            (1, 1, 'bcc', 'username', 'password', 'comment', 'creationdate', 'editeddate'),
            (2, 1, 'microsoft', 'diego', 'password', 'comment', 'creationdate', 'editeddate'),
            (3, 1, 'microsoft', 'jasmijn', 'password', 'comment', 'creationdate', 'editeddate'),
            (4, 1, 'Adobe', 'username', 'password', 'comment', 'creationdate', 'editeddate'),
            (5, 1, 'bcc', 'admin', 'password', 'comment', 'creationdate', 'editeddate'),
            (6, 2, 'candelshop', 'username', 'password', 'comment', 'creationdate', 'editeddate'),
            (7, 2, 'diertentuin', 'username', 'password', 'comment', 'creationdate', 'editeddate'),
            (8, 2, 'eco placa', 'username', 'password', 'comment', 'creationdate', 'editeddate'),
            (9, 2, 'fox', 'username', 'password', 'comment', 'creationdate', 'editeddate');
    '''

    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        cursor.execute(create_table)
        cursor.execute(insert_data)

        cursor.close()

    return db

def test_search_for_view_limit_none(database):
    
    rows = database_logic.search_for_search_view(
        to_search="Adobe",
        database=database,
        userid=1,
        limit=None,
        offset=0
    )

    assert rows is not None

    #Shows that there is only one item.
    assert len(rows) == 1

    rows = database_logic.search_for_search_view(
            to_search="A",
            database=database,
            userid=1,
            limit=None,
            offset=0
        )

    assert len(rows) == 4

def test_search_for_view_limit(database):
    rows = database_logic.search_for_search_view(
        to_search="a",
        database=database,
        userid=1,
        limit=2,
        offset=0
    )

    assert rows is not None

    #Shows that there is only one item.
    assert len(rows) == 2

def test_search_for_view_none(database):
    rows = database_logic.search_for_search_view(
        to_search="Adobe",
        database=database,
        userid=1,
        limit=None,
        offset=0
    )

    assert rows is not None

    #Shows that there is only one item.
    assert len(rows) == 1

    rows = database_logic.search_for_search_view(
            to_search="aljfnalsjnvssdf",
            database=database,
            userid=1,
            limit=None,
            offset=0
        )

    assert rows is None

def test_search_for_view_six_items_in_list(database):
    rows = database_logic.search_for_search_view(
        to_search="Adobe",
        database=database,
        userid=1,
        limit=None,
        offset=0
    )

    assert rows is not None

    #Shows that there is only one item.
    assert len(rows) == 1

    rows = database_logic.search_for_search_view(
            to_search="A",
            database=database,
            userid=1,
            limit=None,
            offset=0
        )

    print(rows)
    assert len(rows[0]) == 6