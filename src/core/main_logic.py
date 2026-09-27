import src.core.login_logic as login_logic
import src.core.vault_logic as vault_logic

def program_flow():
    while True:
        data: tuple | False = login_logic.option_selection(login_logic.main_menu())
        if data is False:
            continue
        
        email, userid, encryption_key = data
        while True:
            result: str | None = vault_logic.start_flow(email=email, userid=userid, encryption_key= encryption_key)
            match result:
                case "q":
                    encryption_key = None
                    email = None
                    userid = None
                    break

                case "a":
                    continue

                case "v":
                    continue

                case "s":
                    continue


if __name__ == "__main__":
    pass