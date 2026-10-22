"""
CLI password vault manager.


By: Diego Wuck
Created: 10/09/26 dd/mm/yy

fastapi dev src/api/main.py
http://127.0.0.1:8000/docs
http://127.0.0.1:8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.credentials.credentials import credential_router
from src.api.routers.auth.login import login_router

app = FastAPI()

#This is a list of the allowed location to fetsh data.
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(credential_router)
app.include_router(login_router)


@app.get("/hello")
async def hello():
    return {"Message": "Hello World!"}