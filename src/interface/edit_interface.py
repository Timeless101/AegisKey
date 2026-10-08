from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.common.helper_functions import get_password_with_complexity
from src.common.helper_functions import clear_screen

CONSOLE = Console()

def edit_success():
    clear_screen()
    CONSOLE.print("[bright_cyan]Succesfully edited!")

class Edit_prompt:
    def new_data_question(title, value):
        print(f"Current {title}: {value}")
        return Prompt.ask(f"New {title}")

    def new_password_question(title, value):
            print(f"Current {title}: {value}")
            return get_password_with_complexity()

    def confirmation():
        return Prompt.ask("is the information corred y/n default", choices=["yes", "y", "n", "no"], case_sensitive=False, show_choices=False, default="y")

def header():
    table = (":locked_with_key: [bold bright_cyan] Credential Details[/]")

    panel = Panel(
        table,
        width= 70
    )

    CONSOLE.print(panel)

def main_view(data: list):

    service, username, comment = data[0]

    table = Table.grid(expand=True)

    table.add_column()
    table.add_column()

    table.add_row("[1] Service", service)
    table.add_row("[2] Username", username)
    table.add_row("[3] Password", "********")
    table.add_row("[4] Comment", comment)
    table.add_row("", "")
    table.add_row("[B] Back", "")

    panel = Panel(
        table,
        width=70
    )

    CONSOLE.print(panel)

def handler(data):
    header()
    main_view(data=data)
    return Prompt.ask("\n[bright_cyan]Option[/]", choices=["b", "1", "2", "3", "4"], case_sensitive=False, show_choices=False).lower()