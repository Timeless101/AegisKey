from fastapi import APIRouter, HTTPException, Response
from src.api.models.login_models import LoginSchema
from src.core.login_logic import api_login
from src.common.errors import AccountError, EmailMismatchError, InvalidPasswordError

login_router = APIRouter(prefix="/auth")


@login_router.post("/login")
def check_login(login_details: LoginSchema, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        email, userid, _encryption_key = api_login(
            input_email=login_details.email,
            input_password=login_details.password,
        )
    except (AccountError, EmailMismatchError, InvalidPasswordError):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
            headers={"Cache-Control": "no-store"},
        ) from None

    return {
        "verified": True,
        "session_created": False,
        "user": {"id": str(userid), "email": email},
    }
