from src.interface.search_interface import screen_handler_with_options, screen_handler_search
import src.storage.storage_logic as storage_logic
from src.storage.database_logic import search_for_search_view
from src.services.pagination import Pagination
from src.services.view_items import open_item
from src.common.helper_functions import clear_screen
from time import sleep

"""def search_database(to_search: str, userid: int, limit: int, offset: int):
    return search_for_search_view(
        to_search=to_search,
        database="CLI_Data.db",
        userid=userid,
        limit=limit,
        offset=offset
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
        db_data: list = search_database(to_search=output, userid=userid, limit=pag.page_size, offset=pag.offset)

        output = screen_handler_with_options(
            data=db_data,
            total_credentials=total_cred,
            current_page=pag.current_page,
            max_page=pag.total_pages,
            showing_items_start=pag.showing_items_start,
            showing_items_end=pag.showing_items_end,
        )

        match output:

            case "n":
                pag.next_page()

            case "p":
                pag.previous_page()

            case "s":
                continue

            case "#":
                open_item()
"""
class Test:
    def __init__(self, total_cred: int, page_size: int, userid: int,):
        self.pag = Pagination(total_cred=total_cred, page_size=page_size)
        self.userid = userid
        self.total_cred = total_cred


    def first_screen(self):
        output = screen_handler_search(total_credentials=self.total_cred, data=self.search_view(userid=self.userid))
        return self.search_database(to_search=output, userid=self.userid, limit=self.pag.page_size, offset=self.pag.offset)


    def next_page(self):
        self.pag.next_page()


    def previous_page(self):
        self.pag.previous_page()


    def search_database(self, to_search: str, userid: int, limit: int, offset: int):
        return search_for_search_view(
            to_search=to_search,
            database="CLI_Data.db",
            userid=userid,
            limit=limit,
            offset=offset
        )

    def search_view(self, userid: int) -> list[tuple]:
        return storage_logic.get_screen_data(
            page_size=5,
            userid=userid,
            offset=0
        )

    def second_screen(self, db_data):
        return screen_handler_with_options(
            data=db_data,
            total_credentials=self.total_cred,
            current_page=self.pag.current_page,
            max_page=self.pag.total_pages,
            showing_items_start=self.pag.showing_items_start,
            showing_items_end=self.pag.showing_items_end,
        )


def search_main(total_cred: int, userid):
    t = Test(total_cred=total_cred, userid=userid, page_size= 5)

    while True:
        clear_screen()
        db_data = t.first_screen()

        clear_screen()
        output = t.second_screen(db_data=db_data)

        match output:

            case "n":
                t.next_page()

            case "p":
                t.previous_page()

            case "s":
                continue

            case "b":
                break

            case "#":
                open_item()
    return "s"