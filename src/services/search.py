from src.interface.search_interface import screen_handler, test
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

def search_main(total_cred: int, userid):
    while True:
        to_search = search_screen()
        data = search_database(to_search=to_search, userid=userid)

        if data is None:
            continue

        for item in data:
            print(item)
        input()