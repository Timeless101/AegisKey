from fastapi import FastAPI, APIRouter
from src.storage.storage_logic import get_screen_data

router = APIRouter(prefix="/credentials")


@router.get("/")
def hello():
    cred = get_screen_data(userid= 1, page_size=50, offset=0)
    return cred