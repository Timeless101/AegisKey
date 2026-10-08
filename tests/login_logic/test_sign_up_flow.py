import src.core.login_logic as login_logic
import src.storage.storage_logic as storage_logic
import src.interface.error_messages as error_messages
import src.common.helper_functions as helper_functions
import pytest
import src.common.errors as errors


def test_sign_up_flow_happy_test(monkeypatch):

    def fake_get_input_and_validate_it():
        return "email@email.com", b"password_hash", b"hashedpassword", b"password_salt", b"encryption_salt"
    
    def fake_insert_sign_up_data(table_name: str, column_name: list, data: list):
        return True
    
    def fake_get_userid(email):
        return "1"

    def fake_get_encryption_key(input_password, encryption_salt):
        return b"encryption_key"

    monkeypatch.setattr(login_logic, "get_encryption_key", fake_get_encryption_key)
    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(storage_logic, "insert_data", fake_insert_sign_up_data)
    monkeypatch.setattr(login_logic, "get_input_and_validate_it", fake_get_input_and_validate_it)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.sign_up_flow() == ('email@email.com', '1', b'encryption_key')

def test_sign_up_flow_database_insert_False(monkeypatch):

    count = 0

    def fake_get_input_and_validate_it():
        return "email@email.com", b"password_hash", b"hashedpassword", b"password_salt", b"encryption_salt"
    
    def fake_insert_sign_up_data(table_name: str, column_name: list, data: list):
        nonlocal count

        if count == 0:
            count += 1
            return False
        
        return True
    
    def fake_get_userid(email):
        return "1"

    def fake_get_encryption_key(input_password, encryption_salt):
            return b"encryption_key"
    
    monkeypatch.setattr(login_logic, "get_encryption_key", fake_get_encryption_key)
    monkeypatch.setattr(storage_logic, "insert_data", fake_insert_sign_up_data)
    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(error_messages, "print_error_database", lambda: None)
    monkeypatch.setattr(login_logic, "get_input_and_validate_it", fake_get_input_and_validate_it)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.sign_up_flow() == ('email@email.com', '1', b'encryption_key')


def test_sign_up_flow_email_mismatch_error(monkeypatch):

    count = 0

    def fake_get_input_and_validate_it():

        nonlocal count

        if count == 0:
            count += 1
            raise errors.EmailMismatchError()

        return "email@email.com", b"password_hash", b"hashedpassword", b"password_salt", b"encryption_salt"
    
    def fake_insert_sign_up_data(table_name: str, column_name: list, data: list):
        return True
    
    def fake_get_userid(email):
        return "1"

    def fake_get_encryption_key(input_password, encryption_salt):
            return b"encryption_key"
    
    monkeypatch.setattr(login_logic, "get_encryption_key", fake_get_encryption_key)
    monkeypatch.setattr(storage_logic, "insert_data", fake_insert_sign_up_data)
    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_logic, "sleep", lambda _: None)
    monkeypatch.setattr(login_logic, "get_input_and_validate_it", fake_get_input_and_validate_it)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.sign_up_flow() == ('email@email.com', '1', b'encryption_key')

def test_sign_up_flow_password_mismatch_error(monkeypatch):

    count = 0

    def fake_get_input_and_validate_it():

        nonlocal count

        if count == 0:
            count += 1
            raise errors.PasswordMismatchError()

        return "email@email.com", b"password_hash", b"hashedpassword", b"password_salt", b"encryption_salt"
    
    def fake_insert_sign_up_data(table_name: str, column_name: list, data: list):
        return True
    
    def fake_get_userid(email):
        return "1"

    def fake_get_encryption_key(input_password, encryption_salt):
            return b"encryption_key"
    
    monkeypatch.setattr(login_logic, "get_encryption_key", fake_get_encryption_key)
    monkeypatch.setattr(storage_logic, "insert_data", fake_insert_sign_up_data)
    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_logic, "sleep", lambda _: None)
    monkeypatch.setattr(login_logic, "get_input_and_validate_it", fake_get_input_and_validate_it)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.sign_up_flow() == ('email@email.com', '1', b'encryption_key')


def test_sign_up_flow_duplication_error(monkeypatch):

    count = 0

    def fake_get_input_and_validate_it():

        nonlocal count

        if count == 0:
            count += 1
            raise errors.DuplicationError()

        return "email@email.com", b"password_hash", b"hashedpassword", b"password_salt", b"encryption_salt"
    
    def fake_insert_sign_up_data(table_name: str, column_name: list, data: list):
        return True
    
    def fake_create_vault_storage(table_name: str, columns: dict):
        return True
    
    def fake_get_userid(email):
        return "1"

    def fake_get_encryption_key(input_password, encryption_salt):
            return b"encryption_key"

    monkeypatch.setattr(login_logic, "get_encryption_key", fake_get_encryption_key)
    monkeypatch.setattr(storage_logic, "insert_data", fake_insert_sign_up_data)
    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_logic, "sleep", lambda _: None)
    monkeypatch.setattr(login_logic, "get_input_and_validate_it", fake_get_input_and_validate_it)
    monkeypatch.setattr(storage_logic, "table_creator", fake_create_vault_storage)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.sign_up_flow() == ('email@email.com', '1', b'encryption_key')


def test_sign_up_flow_key_isnot_bytes(monkeypatch):

    def fake_get_input_and_validate_it():
            return "email@email.com", b"password_hash", b"hashedpassword", b"password_salt", b"encryption_salt"
        
    def fake_insert_sign_up_data(table_name: str, column_name: list, data: list):
        return True
    
    def fake_get_userid(email):
        return "1"

    def fake_get_encryption_key(input_password, encryption_salt):
        return str("encryption_key")

    def fake_exit_program():
        raise SystemExit

    monkeypatch.setattr(login_logic, "get_encryption_key", fake_get_encryption_key)
    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(storage_logic, "insert_data", fake_insert_sign_up_data)
    monkeypatch.setattr(login_logic, "get_input_and_validate_it", fake_get_input_and_validate_it)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)
    monkeypatch.setattr(error_messages, "print_internal_error", lambda: None)
    monkeypatch.setattr(login_logic, "exit_program", fake_exit_program)
    
    with pytest.raises(SystemExit):
        assert login_logic.sign_up_flow()