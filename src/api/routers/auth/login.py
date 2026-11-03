from fastapi import APIRouter, HTTPException
from src.api.models.login_models import LoginSchema
from src.core.login_logic import api_login

login_router = APIRouter(prefix="/auth")


@login_router.post("/{login}")
def check_login(login_details: LoginSchema):
    if login_details == {}:
        raise HTTPException(status_code=204, detail="Connected, but no Content.")
    else:
        email, password = login_details
        _, email = email
        _, password = password
        details = api_login(input_email=email, input_password=password)
        return details