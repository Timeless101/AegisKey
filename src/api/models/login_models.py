from pydantic import BaseModel


class LoginSchema(BaseModel):
    email: str
    password: str

class SignUpScheme(BaseModel):
    name: str
    email: str
    password: str
    password2: str