from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from getpass import getpass
from src.common.helper_functions import clear_screen

CONSOLE = Console()

def add_success():
    clear_screen()
    CONSOLE.print("[bright_cyan]Succes![\]")

def add_items_screen_flow():
    service, username, password, comment = add_items_screen()
    return {"Service": service, "Username": username, "Password": password, "Comment": comment}

def add_item_screen(service, username, password, comment):

    clear_screen()

    asterisk = "*" * len(password)
    table = Table.grid(padding=(0, 1), expand=False)

    table.add_column(justify="left",)
    table.add_column()

    table.add_row("[bright_cyan]Service: [/]", service)
    table.add_row("[bright_cyan]Username: [/]", username)
    table.add_row("[bright_cyan]Password: [/]", asterisk)
    table.add_row("[bright_cyan]Comment: [/]", comment)

    panel = Panel(
            table,
            width=70,
            padding=(0, 1))


    CONSOLE.print(panel)

def question(name):
    return CONSOLE.input(f"[cyan]\n{name}: [/]")


def add_items_screen() -> tuple[str, str, str, str]:

    add_item_screen("", "", "", "")
    service: str = question("Service")
    add_item_screen(service, "", "", "")
    username: str = question("Username")
    add_item_screen(service, username, "","")
    password: str = getpass(echo_char="*")
    add_item_screen(service, username, password, "")
    comment: str = question("Comment")
    add_item_screen(service, username, password, comment)

    return service, username, password, comment