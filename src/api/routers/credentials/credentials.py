from fastapi import FastAPI, APIRouter
from src.storage.storage_logic import get_screen_data
from src.api.models.credential_models import CredentialModel

router = APIRouter(prefix="/credentials")


@router.get("/")
def hello():
    cred = get_screen_data(userid= 1, page_size=50, offset=0)

    if cred is None: return []

    result = []
    for row in cred:
        credential = CredentialModel(
            screen_number_id=row[0],
            cred_id=row[1],
            service=row[2],
            username=row[3],
            comment=row[4],
            EditedDate=row[5]
        )
        result.append(credential)
    return result