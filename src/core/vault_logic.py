import src.storage.storage_logic as storage_logic
import src.interface.error_messages as error_messages
import src.interface.vault_interface as vault_interface
import src.common.errors as errors
from src.common.helper_functions import clear_screen, exit_program
from src.services.add_items import add_main
from src.services.view_items import menu_flow
from src.services.search import search_main

#Helper functions.
def get_five_rows_out_database(userid: int) -> list | None:
    try:
        data: list | None = storage_logic.search_limited_amount_of_items_in_database(
            userid=userid,
            limit=5
        )

        if data is None:
            return None

        if len(data) > 5:
            raise ValueError("Length of the data is not 5")
        
        return data
    
    except errors.TableError:
        error_messages.print_incorrect_table_name()
        return False

def option_handler(choice: str, userid: int, encryption_key: bytes, total_cred: int) -> str | None:
    if not choice in ["a", "v", "s", "d", "e", "q"]:
        return None
    
    dispatch_table = {
        "a": lambda: add_main(userid, encryption_key),
        "v": lambda: menu_flow(userid, total_cred, encryption_key),
        "s": lambda: search_main(total_cred=total_cred, userid=userid, encryption_key=encryption_key),
        "q": option_q
    }
    func = dispatch_table.get(choice)
    return func()

def prepare_vault_screen_data(userid: int):

    data = get_five_rows_out_database(userid=userid)
    total_cred: int | None = storage_logic.get_all_items_in_database(userid=userid)

    showed_items = 0
    if total_cred is None:
        total_cred = 0

    if data is None:
        showed_items = 0
    else:
        showed_items = len(data)

    return data, total_cred, showed_items

#Main flow
def start_flow(email: str, userid: int, encryption_key: bytes):
    try:
        clear_screen()
        data, total_cred, showed_items = prepare_vault_screen_data(userid=userid)

        success = option_handler(
            choice=vault_interface.vault_screen(
                    email=email,
                    total_cred=total_cred,
                    rows=data,
                    showed_items=showed_items),
            userid=userid,
            encryption_key=encryption_key,
            total_cred=total_cred
            )
        
        if success is None:
            error_messages.print_internal_error()
            #Make a log entry that logs that there was something wrong while passing the choice
            #no selection from:"A", "V", "S", "E", "D", "Q
        return success
    
    except (KeyboardInterrupt, EOFError):
        exit_program()

def option_s():
    print("s")


def option_q():
    return "q"

if __name__ == "__main__":
    pass