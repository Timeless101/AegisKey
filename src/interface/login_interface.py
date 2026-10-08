from pystyle import Colors, Colorate
from getpass import getpass
from rich.console import Console
from src.common.helper_functions import get_password_with_complexity

CONSOLE = Console()

global MAIN_SCREEN_LOGO
MAIN_SCREEN_LOGO = r"""
___________________________________________________
|                       _     _  __               |         
|       /\             (_)   | |/ /               |
|      /  \   ___  __ _ _ ___| ' / ___ _   _      |
|     / /\ \ / _ \/ _` | / __|  < / _ \ | | |     |
|    / ____ \  __/ (_| | \__ \ . \  __/ |_| |     |
|   /_/    \_\___|\__, |_|___/_|\_\___|\__, |     |
|                   __/ |               __/ |     |
|                  |___/               |___/      |
|                                                 |
|_________________________________________________| 
        """
global MAIN_SCREEN_OPTIONS
MAIN_SCREEN_OPTIONS= """
    Options:
    1) Login
    2) Sign-Up
    3) About
    4) Exit
            """


#Main Screen functions
def main_menu():
    print(Colorate.Horizontal(Colors.rainbow, MAIN_SCREEN_LOGO), MAIN_SCREEN_OPTIONS)
    selection = input("Selection: ")
    return selection


#Login screen functions
def login_screen():
    login_screen = r"""
________________________________________________________________
|    _                 _                                       |
|   | |               (_)                                      |
|   | |     ___   __ _ _ _ __    ___  ___ _ __ ___  ___ _ __   |
|   | |    / _ \ / _` | | '_ \  / __|/ __| '__/ _ \/ _ \ '_ \  |
|   | |___| (_) | (_| | | | | | \__ \ (__| | |  __/  __/ | | | |
|   \_____/\___/ \__, |_|_| |_| |___/\___|_|  \___|\___|_| |_| |
|                 __/ |                                        |
|                |___/                                         |
|______________________________________________________________| 

                    """    
    print(Colorate.Horizontal(Colors.rainbow, login_screen))
    username = input("Email: ").strip().lower()
    password = getpass(echo_char="*")
    return username, password

#Register screen functions
def register_screen():
    register_screen = r"""
 ____________________________________________       
 |   _____ _                                |
 |  /  ___(_)                               |
 |  \ `--. _  __ _ _ __ ______ _   _ _ __   |
 |   `--. \ |/ _` | '_ \______| | | | '_ \  |
 |  /\__/ / | (_| | | | |     | |_| | |_) | |
 |  \____/|_|\__, |_| |_|      \__,_| .__/  |
 |            __/ |                 | |     |
 |           |___/                  |_|     |
 |__________________________________________|

"""
    print(Colorate.Horizontal(Colors.rainbow, register_screen), "\n")
    email = input("Email: ").strip().lower()

    password1 = get_password_with_complexity()
    password2 = get_password_with_complexity()
    
    return (email, password1, password2)


def about_screen():
    about_screen = r"""
___________________________________
|    ___  _                 _     |
|   / _ \| |               | |    |
|  / /_\ \ |__   ___  _   _| |_   |
|  |  _  | '_ \ / _ \| | | | __|  |
|  | | | | |_) | (_) | |_| | |_   |
|  \_| |_/_.__/ \___/ \__,_|\__|  |
|_________________________________|
"""
    print(Colorate.Horizontal(Colors.rainbow, about_screen))
    print("\nEncrypted Command Line Password Vault.")
    print("This is my first big project")
    print("\nBy: Diego")
    print("Created: 09/04/2026 dd/mm/yy")
    
    input("\n\nwaiting for input: ")
    return True

if __name__ == "__main__":
    pass