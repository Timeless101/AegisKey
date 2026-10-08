import src.core.login_logic as login_logic
import src.interface.login_interface as login_interface
import src.common.helper_functions as helper_functions
import src.common.errors as errors
import pytest

def test_login_flow_happy_test(monkeypatch):

    def fake_login_screen():
        return "test@test.com", "password"

    def fake_sign_in_function(email, password):
        return b"true"

    def fake_get_userid(input_email):
        return "1"

    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_interface, "login_screen", fake_login_screen)
    monkeypatch.setattr(login_logic, "sign_in_function", fake_sign_in_function)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.login_flow() == ("test@test.com", "1", b"true")

def test_login_flow_email_error(monkeypatch):

    count = 0

    def fake_login_screen():
        return "test@test.com", "password"

    def fake_sign_in_function(email, password):
        nonlocal count

        if count == 0:
            count += 1
            raise errors.EmailMismatchError()
        return b"true"

    def fake_get_userid(input_email):
        return "1"

    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_interface, "login_screen", fake_login_screen)
    monkeypatch.setattr(login_logic, "sleep", lambda _: None)
    monkeypatch.setattr(login_logic, "sign_in_function", fake_sign_in_function)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.login_flow() == ("test@test.com", "1", b"true")
    assert count == 1

def test_login_flow_account_error(monkeypatch):

    count = 0

    def fake_login_screen():
        return "test@test.com", "password"

    def fake_sign_in_function(email, password):
        nonlocal count

        if count == 0:
            count += 1
            raise errors.AccountError()
        return b"true"

    def fake_get_userid(input_email):
        return "1"

    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_interface, "login_screen", fake_login_screen)
    monkeypatch.setattr(login_logic, "sleep", lambda _: None)
    monkeypatch.setattr(login_logic, "sign_in_function", fake_sign_in_function)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.login_flow() == ("test@test.com", "1", b"true")
    assert count == 1

def test_login_flow_invalid_password_error(monkeypatch):

    count = 0

    def fake_login_screen():
        return "test@test.com", "password"

    def fake_sign_in_function(email, password):
        nonlocal count

        if count == 0:
            count += 1
            raise errors.InvalidPasswordError()
        return b"true"

    def fake_get_userid(input_email):
        return "1"

    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_interface, "login_screen", fake_login_screen)
    monkeypatch.setattr(login_logic, "sleep", lambda _: None)
    monkeypatch.setattr(login_logic, "sign_in_function", fake_sign_in_function)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)

    assert login_logic.login_flow() == ("test@test.com", "1", b"true")
    assert count == 1


def test_login_flow_key_isnot_bytes(monkeypatch):

    def fake_login_screen():
        return "test@test.com", "password"

    def fake_sign_in_function(email, password):
        return "true"

    def fake_get_userid(input_email):
        return "1"

    def fake_system_exit():
        raise SystemExit

    monkeypatch.setattr(login_logic, "clear_screen", lambda: None)
    monkeypatch.setattr(login_interface, "login_screen", fake_login_screen)
    monkeypatch.setattr(login_logic, "sleep", lambda _: None)
    monkeypatch.setattr(login_logic, "sign_in_function", fake_sign_in_function)
    monkeypatch.setattr(login_logic, "get_userid", fake_get_userid)
    monkeypatch.setattr(login_logic, "exit_program", fake_system_exit)

    with pytest.raises(SystemExit):
        assert login_logic.login_flow()
