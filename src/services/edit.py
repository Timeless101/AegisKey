import src.interface.edit_interface as edit_interface
import src.storage.storage_logic as storage_logic
import src.crypto as crypto
from datetime import datetime

def update_password(column: str, cred_id: int, userid: int, encryption_key: bytes, current_data) -> None:
    while True:
        password_decrypted = crypto.password_decryption(
            password=current_data,
            encryption_key=encryption_key
            )
        
        new_data = edit_interface.Edit_prompt.new_data_question(column, password_decrypted)
        awnser = edit_interface.Edit_prompt.confirmation()

        if awnser.lower() not in ("y", "yes"):
            continue

        password_encrypted = crypto.password_encryption(
            encryption_key=encryption_key,
            password=new_data
        )

        storage_logic.update_database_item(
                            cred_id=cred_id,
                            userid=userid,
                            column=column,
                            new_data=password_encrypted,
                            new_date=datetime.now().replace(microsecond=0)
                            
        )
        edit_interface.edit_success()
        break

def update_data(column: str, cred_id: int, userid: int, encryption_key: bytes, is_password: bool) -> None:
    current_data = storage_logic.searcher(
                columns=[column,],
                column=("cred_id",),
                data_to_search=cred_id,
                userid=userid
            )[0][0]

    if is_password:
        update_password(
            current_data=current_data,
            column=column,
            cred_id=cred_id,
            userid=userid,
            encryption_key=encryption_key,
        )
        return None

    while True:
        new_data = edit_interface.Edit_prompt.new_data_question(column, current_data)
        awnser = edit_interface.Edit_prompt.confirmation()

        if awnser.lower() not in ("y", "yes"):
            continue
        edit_interface.edit_success()
        break

    storage_logic.update_database_item(
            cred_id=cred_id,
            userid=userid,
            column=column,
            new_data=new_data,
            new_date=datetime.now().replace(microsecond=0)
        )

def main(cred_id: int, userid: int, encryption_key: bytes) -> bool | None:

    data = storage_logic.searcher(
        columns=["Service", "Username", "comment"],
        column=("cred_id",),
        data_to_search=cred_id,
        userid=userid
    )
    
    if not choice_table(
        choice=edit_interface.handler(data=data),
        cred_id=cred_id,
        userid=userid,
        encryption_key=encryption_key
        ):
        return False

def choice_table(choice, cred_id: int, userid: int, encryption_key: bytes) -> None:
    match choice:

        case "1":
            update_data(
                column="Service",
                cred_id=cred_id,
                userid=userid,
                encryption_key=encryption_key,
                is_password=False
            )

        case "2":
            update_data(
                column="Username",
                cred_id=cred_id,
                userid=userid,
                encryption_key=encryption_key,
                is_password=False
            )

        case "3":
            update_data(
                column="Password",
                cred_id=cred_id,
                userid=userid,
                encryption_key=encryption_key,
                is_password=True
            )

        case "4":
            update_data(
                column="Comment",
                cred_id=cred_id,
                userid=userid,
                encryption_key=encryption_key,
                is_password=False
            )
        case "b":
            return False