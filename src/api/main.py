"""
CLI password vault manager.


By: Diego Wuck
Created: 10/09/26 dd/mm/yy

fastapi dev src/api/main.py
http://127.0.0.1:8000/docs
http://127.0.0.1:8000
"""
from fastapi import FastAPI
from src.api.routers.credentials.credentials import credential_router
from src.api.routers.auth.login import login_router

app = FastAPI()

app.include_router(credential_router)
app.include_router(login_router)