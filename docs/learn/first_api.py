from fastapi import FastAPI, HTTPException

app = FastAPI()

demo_credentials = {
    1: {"service": "GitHub", "username": "Diego"},
    2: {"service": "Microsoft", "username": "Test"}
}

@app.get("/")
async def root():
    return{"message": "Hello World"}

@app.get("/about")
def about():
    return {
  "name": "AegisKey",
  "phase": 2
}

@app.get("/credentials/{cred_id}")
def credential(cred_id: int):
    if cred_id in demo_credentials:
        return demo_credentials[cred_id]
    else:
        raise HTTPException(status_code=404, detail="Credential not found")