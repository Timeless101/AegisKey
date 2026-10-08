import src.common.errors as errors
import src.storage.storage_logic as storage_logic
import src.interface.login_interface as login_interface
import src.validator as validator
import src.crypto as crypto
import src.interface.error_messages as error_messages
from time import sleep
from src.common.helper_functions import clear_screen, exit_program

#Constances
DATABASE_NAME: str = "CLI_Data.db"
LOGIN_TABLE: str = "login_information"


#Helper functions
def validate_password(input_password: str, database_password: bytes, salt) -> bool:
    if not crypto.verify_password(input_password=input_password, database_password=database_password, salt=salt):
        return False
    return True

def get_encryption_key(input_password: bytes, encryption_salt: bytes) -> bytes:
    return crypto.login_key_calculation(input_password=input_password, encryption_salt=encryption_salt)

#Gets the UserID out of the database.
def get_userid(email) -> int:
    row: list | None  = storage_logic.data_row_search(email=email, table_column="Email", table_name="login_information")
    if row is None:
        raise errors.AccountError("Account doesn't exists.")
    
    userid, _, _, salt, _ = row
    return int(userid)

#Database search email return str email.
def email_search(email) -> None | False | str :
    try:

        data: list | None = storage_logic.search_data(
            table_name="login_information",
            table_column="Email",
            data_to_be_searched=email
        )

        if data is None:
            return None

        first_data = data[0]
        second_data = first_data[1]
        return str(second_data)
    
    except errors.TableError:
        error_messages.print_search_error()
        return False

#Main menu flow.
def initialize_database_bystartup() -> bool:
    try:
        if not storage_logic.create_database(database_name=DATABASE_NAME):
            return False
        
        table1: bool = storage_logic.table_creator(
            table_name=LOGIN_TABLE,
            columns={
            "Id": "INTEGER UNIQUE PRIMARY KEY",
            "Email": "TEXT UNIQUE NOT NULL",
            "Password": "TEXT NOT NULL",
            "Salt": "TEXT NOT NULL",
            "EncryptionSalt": "TEXT NOT NULL"},
            )

        
        table2: bool = storage_logic.table_creator(
            table_name="vault_storage",
            columns={
                "cred_id": "INTEGER PRIMARY KEY",
                "UserID": "INTEGER NOT NULL",
                "Service": "TEXT",
                "Username": "TEXT",
                "Password": "TEXT NOT NULL",
                "Comment": "TEXT",
                "CreationDate": "DATE NOT NULL",
                "EditedDate": "DATE NOT NULL", 
            },
        )

        if table1 and table2:
            return True
        
        return False
        
    except errors.WrongDataTypeDict:
        return False
    
    except errors.TableError:
        return False


def main_menu() -> str:
    if not initialize_database_bystartup():   
        error_messages.print_startup_failed()
        input("Press any key to quit: ")
        exit_program()
    
    clear_screen()
    
    try:
        while True:
            selection: str = login_interface.main_menu()
            if selection in ["1", "2", "3","4"]:
                break
            else:
                clear_screen()
                print("Please select an option from the list.")
                sleep(1.5)
                clear_screen()
                continue
        return selection
    except (KeyboardInterrupt, EOFError):
        exit_program()

#menu selection.
def option_selection(option: str) -> tuple:
    dispatch_table: dict = {
        "1": login_flow,
        "2": sign_up_flow,
        "3": about,
        "4": exit_program,
    }
    func = dispatch_table.get(option)
    return func()

#Login flow.
def login_flow() -> tuple[str, int, bytes]:
    clear_screen()
    try:
        while True:
            try:
                input_email, input_password = login_interface.login_screen()
                encryption_key: bytes = sign_in_function(email=input_email, password=input_password)

                if not isinstance(encryption_key, bytes):
                    error_messages.print_internal_error()
                    sleep(5)
                    exit_program()
                    
                return input_email, get_userid(input_email), encryption_key

            except errors.EmailMismatchError:
                error_messages.print_invalid_email()
                sleep(1.5)
                clear_screen()
                continue

            except errors.AccountError:
                error_messages.print_account_not_in_database()
                sleep(1.5)
                clear_screen()
                continue

            except errors.InvalidPasswordError:
                error_messages.print_wrong_password()
                sleep(1.5)
                clear_screen()
                continue

    except (KeyboardInterrupt, EOFError):
        exit_program()


def sign_in_function(email: str, password: str) -> bytes:

    if not validator.email_checker(email):
        raise errors.EmailMismatchError("Email doesn't match the criteria.")
    
    row = storage_logic.data_row_search(email=email, table_column="Email", table_name="login_information")
    
    if row is None:
        raise errors.AccountError("Account doesn't exists.")
    
    _, _, database_password, salt, encryption_salt = row

    if not validate_password(input_password=password, database_password=database_password, salt=salt):
        raise errors.InvalidPasswordError("Wrong password has been enterd.")

    return get_encryption_key(input_password=password, encryption_salt=encryption_salt)


#Sign up
def sign_up_flow() -> tuple[str, int, bytes]:
    clear_screen()
    try:
        while True:
            try:
                email, password1, hashed_password, salt, encryption_salt = get_input_and_validate_it()

                successs: bool = storage_logic.insert_data(
                    table_name= "login_information",
                    column_name= ["Email", "Password", "Salt", "EncryptionSalt"],
                    data= [email, hashed_password, salt, encryption_salt])
                
                if not successs:
                    error_messages.print_error_data_insert()
                    clear_screen()
                    continue
                    #Print path to log file. and wait for input, after go to menu.
                
                encryption_key: bytes = get_encryption_key(input_password=password1, encryption_salt=encryption_salt)

                if not isinstance(encryption_key, bytes):
                    error_messages.print_internal_error()
                    sleep(5)
                    exit_program()

                return email , get_userid(email), encryption_key
                
            except errors.EmailMismatchError:
                    error_messages.print_invalid_email()
                    sleep(3)
                    clear_screen()
                    continue
            
            except errors.PasswordMismatchError:
                    error_messages.print_password_dont_match()
                    sleep(3)
                    clear_screen()
                    continue
            
            except errors.DuplicationError:
                    error_messages.print_email_exists()
                    sleep(3)
                    clear_screen()
                    continue

            except errors.DataLengthError:
                error_messages.print_data_length_error()
                sleep(5)
                exit_program()
            
            except errors.WrongDataTypeDict:
                error_messages.print_wrong_data_type_dict()
                sleep(3)
                #Make log file
                exit_program()

            except errors.TableError:
                error_messages.print_incorrect_table_name()
                sleep(3)
                #Make log file
                exit_program()

    except (KeyboardInterrupt, EOFError):
        exit_program()

def get_input_and_validate_it() -> tuple[str, str, bytes, bytes, bytes]:

    email, password1, password2 = login_interface.register_screen()

    if not validator.email_checker(email):
        raise errors.EmailMismatchError("Email doesn't match the criteria.")
    
    if not validator.password_match_checker(password1, password2):
        raise errors.PasswordMismatchError("Passwords don't match")
    
    if not validator.email_is_available(new_email=email, database_email=email_search(email)):
        raise errors.DuplicationError("Email already exists in database.")

    hashed_password, password_salt, encryption_salt = crypto.hash_password(password1)

    
    return email, password1, hashed_password, password_salt, encryption_salt


#BAout flow
def about() -> bool:
    clear_screen()
    if login_interface.about_screen():
        return False
    

if __name__ == "__main__":
    ...