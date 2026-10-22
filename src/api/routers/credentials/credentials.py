from fastapi import APIRouter, HTTPException
from src.storage.storage_logic import searcher
from src.api.models.credential_models import CredentialModel

credential_router = APIRouter(prefix="/credentials")


@credential_router.get("/{cred_id}")
def get_item(cred_id: int):

    credential = searcher(
        column=("cred_id",),
        columns=["*",],
        data_to_search=cred_id,
        userid=1
    )

    if credential is None:
          raise HTTPException(status_code=404, detail="No credential found.")

    credential= credential[0]

    result = CredentialModel(
        cred_id=credential[0],
        userid=credential[1],
        service=credential[2],
        username=credential[3],
        password=credential[4],
        comment=credential[5],
        editeddate=credential[6]
        )
    
    return result