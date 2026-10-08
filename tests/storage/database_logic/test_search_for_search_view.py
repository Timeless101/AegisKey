from src.storage.database_logic import search_for_search_view
import sqlite3

def test_search_For_search_view_happy_test(tmp_path):
    db = tmp_path / "database.db"

    create_db = "CREATE TABLE IF NOT EXITST vault_storage (cred_id, userid, service, username, password, comment, creationdate, editeddate)"
    insert_data = "INSERT INTO vault_storage (cred_id, userid, service, username, password, comment creationdate, editeddate) 1, 1, 'hello', 'hello', 'hello', 'hello', '2026-10-10', '2026-10-10'"