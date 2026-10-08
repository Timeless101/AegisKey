import src.storage.database_logic as database_logic
import sqlite3
import pytest
import src.common.errors as errors

def test_create_database_locked(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"

    def fake_connect(*args, **kwargs):
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(database_logic.sqlite3, "connect", fake_connect)

    with pytest.raises(errors.DatabaseError) as caught_error:
        database_logic.create_database(db_path)

    assert isinstance(
        caught_error.value.__cause__,
        sqlite3.OperationalError
    )

    assert str(caught_error.value.__cause__) == "database is locked"


def test_create_database_is_true(tmp_path):
    db_path = tmp_path / "test.db"

    assert database_logic.create_database(db_path) is True