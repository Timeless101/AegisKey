from pydantic import BaseModel


class CredentialModel(BaseModel):
    screen_number_id: int
    cred_id: int
    service: str
    username: str
    comment: str
    EditedDate: str