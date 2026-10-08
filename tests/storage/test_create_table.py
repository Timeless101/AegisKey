import pytest
import src.common.errors as errors
from src.storage.database_logic import create_table


def test_create_tabale__wrong_input(tmp_path):
    db_path = tmp_path / "test.db"

    with pytest.raises(errors.WrongDataTypeDict):
        create_table(
            database_name=str(db_path),
            table_name="bad",
            columns="hello"
        )

def test_create_tabale_raise_error(tmp_path):
    db_path = tmp_path / "test.db"

    with pytest.raises(errors.TableError):
        create_table(
            database_name=str(db_path),
            table_name="bad",
            columns={"hello": "how are you?",
                     "what": "????",}
        )