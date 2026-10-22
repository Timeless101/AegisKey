from fastapi import APIRouter, HTTPException


login_router = APIRouter(prefix="/login")


@login_router.post("")
def check_login():
    return {"Meggase": "success"}