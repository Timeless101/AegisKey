import sqlite3

from src.storage.database_logic import delete_item


def create_test_database(tmp_path):
    database = tmp_path / "delete_test.db"

    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE vault_storage (
                cred_id INTEGER PRIMARY KEY,
                UserID INTEGER NOT NULL
            );
            """
        )
        connection.execute(
            "INSERT INTO vault_storage (cred_id, UserID) VALUES (?, ?)",
            (1, 1)
        )

    return database


def test_delete_item_returns_true_when_row_is_deleted(tmp_path):
    database = create_test_database(tmp_path)

    assert delete_item(
        database=database,
        table="vault_storage",
        cred_id=1,
        userid=1
    ) is True


def test_delete_item_returns_false_for_non_owned_or_missing_row(tmp_path):
    database = create_test_database(tmp_path)

    assert delete_item(
        database=database,
        table="vault_storage",
        cred_id=1,
        userid=2
    ) is False
