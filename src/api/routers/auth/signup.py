from fastapi import APIRouter, HTTPException, Response
from src.api.models.login_models import SignUpScheme


signup_router = APIRouter(prefix="/auth")


@signup_router.post("/signup")
def sign_up(signup: SignUpScheme):
    pass