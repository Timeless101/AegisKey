from src.interface.search_interface import screen_handler_with_options, screen_handler_search
import src.storage.storage_logic as storage_logic
from src.storage.database_logic import search_for_search_view
from src.services.pagination import Pagination
from src.services.view_items import open_item
from src.common.helper_functions import clear_screen
from src.services.add_items import add_main

class Search_flow:
    def __init__(self, userid: int, page_size: int, ):
        self.pag = Pagination(total_cred=0, page_size=page_size)
        self.search_main_view_data = storage_logic.get_screen_data(
                                    page_size=5,
                                    userid=userid,
                                    offset=0
                                )
        self.state = False

    def next_page(self):
        self.pag.next_page()

    def previous_page(self):
        self.pag.previous_page()

    def state_function(self, state):
        if state == True:
            self.state = True
        if state == False:
            self.state = False

    @property
    def current_page(self):
        return self.pag.current_page

    @property
    def offset(self):
        return self.pag.offset

    @property
    def page_size(self):
        return self.pag.page_size

    @property
    def total_pages(self):
        return self.pag.total_pages

    @property
    def showing_start(self):
        return self.pag.showing_items_start

    @property
    def showing_end(self):
        return self.pag.showing_items_end

    def reset_state(self):
        self.pag.reset_state()

    def get_total_cred(self):
        return self.total_cred

    def set_total_cred(self, new_total:int):
        self.pag.total_cred = new_total

def search_database(to_search: str, userid: int, page_size: int, offset: int, ):
        data = search_for_search_view(
            to_search=to_search,
            database="CLI_Data.db",
            userid=userid,
            limit=page_size,
            offset=offset
        )

        return data

def search_total_result(to_search: str, userid: int) -> int:
    data = search_for_search_view(
                to_search=to_search,
                database="CLI_Data.db",
                userid=userid,
                limit=None,
                offset=0
            )

    if data is None:
        return 0
    
    return len(data)

def search_main(total_cred: int, userid, encryption_key: bytes):
    search = Search_flow(userid=userid, page_size=5)
    search.set_total_cred(new_total=total_cred)
    first_screen_data = search.search_main_view_data

    while True:
        if search.state == True:
            return "s"
        
        clear_screen()

        user_search_output = screen_handler_search(total_credentials=total_cred, data=first_screen_data)
        if user_search_output == "":
            break

        while True:
            clear_screen()
            search_total_cred = search_total_result(
                to_search=user_search_output,
                userid=userid
            )

            db_data = search_database(
                        to_search=user_search_output,
                        userid=userid,
                        page_size=search.page_size,
                        offset=search.offset
                        )

            search.set_total_cred(search_total_cred)
            user_option = screen_handler_with_options(
                data=db_data,
                total_credentials=search_total_cred,
                current_page=search.current_page,
                max_page=search.total_pages,
                showing_items_end=search.showing_end,
                showing_items_start=search.showing_start
            )

            match user_option:

                case "n":
                    search.next_page()
                    continue

                case "p":
                    search.previous_page()
                    continue

                case "s":
                    search.reset_state()
                    break

                case "b":
                    search.state_function(state=True)
                    break

                case "#":
                    open_item(data=db_data, encryption_key=encryption_key, userid=userid)
                    break

                case "a":
                    add_main()
                    continue