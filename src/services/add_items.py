import src.common.errors as errors
from src.crypto import password_encryption
from src.storage.storage_logic import insert_data
from datetime import datetime
from src.common.helper_functions import clear_screen, confirmation_prompt
from src.interface.error_messages import print_internal_error
from src.interface.add_interface import add_items_screen_flow, add_success

def add_item(data: dict, key: bytes, userid: int) -> bool:
    current_time = datetime.now()

    service = data["Service"]
    username = data["Username"]
    password = data["Password"]
    comment = data["Comment"]

    encrypted_password = password_encryption(encryption_key=key, password=password)

    try:
        successs: bool = insert_data(
            table_name="vault_storage",
            column_name=[
                "UserID",
                "Service",
                "Username",
                "Password",
                "Comment",
                "CreationDate",
                "EditedDate"
            ],
            data=[
                userid,
                service,
                username,
                encrypted_password,
                comment,
                current_time.replace(microsecond=0),
                current_time.replace(microsecond=0)
            ]
        )

        if successs:
            return True
        
    except errors.WrongDataTypeList as wrong_type_error:  
        raise errors.WrongDataTypeList("Datatype isn't an list") from wrong_type_error
    
    except errors.DataLengthError as wrong_data_length_error:
        raise errors.DataLengthError("column_name and data do not contain the same number of items.") from wrong_data_length_error

    except errors.InsertError as insert_error:
        raise errors.InsertError("Could not insert data into database.") from insert_error

def add_main(userid: int, encryption_key: bytes) -> str:
    clear_screen()
    while True:
        result = add_items_screen_flow()

        match confirmation_prompt(text="\n[bright_cyan]Is al information correct?[/]"):
            case "y":
                if add_item(data=result, key=encryption_key, userid=userid):
                    add_success()
                    break
                else:
                    print_internal_error()
                    break

            case "n":
               continue
    return "a"