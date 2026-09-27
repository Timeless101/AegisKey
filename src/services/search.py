from src.interface.search_interface import screen_handler_with_options, screen_handler_search
import src.storage.storage_logic as storage_logic
from src.storage.database_logic import search_for_search_view
from src.services.pagination import Pagination



def search_screen():
    """screen_handler(
        data=data,
        total_credentials=total_cred,
        current_page=pag.current_page,
        max_page=pag.total_pages,
        showing_items_start=pag.showing_items_start,
        showing_items_end=pag.showing_items_end

        data: list, total_cred: int
    )"""
    return test()


def search_database(to_search: str, userid: int):
    return search_for_search_view(
        to_search=to_search,
        database="CLI_Data.db",
        userid=userid
    )

def search_view(userid: int, limit: int):
    return storage_logic.search_limited_amount_of_items_in_database(
        limit=5,
        userid=userid
    )

def search_main(total_cred: int, userid):
    pag = Pagination()
    while True: 
        output = screen_handler_search(total_credentials=total_cred, data=search_view(userid=userid))
        db_data = search_database(to_search=output, userid=userid)

    """to_search = search_screen()
    data = search_database(to_search=to_search, userid=userid)
    screen_handler(
        data=data,
        total_credentials=total_cred,
        current_page=1,
        max_page=1,
        showing_items_start=5,
        showing_items_end=1,
    )"""

    
    
