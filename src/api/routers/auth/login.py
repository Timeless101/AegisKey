from fastapi import APIRouter, HTTPException
from src.api.models.login_models import LoginSchema


login_router = APIRouter(prefix="/login")


@login_router.post("/")
def check_login(login_details: LoginSchema):
    if login_details == {}:
        raise HTTPException(status_code=204, detail="Connected, but no Content.")
    else:
        print(login_details)
