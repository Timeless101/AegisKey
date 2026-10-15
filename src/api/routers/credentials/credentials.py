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
    )

    if cred_id is None:
        return []
    return credential