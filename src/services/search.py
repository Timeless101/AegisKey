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

def search_view(userid: int) -> list[tuple]:
    return storage_logic.search_limited_amount_of_items_in_database(
        limit=5,
        userid=userid
    )

def search_main(total_cred: int, userid):
    pag = Pagination(total_cred=total_cred, page_size=5)
    while True: 
        output: str = screen_handler_search(total_credentials=total_cred, data=search_view(userid=userid))
        db_data: list = search_database(to_search=output, userid=userid)
        screen_handler_with_options(
            data=db_data,
            total_credentials=total_cred,
            current_page=pag.current_page,
            max_page=pag.total_pages,
            showing_items_start=pag.showing_items_start,
            showing_items_end=pag.showing_items_end,
        )

    
    
