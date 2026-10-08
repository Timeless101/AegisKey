from src.storage.database_logic import search_interface_password_id
import sqlite3


def test_search_interface_password_id_user_2(tmp_path):
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

    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        cursor.execute(create_table)
        cursor.execute(insert_data)


    rows = search_interface_password_id(
        userid=2,
        database=db,
        limit=3
    )

    assert rows is not None
    assert len(rows) == 2

    #Check Screen_number_ID
    assert rows[0][0] == 1
    assert rows[1][0] == 2

def test_search_interface_password_id_user_3(tmp_path):
    db = tmp_path / "test.db"

    create_table = """
        CREATE TABLE vault_storage (
            cred_id INTEGER,
            UserID INTEGER,
            Service TEXT,
            Username TEXT,
            Password TEXT,
            Comment TEXT,
            CreationDate TEXT,
            EditedDate TEXT
        );
    """

    insert_data = """
        INSERT INTO vault_storage
        VALUES
            (1, 1, "test", "test", "test", "test", "test", "test"), 
            (2, 2, "test", "test", "test", "test", "test", "test"),
            (3, 2, "test", "test", "test", "test", "test", "test"),
            (4, 3, "test", "test", "test", "test", "test", "test"),
            (5, 3, "test", "test", "test", "test", "test", "test"),
            (6, 3, "test", "test", "test", "test", "test", "test");
    """

    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        cursor.execute(create_table)
        cursor.execute(insert_data)


    rows = search_interface_password_id(
        userid=3,
        database=db,
        limit=3
    )

    assert rows is not None
    assert len(rows) == 3

    #Check Screen_number_ID
    assert rows[0][0] == 1
    assert rows[1][0] == 2
    assert rows[2][0] == 3


def test_search_interface_password_None(tmp_path):
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

    insert_data = """
        INSERT INTO vault_storage
        VALUES
            (1, 1, "test", "test", "test", "test", "test", "test"), 
            (2, 2, "test", "test", "test", "test", "test", "test"),
            (3, 2, "test", "test", "test", "test", "test", "test"),
            (4, 3, "test", "test", "test", "test", "test", "test"),
            (5, 3, "test", "test", "test", "test", "test", "test"),
            (6, 3, "test", "test", "test", "test", "test", "test");
    """

    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        cursor.execute(create_table)
        cursor.execute(insert_data)


    rows = search_interface_password_id(
        userid=10,
        database=db,
        limit=3
    )

    assert rows is None