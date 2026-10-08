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

def test_search_for_view_items_happy_test(database):
    
    rows = database_logic.search_for_view_items(
        userid= 1,
        limit= 5,
        offset=0,
        database=database)

    assert rows is not None

    #If row returns 5 items
    assert len(rows) == 5

    #Check for service ASC
    assert rows[0][2] == "Adobe"

    #Check for username ASC
    assert rows[2][3] == "username"
    assert rows[3][3] == "diego"