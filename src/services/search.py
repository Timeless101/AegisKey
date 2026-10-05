from src.interface.search_interface import screen_handler_with_options, screen_handler_search
import src.storage.storage_logic as storage_logic
from src.storage.database_logic import search_for_search_view
from src.services.pagination import Pagination
from src.services.view_items import open_item
from src.common.helper_functions import clear_screen
from src.services.add_items import add_main

class Search_flow:
    def __init__(self, userid: int, page_size: int, ):
        self.total_cred = 0
        self.pag = Pagination(total_cred=self.get_total_cred(), page_size=page_size)
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


    def get_total_cred(self):
        return self.total_cred

    def set_total_cred(self, new_total:int):
        self.total_cred = new_total

def search_database(to_search: str, userid: int, page_size: int, offset: int, ):
        data = search_for_search_view(
            to_search=to_search,
            database="CLI_Data.db",
            userid=userid,
            limit=page_size,
            offset=offset
        )

        return data

def search_total_result(to_search: str, userid: int):
    return len(search_for_search_view(
                to_search=to_search,
                database="CLI_Data.db",
                userid=userid,
                limit=None,
                offset=0
            ) 
    )

def search_main(total_cred: int, userid):
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
            for _ in db_data:
                print(_)
            import time
            time.sleep(5)
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
                    break

                case "b":
                    search.state_function(state=True)
                    break

                case "#":
                    open_item()
                    break

                case "a":
                    add_main()
                    continue

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