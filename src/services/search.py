from src.interface.search_interface import screen_handler_with_options, screen_handler_search
import src.storage.storage_logic as storage_logic
from src.storage.database_logic import search_for_search_view
from src.services.pagination import Pagination
from src.services.view_items import open_item
from src.common.helper_functions import clear_screen


class Search_flow:
    def __init__(self, total_cred: int, userid: int, page_size: int, ):
        self.pag = Pagination(total_cred=total_cred, page_size=page_size)
        self.search_main_view_data = storage_logic.get_screen_data(
                                    page_size=5,
                                    userid=userid,
                                    offset=0
                                )
        self.page_size = self.pag.page_size
        self.offset = self.pag.offset
        self.current_page = self.pag.current_page
        self.total_pages = self.pag.total_pages
        self.showing_start = self.pag.showing_items_start
        self.showing_end = self.pag.showing_items_end
        

    def next_page(self):
        self.pag.next_page()


    def previous_page(self):
        self.pag.previous_page()

    def state_function(self, state):
        if state == True:
            self.state == True
        if state == False:
            self.state == False

    @property
    def state(state):
        return state

def search_database(to_search: str, userid: int, page_size: int, offset: int, ):
        return search_for_search_view(
            to_search=to_search,
            database="CLI_Data.db",
            userid=userid,
            limit=page_size,
            offset=offset
        )


def search_main(total_cred: int, userid):
    search = Search_flow(total_cred=total_cred, userid=userid, page_size=5)
    first_screen_data = search.search_main_view_data
    

    while True:
        if search.state == True:
            return "s"
        clear_screen()
        user_search_output = screen_handler_search(total_credentials=total_cred, data=first_screen_data)
        if user_search_output == "":
            break

        while True:
            db_data = search_database(
                        to_search=user_search_output,
                        userid=userid,
                        page_size=search.page_size,
                        offset=search.offset
                        )

            user_option = screen_handler_with_options(
                data=db_data,
                total_credentials=total_cred,
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
                    break

                case "b":
                    search.state_function(state=True)
                    break

                case "#":
                    open_item()
                    break

"""
S typed in main view; 
data needs to be search for the search screen main view 5 entrys; class is initiated, self.search_main_data search for screen data.
dat is geven to the screen; screen_handler_search(data=first_screen_data)
screen is show with the data; main_view()
screen is waiting for input from user; screen_handler_search() is called -> what to be searched.
input will go to database; db_data = search.search_database(to_search=screen_handler_search(data=first_screen_data))
database gets the data; search_database -> return the database data
the data will go to the screen; screen_handler_with_options -> returns the user_option.


the screen shows the data with limit 5 (so 5 items will be shown)
user chooses a option: N or P;
then screen give the input back;
The match tree wil see what match;
N is choose;
input is handeld and given back;
get the data;
then it wil give the data to the screen;
screen shows the data;
and waits for new input.
P is choosen;
input is handeld and given back;
get the data;
then it wil give the data to the screen;
screen shows the data;
and waits for new input.
s is choosen;
input is handeld and given back;
get the data to show for search screen;
gives the data to the screen;
shows the search screen with the data and wait for input;
search is done;
gets back to the search result screen;
repead.
"""