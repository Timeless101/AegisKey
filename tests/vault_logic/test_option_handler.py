import src.core.vault_logic as vault_logic


def test_option_handler_test_add_items(monkeypatch):

    received= {"add_items_calls": 0}

    def fake_add_items(userid, encryption_key):
        received["add_items_calls"] += 1
        return "add_result"

    monkeypatch.setattr(vault_logic, "add_main", fake_add_items)

    result = vault_logic.option_handler("a", 1, b"test", 10)

    assert received["add_items_calls"] == 1
    assert result == "add_result"

def test_option_handler_test_view_screen(monkeypatch):

    received= {"view_screen_calls": 0}

    def fake_view_screen(userid, total_cred, encryption_key):
        received["view_screen_calls"] += 1
        return "view_screen"

    monkeypatch.setattr(vault_logic, "menu_flow", fake_view_screen)

    result = vault_logic.option_handler("v", 1, b"test", 10)

    assert received["view_screen_calls"] == 1
    assert result == "view_screen"


def test_option_handler_test_search_items(monkeypatch):

    received= {"search_item_calls": 0}

    def fake_search_item(total_cred, userid, encryption_key):
        received["search_item_calls"] += 1
        return "search_item"

    monkeypatch.setattr(vault_logic, "search_main", fake_search_item)

    result = vault_logic.option_handler("s", 1, b"test", 10)

    assert received["search_item_calls"] == 1
    assert result == "search_item"

def test_option_handler_test_quit_program(monkeypatch):

    received= {"quit_program_calls": 0}

    def fake_quit_program():
        received["quit_program_calls"] += 1
        return "quit_program"

    monkeypatch.setattr(vault_logic, "option_q", fake_quit_program)

    result = vault_logic.option_handler("q", 1, b"test", 10)

    assert received["quit_program_calls"] == 1
    assert result == "quit_program"

def test_option_handler_test_none():

    assert vault_logic.option_handler(None, 1, b"test", 10) is None

def test_option_handler_test_choice_not_in_list(monkeypatch):

    assert vault_logic.option_handler("w", 1, b"test", 10) is None