from fastapi import FastAPI, APIRouter

router = APIRouter(prefix="/credentials")


@router.get("/")
def hello():
    return "hello, het is gelukt"