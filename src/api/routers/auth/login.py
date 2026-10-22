from fastapi import APIRouter, HTTPException


login_router = APIRouter(prefix="/login")


@login_router.post("/{login_details}")
def check_login(login_details):
    print(login_details)
    return {"Detail": login_details}