import src.services.search as s

def test_search_flow_starts_on_first_page(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )

    search = s.Search_flow(userid=1, page_size=5)

    assert search.current_page == 1
    assert search.offset == 0

def test_search_flow_next_page(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )
    search = s.Search_flow(userid=1, page_size=5)

    search.set_total_cred(new_total=10)
    search.next_page()

    assert search.current_page == 2
    assert search.offset == 5

def test_search_flow_previous_page(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )
    search = s.Search_flow(userid=1, page_size=5)

    search.set_total_cred(new_total=15)
    for _ in range(2): search.next_page()
    
    assert search.current_page == 3
    assert search.offset == 10

    search.previous_page()

    assert search.current_page == 2
    assert search.offset == 5

def test_search_flow_reset(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )
    search = s.Search_flow(userid=1, page_size=5)
    search.state_function(True)
    search.set_total_cred(new_total=15)
    for _ in range(2): search.next_page()
    
    assert search.current_page == 3
    assert search.offset == 10

    search.reset_state()

    assert search.current_page == 1
    assert search.offset == 0
    assert search.state is False

def test_search_flow_state(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )
    search = s.Search_flow(userid=1, page_size=5)

    search.state_function(True)
    assert search.state is True

    search.state_function(False)
    assert search.state is False

def test_search_flow_total_cred(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )
    search = s.Search_flow(userid=1, page_size=5)

    assert search.get_total_cred() == 0
    search.set_total_cred(50)
    assert search.get_total_cred() == 50

def test_search_flow_pagination_next_does_nothing(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )

    search = s.Search_flow(userid=1, page_size=5)

    search.set_total_cred(new_total=5)
    assert search.get_total_cred() == 5
    assert search.current_page == 1
    assert search.offset == 0

    search.next_page()
    assert search.current_page == 1
    assert search.offset == 0

def test_search_flow_pagination_previous_does_nothing(monkeypatch):
    monkeypatch.setattr(
        "src.services.search.storage_logic.get_screen_data",
        lambda **kwargs: []
    )

    search = s.Search_flow(userid=1, page_size=5)

    search.set_total_cred(new_total=5)
    assert search.get_total_cred() == 5
    assert search.current_page == 1
    assert search.offset == 0

    search.previous_page()
    assert search.current_page == 1
    assert search.offset == 0