from src.interface.search_interface import screen_handler_with_options, screen_handler_search
import src.storage.storage_logic as storage_logic
from src.storage.database_logic import search_for_search_view
from src.services.pagination import Pagination
from src.services.view_items import open_item
from src.common.helper_functions import clear_screen


class Search_flow:
    def __init__(self, total_cred: int, page_size: int, userid: int,):
        self.pag = Pagination(total_cred=total_cred, page_size=page_size)
        self.userid = userid
        self.total_cred = total_cred


    def first_screen(self):
        output = screen_handler_search(total_credentials=self.total_cred, data=self.search_view(userid=self.userid))
        return self.search_database(to_search=output)


    def next_page(self):
        self.pag.next_page()
        return self.search_database()


    def previous_page(self):
        self.pag.previous_page()
        return self.search_database()


    def search_database(self, to_search: str):
        return search_for_search_view(
            to_search=to_search,
            database="CLI_Data.db",
            userid=self.userid,
            limit=self.pag.page_size,
            offset=self.pag.offset
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
    search = Search_flow(total_cred=total_cred, userid=userid, page_size= 5)

    while True:
        clear_screen()
        db_data = search.first_screen()

        clear_screen()
        output = search.second_screen(db_data=db_data)

        match output:

            case "n":
                pass

            case "p":
                pass

            case "s":
                pass

            case "b":
                pass

            case "#":
                pass

"""
S typed: Search screen is show;
screen is waiting for input from user;
input will go to database;
database gets the data;
the data will go to the screen;
the screen shows the data with limit 5 (so 5 items will be shown)
user chooses a option: N or P;
then screen give the input back;
The match tree wil see what match;
N is choosen, so screen wil get the data;
then it wil give the data to the screen;


"""