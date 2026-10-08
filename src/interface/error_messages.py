from rich.console import Console

CONSOLE = Console()

#Database errors:
def print_error_database():
    CONSOLE.print("\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]COULD_NOT_CREATE_DATABASE[/]", print_contact_support())

def print_insert_error():
    CONSOLE.print("\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]DATABASE_INSERT_ERROR:[/]\n Couldn't insert data into database.")

def print_error_data_insert():
    print("There was an problem with inserting your data into the database", print_contact_support())

def print_search_error():
    print("\nCould not search in database.", print_contact_support())

def print_database_data_row_search():
    print("\nCouldn'tsearch for the data in the database.", print_contact_support())

def print_data_length_error():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]Length of the list isn't the same as the length of the columns.[/]")

def print_email_exists():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]EMAIL_EXISTS_IN_DATABASE[/]")

def print_account_not_in_database():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]ACCOUNT_NOT_IN_DATABASE[/]")

def print_table_creation_error():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]CAN'T_CREATE_TABLE_WITH_THE_GIVEN_TABLENAME_OR_DATA[/]")

def print_startup_failed():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]DATABASE_STARTUP_FAILED[/]")

def print_incorrect_table_name():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]WRONG_TABLENAME_ENTERD[/]")

#Wrong type errors:
def print_wrong_data_type_dict():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]WRONG_DATATYPE_ENTERD_FOR_TABLE_CREATON\n NOTE: Datatype must be dictionary.[/]")

def print_wrong_data_type_list():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]WRONG_DATATYPE_ENTERD_FOR\nNOTE: Datatype must be a list.[/]")

def print_list_length_error():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]LIST_LENGTH_ERROR[/]\nNOTE: Column name and data insert list length isn't the same.")

#Invalid Input errors:
def print_invalid_email():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]EMAIL_DOESN'T_MATCH_THE_CRITERIA[/]")

def print_password_dont_match():
    CONSOLE.print("\n\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]PASSWORD_DON'T_MATCH.[/]\nPlease try again.")

def print_wrong_password():
    CONSOLE.print("\n\n\n:warning: [bold red]ERROR![/bold red]:warning:\n[red]WRONG_PASSWORD_ENTERD[/]")

def print_decryption_error():
    CONSOLE.print("\n\n:warning: [bold red]ERROR![/bold red]:warning:\n [red]PASSWORD_COULD_NOT_BE_DECRYPTED[/]\nThe credential data may be corrupted.")

def print_contact_support():
    return print("\nSomething went wrong, please contact support for further help.")

def print_internal_error():
    CONSOLE.print("\n\n:warning: [bold red]ERROR[/] :warning:\n [red]INTERNAL ERROR[/] \nSomething happened with the system.\n", print_contact_support())

def print_option_out_of_range():
    CONSOLE.print("\n\n:warning: [bold red] ERROR[/] :warning:\n [red]Option out of scope.\n Please select an id that is listed in the view or move to that page.")
