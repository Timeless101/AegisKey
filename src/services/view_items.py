import pyperclip
import src.storage.database_logic as database_logic
import src.storage.storage_logic as storage_logic
import src.interface.error_messages as error_messages
import src.interface.view_interface as view_interface
import src.common.errors as errors
from src.services import edit
from src.crypto import password_decryption
from src.common.helper_functions import clear_screen, print_copy, confirmation_prompt
from src.services.add_items import add_main
from src.storage.storage_logic import searcher
from src.services.pagination import Pagination
from time import sleep

def data_handler(data: list[tuple], choice: int, userid: int) -> tuple:
    cred_id = get_cred_id(data=data, choice=choice)

    data = storage_logic.searcher(
        columns=["service", "username", "comment", "creationdate", "editeddate"],
        column=("cred_id",),
        data_to_search=cred_id,
        userid=userid
    )

    if data is None:
        return None

    return data[0], cred_id # returns .

def get_cred_id(data: list[tuple], choice: int) -> int:
    for item in data:
        if item[0] == choice:
            return item[1]
        continue

def view_password(encryption_key: bytes, cred_id: int, userid: int) -> str:

    password = storage_logic.searcher(
        columns=["Password",],
        column=("cred_id",),
        data_to_search=cred_id,
        userid=userid
    )

    return password_decryption(encryption_key=encryption_key, password=password[0][0])

def show_screen_with_data_get_option(data: list, total_cred: int, current_page:int , total_pages: int, showing_items_end: int, showing_items_start: int):
    option: str = view_interface.screen_handler(
                data=data,
                total_credentials=total_cred,
                current_page=current_page,
                max_page=total_pages,
                showing_items_end=showing_items_end,
                showing_items_start=showing_items_start,
                )
    return option

#Flow functions
def menu_flow(userid: int, total_cred: int, encryption_key: bytes) -> str:
    pag = Pagination(total_cred=total_cred, page_size= 5)
    while True:
        clear_screen()
        data = storage_logic.get_screen_data(userid=userid, page_size=pag.page_size, offset=pag.offset)

        option = show_screen_with_data_get_option(
            data=data,
            total_cred=pag.total_cred,
            current_page=pag.current_page,
            total_pages=pag.total_pages,
            showing_items_start=pag.showing_items_start,
            showing_items_end=pag.showing_items_end
        )

        match option:
            case "b":
                return "v"

            case "n":
                pag.next_page()
                continue

            case "p":
                pag.previous_page()
                continue

            case "#":
                if not open_item(data=data, encryption_key=encryption_key, userid=userid):
                    continue

            case "a":
                add_main(userid=userid, encryption_key=encryption_key)

def password_item_flow(str_choice: str, encryption_key: bytes, userid: int, cred_id: int) -> bool | None:
    data = searcher(
        columns=["Service", "Username", "Comment", "CreationDate", "EditedDate"],
        column=("cred_id",),
        data_to_search=cred_id,
        userid=userid
    )

    match str_choice:
        case "r":
            if confirmation_prompt(text="\n[bright_cyan]Are you sure you want to reveal the password?[/]") == "y":
                clear_screen()
                password = view_password(encryption_key=encryption_key, cred_id=cred_id, userid=userid)
                while True:
                    clear_screen()
                    if view_interface.view_password_plain_handeler(data=data, password=password) == "c":
                        pyperclip.copy(password)
                        print_copy()
                    else:
                        break
                    
        case "e":
            edit.main(cred_id=cred_id, userid=userid, encryption_key=encryption_key)

        case "d":
            if confirmation_prompt(text="\n:warning:[bright_cyan] Are you sure you want to delete this item?[/]:warning:") == "y":
                delete_item(cred_id=cred_id, userid=userid)
                clear_screen()
                view_interface.delete_success()
            pass

def select_item_flow(data: list, userid: int) -> str:

    id_choice: int = view_interface.ask_item_id()
    clear_screen()

    view_item_data = data_handler(data=data, choice=id_choice, userid=userid)

    if view_item_data is None:
        error_messages.print_option_out_of_range()
        sleep(2.5)
        return False

    view_item_data, cred_id = view_item_data
    return view_interface.view_password_handler(data=view_item_data), id_choice, cred_id

#Item Operations
def open_item(data: list, encryption_key: bytes, userid: int) -> bool:
    result = select_item_flow(data=data, userid=userid)
    if result is False:
        return False

    str_choice, _, cred_id = result

    if str_choice is None:
        return False
    password_item_flow(str_choice=str_choice, encryption_key=encryption_key, userid=userid, cred_id=cred_id)


def delete_item(cred_id: int, userid: int) -> bool:
    try:
        if database_logic.delete_item(
        database="CLI_Data.db",
        table="vault_storage",
        cred_id=cred_id,
        userid=userid
        ):
            return True
    except errors.WrongSQLStatement:
        error_messages.print_internal_error()
        return False
    except errors.DatabaseError:
        error_messages.print_internal_error()
        return False
    except errors.UnexpectedError:
        error_messages.print_contact_support()
        return False