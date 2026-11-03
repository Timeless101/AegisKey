from pydantic import BaseModel, ConfigDict


class LoginSchema(BaseModel):
    email: str
    password: str