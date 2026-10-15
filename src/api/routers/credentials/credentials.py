from fastapi import FastAPI, APIRouter
from src.storage.storage_logic import searcher
from src.api.models.credential_models import CredentialModel

router = APIRouter(prefix="/credentials")


@router.get("/cred_id")
def get_item(cred_id: int):
    credential = searcher(
        column=("cred_id",),
        columns=["*",],
        data_to_search=cred_id,
        userid=1
    )[0]

    result = CredentialModel(
        cred_id=credential[0],
        userid=credential[1],
        service=credential[2],
        username=credential[3],
        password=credential[4],
        comment=credential[5],
        editeddate=credential[6]
        )
    
    if cred_id is None:
        return []
    
    return result