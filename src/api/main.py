"""
CLI password vault manager.


By: Diego Wuck
Created: 10/09/26 dd/mm/yy

fastapi dev src/api/main.py
http://127.0.0.1:8000/docs
http://127.0.0.1:8000
"""
from fastapi import FastAPI, APIRouter
from src.api.routers.credentials.credentials import router

app = FastAPI()

app.include_router(router)