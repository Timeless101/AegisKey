from pydantic import BaseModel


class CredentialModel(BaseModel):
    cred_id: int
    userid: int
    service: str
    username: str
    password: bytes
    comment: str
    editeddate: str