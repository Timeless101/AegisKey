from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from time import sleep

CONSOLE = Console()

def items_none() -> str:

    empty_vault = ":information: [bold yellow]No recent passwords added[/] :information:"
    panel1 = Panel(
        empty_vault,
        width=70
    )
    CONSOLE.print(panel1,"\n")

    table = Table.grid(expand= True)
        
    table.add_column(justify="left", no_wrap=True)
    table.add_column(justify="center", no_wrap=True)
    table.add_column(justify="right", no_wrap=True)

    table.add_row("[bright_green][A] Add credential[/]")
    table.add_row("", "", "")
    table.add_row("[yellow][B] Back[/]")
    panel = Panel(
        table,
        width=70,
        padding= (0, 1)
    )
    
    CONSOLE.print(panel)

    return input()

def main_header(total_credentials: int) -> None:
    table = Table.grid(expand= True)

    table.add_column(justify="left", no_wrap=True)
    table.add_column(justify="right", no_wrap=True)

    table.add_row(":locked_with_key: [bold bright_cyan] All Credentials[/]", ":white_heavy_check_mark: [bright_green]Vault Unlocked[/]")
    table.add_row("", "")
    table.add_row("Browse saved credentials", f"{total_credentials} [bold grey53]Credentials[/]")

    panel = Panel(
        table,
        width=70,
        padding= (0, 1)
    )

    CONSOLE.print(panel)
    print("\n")

def main_view(data: list):

    table = Table()

    table.add_column("#")
    table.add_column("[bold bright_cyan]Service[/]")
    table.add_column("[bold bright_cyan]Username[/]")
    table.add_column("[bold bright_cyan]Password[/]")
    table.add_column("[bold bright_cyan]Comment[/]")
    table.add_column("[bold bright_cyan]Edited[/]")

    asterisk = "*" * 8

    for item in data:
        screen_number_id, _, service, username, comment, editedDate = item
        
        table.add_row(str(screen_number_id), service, username, asterisk, comment, editedDate)

    CONSOLE.print(table)

def options(total_cred: int, current_page:int, max_page: int, showing_items_end: int, showing_items_start: int) -> str:
    table = Table.grid(expand= True)
    
    table.add_column(justify="left", no_wrap=True)
    table.add_column(justify="center", no_wrap=True)
    table.add_column(justify="right", no_wrap=True)

    table.add_row("[bright_blue][P] Previous[/]", "[yellow][B] Back[/]", "[bright_blue][N] Next[/]")
    table.add_row("", "")
    table.add_row(f"[grey53]Showing {showing_items_start}-{showing_items_end} of {str(total_cred)}][/]", f"[cyan] Page {current_page}/{max_page}[/]", r"[cyan]\[#] Open item[/]")
    panel = Panel(
        table,
        width=70,
        padding= (0, 1)
    )

    CONSOLE.print(panel)

    return Prompt.ask("\n[bright_cyan]Option[/]", choices=["P", "B", "N", "#"], case_sensitive=False, show_choices=False)

def footer():
    table = Table.grid(expand= True)
        
    table.add_column(justify="center", no_wrap=True)

    table.add_row("Search by service, username or comment.")
    table.add_row("Press enter to go back.")
    panel = Panel(
        table,
        width=70,
        padding= (0, 1)
    )

    CONSOLE.print(panel)

    return input("Search: ")

def screen_handler_with_options(data: list, total_credentials: int, current_page: int, max_page: int, showing_items_end: int, showing_items_start: int) -> str:

    if data is None:
        main_header(total_credentials=total_credentials)
        option_no_items = items_none().lower()
        return option_no_items

    main_header(total_credentials=total_credentials)
    CONSOLE.print("\n:lock: [bold bright_cyan]CREDENTIALS [/]\n")
    main_view(data=data)
    print("\n")
    
    option: str =  options(
            total_cred=total_credentials,
            current_page=current_page,
            max_page=max_page,
            showing_items_end=showing_items_end,
            showing_items_start=showing_items_start
            ).lower()

    return option

def screen_handler_search(data: list, total_credentials: int) -> str:

    if data is None:
        main_header(total_credentials=total_credentials)
        option_no_items = items_none().lower()
        return option_no_items

    main_header(total_credentials=total_credentials)
    CONSOLE.print("\n:lock: [bold bright_cyan]CREDENTIALS [/]\n")
    main_view(data=data)
    print("\n")

    return footer().lower()